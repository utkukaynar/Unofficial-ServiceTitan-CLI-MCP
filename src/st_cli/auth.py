"""OAuth 2.0 Client Credentials auth with two-tier caching."""

from __future__ import annotations

import json
import time
from pathlib import Path

import httpx

from st_cli.config import Settings
from st_cli.exceptions import AuthError

_CACHE_DIR = Path.home() / ".st_cli"
_CACHE_FILE = _CACHE_DIR / "token_cache.json"
_EARLY_EXPIRY_BUFFER = 60  # seconds
_REFRESH_ATTEMPTS = 4
_REFRESH_BACKOFF_BASE = 2.0  # seconds; sleeps 2, 4, 8 between attempts


class TokenManager:
    """Manages OAuth tokens with in-memory + file-based caching."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._token: str | None = None
        self._expires_at: float = 0.0
        self._load_from_file()

    def get_token(self) -> str:
        """Return a valid token, refreshing if needed."""
        if self._is_valid():
            assert self._token is not None
            return self._token
        return self._refresh()

    def force_refresh(self) -> str:
        """Force a token refresh (used on 401 retry)."""
        return self._refresh()

    def _is_valid(self) -> bool:
        return self._token is not None and time.time() < (self._expires_at - _EARLY_EXPIRY_BUFFER)

    def _refresh(self) -> str:
        resp = self._post_token_request()
        data = resp.json()
        self._token = data["access_token"]
        self._expires_at = time.time() + data["expires_in"]
        self._save_to_file()
        return self._token  # type: ignore[return-value]

    def _post_token_request(self) -> httpx.Response:
        """POST the token request, retrying transient failures with backoff.

        Transport errors (DNS, connect, timeout) and 5xx responses are retried
        so a network blip can't kill an unattended long-running drain; 4xx is
        definitive (bad credentials/config) and fails immediately.
        """
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = httpx.post(
                    self._settings.auth_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self._settings.client_id,
                        "client_secret": self._settings.client_secret,
                    },
                )
                resp.raise_for_status()
                return resp
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code < 500 or attempt >= _REFRESH_ATTEMPTS:
                    raise AuthError(
                        f"Token request failed ({exc.response.status_code}): "
                        f"{exc.response.text}"
                    ) from exc
            except httpx.RequestError as exc:
                if attempt >= _REFRESH_ATTEMPTS:
                    raise AuthError(
                        f"Token request failed after {attempt} attempts: {exc}"
                    ) from exc
            time.sleep(_REFRESH_BACKOFF_BASE * 2 ** (attempt - 1))

    def _load_from_file(self) -> None:
        if not _CACHE_FILE.exists():
            return
        try:
            raw = json.loads(_CACHE_FILE.read_text())
            cache_key = self._cache_key()
            entry = raw.get(cache_key)
            if entry and time.time() < (entry["expires_at"] - _EARLY_EXPIRY_BUFFER):
                self._token = entry["token"]
                self._expires_at = entry["expires_at"]
        except (json.JSONDecodeError, KeyError):
            pass

    def _save_to_file(self) -> None:
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        raw: dict = {}
        if _CACHE_FILE.exists():
            try:
                raw = json.loads(_CACHE_FILE.read_text())
            except json.JSONDecodeError:
                pass
        raw[self._cache_key()] = {
            "token": self._token,
            "expires_at": self._expires_at,
        }
        _CACHE_FILE.write_text(json.dumps(raw))

    def _cache_key(self) -> str:
        return f"{self._settings.client_id}:{self._settings.tenant_id}"

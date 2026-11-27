"""Base HTTP client wrapping httpx with auth, retry, and error mapping."""

from __future__ import annotations

import time
from typing import Any
from urllib.parse import quote

import httpx

from st_cli.auth import TokenManager
from st_cli.config import Settings
from st_cli.exceptions import APIError, NotFoundError, RateLimitError, UsageError


def path_segment(value: Any) -> str:
    """Encode a caller-supplied id as exactly one URL path segment.

    Ids reach the URL from CLI args and from MCP tool calls (i.e. from a model).
    Percent-encoding ``/`` and rejecting ``.``/``..`` keeps a value like
    ``../../settings/...`` from steering the request to a different endpoint.
    """
    text = str(value)
    if text in ("", ".", ".."):
        raise UsageError(f"invalid path parameter: {text!r}")
    return quote(text, safe="")


_MAX_RETRIES = 3
_BACKOFF_BASE = 1.0  # seconds


class ServiceTitanClient:
    """HTTP client for the ServiceTitan REST API.

    Most endpoints are ``v2``; a few newer ones (CRM leads create, telecom calls
    feed, opt-outs) exist only under ``v3``, so every method takes ``version``.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._token_manager = TokenManager(settings)
        self._http = httpx.Client(base_url=settings.api_base, timeout=30.0)

    def close(self) -> None:
        self._http.close()

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token_manager.get_token()}",
            "ST-App-Key": self._settings.app_key,
        }

    def _url(self, module: str, resource: str, version: str = "v2") -> str:
        return f"/{module}/{version}/tenant/{self._settings.tenant_id}/{resource}"

    def get(
        self,
        module: str,
        resource: str,
        params: dict[str, Any] | None = None,
        version: str = "v2",
    ) -> Any:
        return self._request("GET", module, resource, params=params, version=version)

    def post(
        self,
        module: str,
        resource: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        version: str = "v2",
    ) -> Any:
        return self._request(
            "POST", module, resource, params=params, json_body=json_body, version=version
        )

    def patch(
        self,
        module: str,
        resource: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        version: str = "v2",
    ) -> Any:
        return self._request(
            "PATCH", module, resource, params=params, json_body=json_body, version=version
        )

    def put(
        self,
        module: str,
        resource: str,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        version: str = "v2",
    ) -> Any:
        return self._request(
            "PUT", module, resource, params=params, json_body=json_body, version=version
        )

    def delete(
        self,
        module: str,
        resource: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        version: str = "v2",
    ) -> Any:
        return self._request(
            "DELETE", module, resource, params=params, json_body=json_body, version=version
        )

    def _request(
        self,
        method: str,
        module: str,
        resource: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        version: str = "v2",
    ) -> Any:
        url = self._url(module, resource, version)
        retries = 0
        refreshed = False

        while True:
            resp = self._http.request(
                method, url, headers=self._headers(), params=params, json=json_body
            )

            if resp.status_code == 401 and not refreshed:
                self._token_manager.force_refresh()
                refreshed = True
                continue

            if resp.status_code == 429 and retries < _MAX_RETRIES:
                retries += 1
                wait = _BACKOFF_BASE * (2 ** (retries - 1))
                time.sleep(wait)
                continue

            break

        if resp.status_code == 404:
            raise NotFoundError(resp.text)
        if resp.status_code == 429:
            raise RateLimitError(resp.text)
        if resp.status_code >= 400:
            raise APIError(resp.status_code, resp.text)

        if resp.status_code == 204:
            return None
        return resp.json()

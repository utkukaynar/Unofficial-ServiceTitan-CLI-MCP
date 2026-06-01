"""Tests for auth.py."""

from __future__ import annotations

import json
import time
from unittest.mock import patch

import httpx
import pytest
import respx

from st_cli.auth import TokenManager
from st_cli.config import Environment, Settings
from st_cli.exceptions import AuthError


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        client_id="test-id",
        client_secret="test-secret",
        app_key="test-key",
        tenant_id=12345,
        environment=Environment.PRODUCTION,
    )


@pytest.fixture(autouse=True)
def clean_cache(tmp_path):
    """Redirect cache to tmp_path for isolation."""
    cache_dir = tmp_path / ".st_cli"
    cache_file = cache_dir / "token_cache.json"
    with patch("st_cli.auth._CACHE_DIR", cache_dir), patch("st_cli.auth._CACHE_FILE", cache_file):
        yield cache_dir, cache_file


class TestTokenManager:
    @respx.mock
    def test_fetches_new_token(self, settings, clean_cache):
        route = respx.post(settings.auth_url).mock(
            return_value=httpx.Response(200, json={"access_token": "tok123", "expires_in": 3600})
        )
        tm = TokenManager(settings)
        token = tm.get_token()
        assert token == "tok123"
        assert route.called

    @respx.mock
    def test_caches_in_memory(self, settings, clean_cache):
        route = respx.post(settings.auth_url).mock(
            return_value=httpx.Response(200, json={"access_token": "tok", "expires_in": 3600})
        )
        tm = TokenManager(settings)
        tm.get_token()
        tm.get_token()
        assert route.call_count == 1

    @respx.mock
    def test_force_refresh_fetches_new_token(self, settings, clean_cache):
        route = respx.post(settings.auth_url).mock(
            return_value=httpx.Response(200, json={"access_token": "new", "expires_in": 3600})
        )
        tm = TokenManager(settings)
        tm.get_token()
        token = tm.force_refresh()
        assert token == "new"
        assert route.call_count == 2

    @respx.mock
    def test_saves_to_file_cache(self, settings, clean_cache):
        _, cache_file = clean_cache
        respx.post(settings.auth_url).mock(
            return_value=httpx.Response(200, json={"access_token": "file-tok", "expires_in": 3600})
        )
        tm = TokenManager(settings)
        tm.get_token()
        assert cache_file.exists()
        raw = json.loads(cache_file.read_text())
        key = f"{settings.client_id}:{settings.tenant_id}"
        assert raw[key]["token"] == "file-tok"

    @respx.mock
    def test_loads_from_file_cache(self, settings, clean_cache):
        cache_dir, cache_file = clean_cache
        key = f"{settings.client_id}:{settings.tenant_id}"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(
            json.dumps({key: {"token": "cached", "expires_at": time.time() + 3600}})
        )
        route = respx.post(settings.auth_url)
        tm = TokenManager(settings)
        token = tm.get_token()
        assert token == "cached"
        assert not route.called

    @respx.mock
    def test_expired_file_cache_triggers_refresh(self, settings, clean_cache):
        cache_dir, cache_file = clean_cache
        key = f"{settings.client_id}:{settings.tenant_id}"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps({key: {"token": "old", "expires_at": time.time() - 100}}))
        respx.post(settings.auth_url).mock(
            return_value=httpx.Response(200, json={"access_token": "fresh", "expires_in": 3600})
        )
        tm = TokenManager(settings)
        token = tm.get_token()
        assert token == "fresh"

    @respx.mock
    def test_auth_error_on_http_failure(self, settings, clean_cache):
        respx.post(settings.auth_url).mock(return_value=httpx.Response(401, text="bad creds"))
        tm = TokenManager(settings)
        with pytest.raises(AuthError):
            tm.get_token()

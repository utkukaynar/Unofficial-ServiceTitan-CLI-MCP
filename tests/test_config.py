"""Tests for config.py."""

import os

import pytest

from st_cli.config import Environment, Settings


@pytest.fixture(autouse=True)
def clear_env_vars(monkeypatch):
    """Prevent .env file from leaking into tests."""
    monkeypatch.delenv("ST_ENVIRONMENT", raising=False)
    monkeypatch.delenv("ST_CLIENT_ID", raising=False)
    monkeypatch.delenv("ST_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("ST_APP_KEY", raising=False)
    monkeypatch.delenv("ST_TENANT_ID", raising=False)


class TestEnvironment:
    def test_production_urls(self):
        env = Environment.PRODUCTION
        assert "auth.servicetitan.io" in env.auth_url
        assert "api.servicetitan.io" in env.api_base
        assert "integration" not in env.auth_url

    def test_integration_urls(self):
        env = Environment.INTEGRATION
        assert "integration" in env.auth_url
        assert "integration" in env.api_base


class TestSettings:
    def test_creates_with_required_fields(self):
        s = Settings(
            client_id="cid",
            client_secret="csec",
            app_key="key",
            tenant_id=1,
            _env_file=None,
        )
        assert s.client_id == "cid"
        assert s.tenant_id == 1
        assert s.environment == Environment.PRODUCTION

    def test_defaults_to_production(self):
        s = Settings(
            client_id="a", client_secret="b", app_key="c", tenant_id=1,
            _env_file=None,
        )
        assert s.environment == Environment.PRODUCTION

    def test_auth_url_delegates_to_environment(self):
        s = Settings(
            client_id="a", client_secret="b", app_key="c", tenant_id=1,
            environment=Environment.INTEGRATION,
            _env_file=None,
        )
        assert "integration" in s.auth_url

    def test_api_base_delegates_to_environment(self):
        s = Settings(
            client_id="a", client_secret="b", app_key="c", tenant_id=1,
            environment=Environment.INTEGRATION,
            _env_file=None,
        )
        assert "integration" in s.api_base

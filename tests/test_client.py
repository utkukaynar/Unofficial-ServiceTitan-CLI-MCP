"""Tests for client.py."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest
import respx

from st_cli.client import ServiceTitanClient
from st_cli.config import Environment, Settings
from st_cli.exceptions import APIError, NotFoundError, RateLimitError


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        client_id="test-id",
        client_secret="test-secret",
        app_key="test-key",
        tenant_id=12345,
        environment=Environment.PRODUCTION,
    )


@pytest.fixture()
def client(settings):
    """Client with a mocked TokenManager so no real auth calls happen."""
    with patch("st_cli.client.TokenManager") as MockTM:
        MockTM.return_value.get_token.return_value = "fake-token"
        MockTM.return_value.force_refresh.return_value = "refreshed-token"
        c = ServiceTitanClient(settings)
        yield c
        c.close()


class TestServiceTitanClient:
    @respx.mock
    def test_get_success(self, client):
        url = "/crm/v2/tenant/12345/customers"
        respx.get(url).mock(return_value=httpx.Response(200, json={"data": []}))
        result = client.get("crm", "customers")
        assert result == {"data": []}

    @respx.mock
    def test_post_success(self, client):
        url = "/crm/v2/tenant/12345/customers"
        respx.post(url).mock(return_value=httpx.Response(200, json={"id": 1}))
        result = client.post("crm", "customers", json_body={"name": "Test"})
        assert result == {"id": 1}

    @respx.mock
    def test_patch_success(self, client):
        url = "/crm/v2/tenant/12345/customers/1"
        respx.patch(url).mock(return_value=httpx.Response(200, json={"id": 1}))
        result = client.patch("crm", "customers/1", json_body={"name": "New"})
        assert result == {"id": 1}

    @respx.mock
    def test_404_raises_not_found(self, client):
        url = "/crm/v2/tenant/12345/customers/999"
        respx.get(url).mock(return_value=httpx.Response(404, text="not found"))
        with pytest.raises(NotFoundError):
            client.get("crm", "customers/999")

    @respx.mock
    def test_500_raises_api_error(self, client):
        url = "/crm/v2/tenant/12345/customers"
        respx.get(url).mock(return_value=httpx.Response(500, text="server error"))
        with pytest.raises(APIError) as exc_info:
            client.get("crm", "customers")
        assert exc_info.value.status_code == 500

    @respx.mock
    def test_401_triggers_token_refresh(self, client):
        url = "/crm/v2/tenant/12345/customers"
        respx.get(url).mock(side_effect=[
            httpx.Response(401, text="expired"),
            httpx.Response(200, json={"data": []}),
        ])
        result = client.get("crm", "customers")
        assert result == {"data": []}

    @respx.mock
    def test_429_retries_with_backoff(self, client):
        url = "/crm/v2/tenant/12345/customers"
        respx.get(url).mock(side_effect=[
            httpx.Response(429, text="rate limited"),
            httpx.Response(200, json={"data": []}),
        ])
        with patch("st_cli.client.time.sleep"):  # skip actual sleep
            result = client.get("crm", "customers")
        assert result == {"data": []}

    @respx.mock
    def test_429_exhausts_retries(self, client):
        url = "/crm/v2/tenant/12345/customers"
        respx.get(url).mock(return_value=httpx.Response(429, text="rate limited"))
        with patch("st_cli.client.time.sleep"):
            with pytest.raises(RateLimitError):
                client.get("crm", "customers")

    @respx.mock
    def test_204_returns_none(self, client):
        url = "/jpm/v2/tenant/12345/jobs/1/cancel"
        respx.post(url).mock(return_value=httpx.Response(204))
        result = client.post("jpm", "jobs/1/cancel")
        assert result is None

    @respx.mock
    def test_headers_include_auth_and_app_key(self, client):
        url = "/crm/v2/tenant/12345/customers"
        route = respx.get(url).mock(return_value=httpx.Response(200, json={}))
        client.get("crm", "customers")
        request = route.calls[0].request
        assert "Bearer" in request.headers["authorization"]
        assert request.headers["st-app-key"] == "test-key"

    @respx.mock
    def test_params_are_passed(self, client):
        url = "/crm/v2/tenant/12345/customers"
        route = respx.get(url).mock(return_value=httpx.Response(200, json={}))
        client.get("crm", "customers", params={"name": "Acme"})
        request = route.calls[0].request
        assert "name=Acme" in str(request.url)

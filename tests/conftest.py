"""Shared fixtures for ST CLI tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from st_cli.client import ServiceTitanClient
from st_cli.config import Settings, Environment


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
def mock_client() -> MagicMock:
    """A mock ServiceTitanClient."""
    return MagicMock(spec=ServiceTitanClient)


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


def make_envelope(
    data: list,
    page: int = 1,
    page_size: int = 50,
    has_more: bool = False,
    total: int | None = None,
) -> dict:
    """Build a ServiceTitan-style page envelope."""
    return {
        "page": page,
        "pageSize": page_size,
        "hasMore": has_more,
        "totalCount": total if total is not None else len(data),
        "data": data,
    }


@pytest.fixture()
def invoke(runner: CliRunner, mock_client: MagicMock, settings: Settings):
    """Return a helper that invokes the CLI with mocked auth + client."""
    from st_cli.main import app

    def _invoke(args: list[str], json_output: bool = False):
        cli_args = list(args)
        if json_output:
            cli_args = ["--json"] + cli_args

        # Patch _LazyClient so it returns the mock_client directly
        with patch("st_cli.main._LazyClient") as MockLazy:
            MockLazy.return_value = mock_client
            return runner.invoke(app, cli_args, catch_exceptions=False)

    return _invoke

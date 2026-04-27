"""Root Typer app — global flags + module registration."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from st_cli.client import ServiceTitanClient
from st_cli.commands import accounting, crm, dispatch, jobs, memberships, reporting, settings
from st_cli.config import load_settings
from st_cli.exceptions import STCLIError

app = typer.Typer(
    name="st",
    help="CLI for the ServiceTitan REST API v2",
    no_args_is_help=True,
)

app.add_typer(crm.app, name="crm")
app.add_typer(jobs.app, name="jobs")
app.add_typer(dispatch.app, name="dispatch")
app.add_typer(accounting.app, name="accounting")
app.add_typer(memberships.app, name="memberships")
app.add_typer(reporting.app, name="reporting")
app.add_typer(settings.app, name="settings")


class _LazyClient:
    """Defers client creation until first attribute access (skips init for --help)."""

    def __init__(self, env_file: Path | None) -> None:
        self._env_file = env_file
        self._client: ServiceTitanClient | None = None

    def _init(self) -> ServiceTitanClient:
        if self._client is None:
            try:
                settings = load_settings(self._env_file)
            except Exception as exc:
                typer.echo(f"Config error: {exc}", err=True)
                raise typer.Exit(1) from exc
            self._client = ServiceTitanClient(settings)
        return self._client

    def __getattr__(self, name: str):
        return getattr(self._init(), name)


@app.callback()
def main(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Output as JSON instead of table"),
    env_file: Optional[Path] = typer.Option(None, "--env", help="Path to .env file"),
) -> None:
    """ServiceTitan CLI — interact with the ST API from the terminal."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_output
    ctx.obj["client"] = _LazyClient(env_file)


def cli() -> None:
    """Entry point for the `st` command."""
    try:
        app()
    except STCLIError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc

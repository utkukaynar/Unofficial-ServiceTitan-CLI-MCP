"""Settings commands: business units, job types."""

from __future__ import annotations

from typing import Optional

import typer

from st_cli.output import Column, render
from st_cli.pagination import fetch_all, fetch_page

MODULE = "settings"

app = typer.Typer(help="Settings — business units, job types")

BUSINESS_UNIT_COLUMNS: list[Column] = [
    ("ID", "id"),
    ("Name", "name"),
    ("Active", "active"),
    ("Default", "isDefault"),
    ("Address", "address.street"),
    ("City", "address.city"),
    ("State", "address.state"),
    ("Phone", "phoneNumber"),
]

JOB_TYPE_COLUMNS: list[Column] = [
    ("ID", "id"),
    ("Name", "name"),
    ("Business Unit ID", "businessUnitId"),
    ("Priority", "priority"),
    ("Duration (min)", "durationMinutes"),
    ("Active", "active"),
]


# --- Business Units ---


@app.command("business-units-list")
def business_units_list(
    ctx: typer.Context,
    active: Optional[bool] = typer.Option(None, help="Filter by active status"),
    page: int = typer.Option(1, help="Page number"),
    page_size: int = typer.Option(50, help="Page size"),
    all_pages: bool = typer.Option(False, "--all", help="Fetch all pages"),
) -> None:
    """List business units."""
    client = ctx.obj["client"]
    as_json = ctx.obj["json"]
    params: dict = {}
    if active is not None:
        params["active"] = active
    if all_pages:
        data = list(fetch_all(client, MODULE, "business-units", params, page_size=page_size))
        render(data, BUSINESS_UNIT_COLUMNS, as_json=as_json, title="Business Units")
    else:
        envelope = fetch_page(
            client, MODULE, "business-units", params, page=page, page_size=page_size
        )
        render(
            envelope.get("data", []),
            BUSINESS_UNIT_COLUMNS,
            as_json=as_json,
            title="Business Units",
            total_count=envelope.get("totalCount"),
        )


# --- Job Types ---


@app.command("job-types-list")
def job_types_list(
    ctx: typer.Context,
    active: Optional[bool] = typer.Option(None, help="Filter by active status"),
    page: int = typer.Option(1, help="Page number"),
    page_size: int = typer.Option(50, help="Page size"),
    all_pages: bool = typer.Option(False, "--all", help="Fetch all pages"),
) -> None:
    """List job types."""
    client = ctx.obj["client"]
    as_json = ctx.obj["json"]
    params: dict = {}
    if active is not None:
        params["active"] = active
    if all_pages:
        data = list(fetch_all(client, MODULE, "job-types", params, page_size=page_size))
        render(data, JOB_TYPE_COLUMNS, as_json=as_json, title="Job Types")
    else:
        envelope = fetch_page(client, MODULE, "job-types", params, page=page, page_size=page_size)
        render(
            envelope.get("data", []),
            JOB_TYPE_COLUMNS,
            as_json=as_json,
            title="Job Types",
            total_count=envelope.get("totalCount"),
        )

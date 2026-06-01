"""Memberships commands: memberships, membership-types."""

from __future__ import annotations

import typer

from st_cli.output import Column, render, render_single
from st_cli.pagination import fetch_all, fetch_page

MODULE = "memberships"

app = typer.Typer(help="Memberships — memberships, membership types")

MEMBERSHIP_COLUMNS: list[Column] = [
    ("ID", "id"),
    ("Customer ID", "customerId"),
    ("Type ID", "membershipTypeId"),
    ("Status", "status"),
    ("From", "from"),
    ("To", "to"),
    ("Created", "createdOn"),
]

MEMBERSHIP_TYPE_COLUMNS: list[Column] = [
    ("ID", "id"),
    ("Name", "name"),
    ("Duration Billing Periods", "durationBillingPeriods"),
    ("Active", "active"),
]


@app.command("list")
def memberships_list(
    ctx: typer.Context,
    page: int = typer.Option(1, help="Page number"),
    page_size: int = typer.Option(50, help="Page size"),
    all_pages: bool = typer.Option(False, "--all", help="Fetch all pages"),
) -> None:
    """List memberships."""
    client = ctx.obj["client"]
    as_json = ctx.obj["json"]
    if all_pages:
        data = list(fetch_all(client, MODULE, "memberships", page_size=page_size))
        render(data, MEMBERSHIP_COLUMNS, as_json=as_json, title="Memberships")
    else:
        envelope = fetch_page(client, MODULE, "memberships", page=page, page_size=page_size)
        render(
            envelope.get("data", []),
            MEMBERSHIP_COLUMNS,
            as_json=as_json,
            title="Memberships",
            total_count=envelope.get("totalCount"),
        )


@app.command("get")
def memberships_get(
    ctx: typer.Context, membership_id: int = typer.Argument(..., help="Membership ID")
) -> None:
    """Get a single membership by ID."""
    client = ctx.obj["client"]
    data = client.get(MODULE, f"memberships/{membership_id}")
    render_single(data, MEMBERSHIP_COLUMNS, as_json=ctx.obj["json"])


@app.command("types-list")
def types_list(
    ctx: typer.Context,
    page: int = typer.Option(1, help="Page number"),
    page_size: int = typer.Option(50, help="Page size"),
) -> None:
    """List membership types."""
    client = ctx.obj["client"]
    envelope = fetch_page(client, MODULE, "membership-types", page=page, page_size=page_size)
    render(
        envelope.get("data", []),
        MEMBERSHIP_TYPE_COLUMNS,
        as_json=ctx.obj["json"],
        title="Membership Types",
        total_count=envelope.get("totalCount"),
    )

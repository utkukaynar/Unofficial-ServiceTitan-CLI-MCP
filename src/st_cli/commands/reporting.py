"""Reporting commands: discover and pull ServiceTitan built-in/custom reports."""

from __future__ import annotations

import json
from typing import Any, Optional

import typer

from st_cli.output import Column, console, render
from st_cli.pagination import fetch_page

MODULE = "reporting"

app = typer.Typer(
    help="Reporting — discover and pull ServiceTitan reports (e.g. Technician Scorecard)",
)

CATEGORY_COLUMNS: list[Column] = [
    ("ID", "id"),
    ("Name", "name"),
]

REPORT_COLUMNS: list[Column] = [
    ("ID", "id"),
    ("Name", "name"),
]


# ---------------------------------------------------------------------------
# Helpers for the columnar report-data response
# ---------------------------------------------------------------------------


def _report_rows_to_dicts(
    fields: list[dict[str, Any]], data: list[list[Any]]
) -> list[dict[str, Any]]:
    """Convert the columnar report response into a list of dicts.

    The reporting API returns:
      fields: [{"name": "TechName", "label": "Technician", "type": "String"}, ...]
      data:   [["John", 15000], ["Jane", 22000]]

    We turn that into:
      [{"TechName": "John"}, {"TechName": "Jane"}]
    """
    names = [f["name"] for f in fields]
    return [dict(zip(names, row)) for row in data]


def _render_report(
    fields: list[dict[str, Any]],
    data: list[list[Any]],
    *,
    as_json: bool = False,
    title: str | None = None,
    total_count: int | None = None,
) -> None:
    """Render columnar report data as a rich table or JSON."""
    if as_json:
        rows = _report_rows_to_dicts(fields, data)
        console.print_json(json.dumps(rows, default=str))
        return

    from rich.table import Table

    table = Table(title=title, show_lines=False)
    for field in fields:
        table.add_column(field.get("label") or field["name"])

    for row in data:
        table.add_row(*(str(v) if v is not None else "" for v in row))

    console.print(table)
    if total_count is not None:
        console.print(f"[dim]Total: {total_count}[/dim]")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@app.command("categories")
def categories_list(
    ctx: typer.Context,
    page: int = typer.Option(1, help="Page number"),
    page_size: int = typer.Option(50, help="Page size"),
) -> None:
    """List report categories available for this tenant."""
    client = ctx.obj["client"]
    envelope = fetch_page(client, MODULE, "report-categories", page=page, page_size=page_size)
    render(
        envelope.get("data", []),
        CATEGORY_COLUMNS,
        as_json=ctx.obj["json"],
        title="Report Categories",
        total_count=envelope.get("totalCount"),
    )


@app.command("reports")
def reports_list(
    ctx: typer.Context,
    category_id: str = typer.Argument(..., help="Report category ID"),
    page: int = typer.Option(1, help="Page number"),
    page_size: int = typer.Option(50, help="Page size"),
) -> None:
    """List reports in a category."""
    client = ctx.obj["client"]
    envelope = fetch_page(
        client,
        MODULE,
        f"report-category/{category_id}/reports",
        page=page,
        page_size=page_size,
    )
    render(
        envelope.get("data", []),
        REPORT_COLUMNS,
        as_json=ctx.obj["json"],
        title="Reports",
        total_count=envelope.get("totalCount"),
    )


@app.command("fields")
def report_fields(
    ctx: typer.Context,
    category_id: str = typer.Argument(..., help="Report category ID"),
    report_id: str = typer.Argument(..., help="Report ID"),
) -> None:
    """Show a report's fields and required parameters."""
    client = ctx.obj["client"]
    meta = client.get(MODULE, f"report-category/{category_id}/reports/{report_id}")
    as_json = ctx.obj["json"]

    if as_json:
        console.print_json(json.dumps(meta, default=str))
        return

    # Parameters table
    params = meta.get("parameters", [])
    if params:
        from rich.table import Table

        pt = Table(title="Parameters", show_lines=False)
        pt.add_column("Name", style="bold")
        pt.add_column("Label")
        pt.add_column("Required")
        pt.add_column("Data Type")
        for p in params:
            pt.add_row(
                p.get("name", ""),
                p.get("label", ""),
                str(p.get("isRequired", "")),
                p.get("dataType", ""),
            )
        console.print(pt)

    # Fields table
    report_fields_list = meta.get("fields", [])
    if report_fields_list:
        from rich.table import Table

        ft = Table(title="Fields", show_lines=False)
        ft.add_column("Name", style="bold")
        ft.add_column("Label")
        ft.add_column("Type")
        for f in report_fields_list:
            ft.add_row(
                f.get("name", ""),
                f.get("label", ""),
                f.get("type", ""),
            )
        console.print(ft)

    if not params and not report_fields_list:
        typer.echo("No fields or parameters found.")


@app.command("data")
def report_data(
    ctx: typer.Context,
    category_id: str = typer.Argument(..., help="Report category ID"),
    report_id: str = typer.Argument(..., help="Report ID"),
    from_date: Optional[str] = typer.Option(None, "--from", help="From date (YYYY-MM-DD)"),
    to_date: Optional[str] = typer.Option(None, "--to", help="To date (YYYY-MM-DD)"),
    params: Optional[str] = typer.Option(
        None, "--params", help='Extra params as JSON, e.g. \'[{"name":"X","value":"Y"}]\''
    ),
    page: int = typer.Option(1, help="Page number"),
    page_size: int = typer.Option(50, help="Page size"),
    all_pages: bool = typer.Option(False, "--all", help="Fetch all pages"),
) -> None:
    """Fetch report data. Pass --from/--to for date-bounded reports."""
    client = ctx.obj["client"]
    as_json = ctx.obj["json"]

    parameters: list[dict[str, str]] = []
    if from_date:
        parameters.append({"name": "From", "value": from_date})
    if to_date:
        parameters.append({"name": "To", "value": to_date})
    if params:
        parameters.extend(json.loads(params))

    body: dict[str, Any] = {"parameters": parameters}
    resource = f"report-category/{category_id}/reports/{report_id}/data"

    if all_pages:
        all_fields: list[dict[str, Any]] = []
        all_data: list[list[Any]] = []
        current_page = 1
        while True:
            resp = client.post(
                MODULE,
                resource,
                json_body=body,
                params={"page": current_page, "pageSize": page_size},
            )
            if not all_fields:
                all_fields = resp.get("fields", [])
            all_data.extend(resp.get("data", []))
            if not resp.get("hasMore", False):
                break
            current_page += 1
        _render_report(
            all_fields,
            all_data,
            as_json=as_json,
            title="Report Data",
            total_count=len(all_data),
        )
    else:
        resp = client.post(
            MODULE,
            resource,
            json_body=body,
            params={"page": page, "pageSize": page_size},
        )
        _render_report(
            resp.get("fields", []),
            resp.get("data", []),
            as_json=as_json,
            title="Report Data",
            total_count=resp.get("totalCount"),
        )

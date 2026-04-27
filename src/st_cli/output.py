"""Rich table + JSON output formatting."""

from __future__ import annotations

import json
from typing import Any, Sequence

from rich.console import Console
from rich.table import Table

Column = tuple[str, str]  # (display_name, api_field_key)

console = Console()


def _resolve(record: dict[str, Any], key: str) -> Any:
    """Resolve a potentially nested key like 'address.city'."""
    parts = key.split(".")
    val: Any = record
    for part in parts:
        if isinstance(val, dict):
            val = val.get(part)
        else:
            return None
    return val


def render(
    data: list[dict[str, Any]],
    columns: Sequence[Column],
    *,
    as_json: bool = False,
    title: str | None = None,
    total_count: int | None = None,
) -> None:
    """Render a list of records as a table or JSON."""
    if as_json:
        console.print_json(json.dumps(data, default=str))
        return

    table = Table(title=title, show_lines=False)
    for display_name, _ in columns:
        table.add_column(display_name)

    for record in data:
        row = [str(_resolve(record, key) or "") for _, key in columns]
        table.add_row(*row)

    console.print(table)
    if total_count is not None:
        console.print(f"[dim]Total: {total_count}[/dim]")


def render_single(
    record: dict[str, Any],
    columns: Sequence[Column],
    *,
    as_json: bool = False,
) -> None:
    """Render a single record as a vertical key-value table or JSON."""
    if as_json:
        console.print_json(json.dumps(record, default=str))
        return

    table = Table(show_header=False, show_lines=True)
    table.add_column("Field", style="bold")
    table.add_column("Value")

    for display_name, key in columns:
        val = _resolve(record, key)
        table.add_row(display_name, str(val) if val is not None else "")

    console.print(table)

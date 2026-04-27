"""Pagination helpers for ServiceTitan list endpoints."""

from __future__ import annotations

from typing import Any, Iterator

from st_cli.client import ServiceTitanClient


def fetch_page(
    client: ServiceTitanClient,
    module: str,
    resource: str,
    params: dict[str, Any] | None = None,
    page: int = 1,
    page_size: int = 50,
) -> dict[str, Any]:
    """Fetch a single page. Returns the full envelope (page, pageSize, hasMore, totalCount, data)."""
    p = dict(params or {})
    p["page"] = page
    p["pageSize"] = page_size
    return client.get(module, resource, params=p)


def fetch_all(
    client: ServiceTitanClient,
    module: str,
    resource: str,
    params: dict[str, Any] | None = None,
    page_size: int = 50,
) -> Iterator[dict[str, Any]]:
    """Auto-paginate until hasMore=False, yielding each record."""
    page = 1
    while True:
        envelope = fetch_page(client, module, resource, params, page=page, page_size=page_size)
        for record in envelope.get("data", []):
            yield record
        if not envelope.get("hasMore", False):
            break
        page += 1

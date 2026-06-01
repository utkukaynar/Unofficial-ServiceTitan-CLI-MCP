# MCP server

`st-mcp` exposes the same operations as the CLI as **tools** for an MCP client
(Claude Code, Claude Desktop) over stdio.

```bash
st-mcp
```

It serves **~394 tools** spanning all 24 ServiceTitan modules — the same surface
as the CLI (see [API coverage](api-coverage.md)).

## Tool naming

`st_{module}_{resource}_{action}`, with hyphens normalized to underscores:

| CLI command | MCP tool |
|---|---|
| `st salestech estimates-sell 123 --data …` | `st_salestech_estimates_sell` |
| `st inventory purchase-orders-approve 678` | `st_inventory_purchase_orders_approve` |
| `st pricebook services-create --data …` | `st_pricebook_services_create` |
| `st jobs job-types-list` | `st_jpm_job_types_list` |
| `st telecom export-calls` | `st_telecom_export_calls` |

A resource named after its module drops the redundant segment
(`st_findings_list`, not `st_findings_findings_list`). Job types are under `jpm`
and estimates under `salestech` — the two prior routing bugs are fixed.

## Tool shapes

- **List** tools take an optional `filters` dict of query params plus
  `date_range` / `created_after` / `created_before`, and paginate via `page` or
  `max_results`.
- **Get / delete / single-id actions** take `record_id`.
- **Create / update / body actions** take a `data` dict.
- **Export** tools (`st_{module}_export_{feed}`) take `continue_from` and return
  `{ data, continueFrom, totalCount }` — persist `continueFrom` and pass it back
  to fetch only newer changes.

A few endpoints are hand-tuned with richer typed parameters:

| Tool | Notes |
|------|-------|
| `st_crm_customers_list` | `name` / `email` / `phone` filters |
| `st_jpm_jobs_list` | `status`, `customer_id`, date range |
| `st_dispatch_who_busy` | per-tech availability summary (shifts × appointments) |
| `st_dispatch_capacity` | flat body (`businessUnitIds`, `jobTypeId`, `skillBasedAvailability`); 14-day cap |
| `st_reporting_report_data` | 1 of the same report / minute / tenant |

## Pagination model

MCP tools auto-paginate up to a `max_results` cap rather than exposing `--all`:

| Parameter      | Default | Description                                |
|----------------|---------|--------------------------------------------|
| `page`         | none    | Specific page (disables auto-paginate)     |
| `page_size`    | 50      | Items per page                             |
| `max_results`  | 200     | Auto-paginate cap (hard limit: 1000)       |

## Error mapping

CLI exceptions map to FastMCP `ToolError`s:

| Source | MCP behavior |
|--------|--------------|
| `NotFoundError` | `ToolError("Not found: …")` |
| `RateLimitError` | `ToolError("Rate limited: …")` |
| `AuthError` | `ToolError("Authentication error: …")` |
| `ConfigError` | `ToolError("Configuration error: …")` |
| `DateParseError` | `ToolError("Invalid date range: …")` |
| `APIError` | `ToolError("API error (HTTP …): …")` |

## Hooking it up to Claude Code

The installer can do this for you (`./scripts/install.sh --code`). Manually, add
to `~/.claude/settings.json` (or a project `.claude/settings.json`):

```json
{
  "mcpServers": {
    "servicetitan": {
      "command": "st-mcp"
    }
  }
}
```

Then `/mcp` in Claude Code lists `servicetitan` and its tools.

> The MCP server reads the same `.env` / `ST_*` configuration as the CLI — see
> [Configuration](configuration.md).

---

← [API coverage](api-coverage.md) · [Docs index](README.md) · [Architecture →](architecture.md)

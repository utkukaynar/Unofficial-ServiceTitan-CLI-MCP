# Unofficial ServiceTitan CLI

An unofficial command-line tool and MCP server for the [ServiceTitan REST API v2](https://developer.servicetitan.io/). Two interfaces over the same core:

- **`st`** — Typer-based CLI with rich tables or JSON output, for humans.
- **`st-mcp`** — FastMCP server exposing the same operations as tools for AI agents over stdio.

> Not affiliated with or endorsed by ServiceTitan, Inc.

### Intended integration path: Customer-Built Apps only

ServiceTitan documents several integration paths in [Integration Paths](https://developer.servicetitan.io/integration-paths). **Use this repo only for the "Customer-Built Apps" path** — i.e. a ServiceTitan customer building an internal tool against their own tenant.

Other paths (apps distributed to additional ServiceTitan customers, e.g. Integrator/Marketplace apps) involve onboarding, review, and distribution requirements that this CLI does not satisfy. If you intend to ship something to other ServiceTitan customers, follow ServiceTitan's official path on the link above instead of using this project as a basis for distribution.

---

## Table of Contents

- [Install](#install)
- [Configure](#configure)
- [Quick Start](#quick-start)
- [Global Options](#global-options)
- [Date Ranges](#date-ranges)
- [Pagination](#pagination)
- [CLI Commands](#cli-commands)
  - [CRM](#crm) · [Jobs](#jobs) · [Dispatch](#dispatch) · [Accounting](#accounting) · [Memberships](#memberships) · [Reporting](#reporting) · [Settings](#settings)
- [MCP Server](#mcp-server)
- [Development](#development)

---

## Install

```bash
# Editable install with dev dependencies (uv)
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"

# Verify
st --help
st-mcp --help
```

Requires Python 3.11+.

---

## Configure

Create a `.env` file in the working directory (or pass `--env <path>`):

```dotenv
ST_CLIENT_ID=your-client-id
ST_CLIENT_SECRET=your-client-secret
ST_APP_KEY=your-app-key
ST_TENANT_ID=123456789
ST_ENVIRONMENT=production       # or "integration"
```

| Variable           | Required | Description                              |
|--------------------|----------|------------------------------------------|
| `ST_CLIENT_ID`     | Yes      | OAuth 2.0 client ID                      |
| `ST_CLIENT_SECRET` | Yes      | OAuth 2.0 client secret                  |
| `ST_APP_KEY`       | Yes      | ServiceTitan application key             |
| `ST_TENANT_ID`     | Yes      | Your ServiceTitan tenant (account) ID    |
| `ST_ENVIRONMENT`   | No       | `production` (default) or `integration`  |

| Environment   | Auth URL                                                  | API Base URL                              |
|---------------|-----------------------------------------------------------|-------------------------------------------|
| `production`  | `https://auth.servicetitan.io/connect/token`              | `https://api.servicetitan.io`             |
| `integration` | `https://auth-integration.servicetitan.io/connect/token`  | `https://api-integration.servicetitan.io` |

**Authentication.** OAuth 2.0 Client Credentials, handled automatically. Tokens are cached in-memory for the process lifetime and on disk at `~/.st_cli/token_cache.json`. Refreshed 60s before expiry. On `401` the client refreshes and retries once; on `429` it backs off exponentially.

---

## Quick Start

```bash
# 1. Configure
cat > .env <<'EOF'
ST_CLIENT_ID=...
ST_CLIENT_SECRET=...
ST_APP_KEY=...
ST_TENANT_ID=...
ST_ENVIRONMENT=production
EOF

# 2. Try a few commands
st crm customers-list --name "Smith"
st jobs list --range today --json
st dispatch who-busy --range this-week
st dispatch capacity --range this-week --bu-ids 1,2

# 3. Run the MCP server (for an AI agent client)
st-mcp
```

---

## Global Options

```text
st [--json] [--env PATH] COMMAND [ARGS]
```

| Option   | Description                                       |
|----------|---------------------------------------------------|
| `--json` | Output raw JSON instead of a rich table           |
| `--env`  | Path to a `.env` file (overrides default lookup)  |

A handful of commands (e.g. `dispatch capacity`) also accept a local `--json` flag at the end for ergonomics.

---

## Date Ranges

Date-filterable commands accept `--range`, `--from-date`, and `--to-date`. Explicit dates win over `--range`.

| Range                     | Resolves to                          |
|---------------------------|--------------------------------------|
| `today` / `yesterday` / `tomorrow`  | One-day window               |
| `last-7-days` / `last-30-days` / `last-90-days` | Rolling N-day window |
| `this-week` / `last-week` / `next-week`  | Mon–Sun                 |
| `this-month` / `last-month` / `next-month` | Calendar month        |
| `this-quarter` / `last-quarter` / `next-quarter` | Calendar quarter |
| `this-year` / `last-year` | Calendar year                        |
| `2025-03-15`              | Single date                          |
| `2025-01-01:2025-03-31`   | Explicit start:end                   |

> Dispatch endpoints filter on `startsOnOrAfter` / `startsBefore`; other modules use `createdOnOrAfter` / `createdBefore`. The CLI handles the mapping for you.

---

## Pagination

List commands support:

| Option         | Default | Description                       |
|----------------|---------|-----------------------------------|
| `--page`       | 1       | Page number                       |
| `--page-size`  | 50      | Items per page                    |
| `--all`        | off     | Auto-paginate through every page  |

```bash
st crm customers-list --page 3 --page-size 25
st jobs list --all --range this-month
```

---

## CLI Commands

### CRM

Customers, locations, bookings, contacts.

```bash
st crm customers-list [--name TEXT] [--email TEXT] [--phone TEXT] [--page] [--page-size] [--all]
st crm customers-get   CUSTOMER_ID
st crm customers-create --name TEXT [--data JSON]
st crm customers-update CUSTOMER_ID [--name TEXT] [--data JSON]

st crm locations-list  [--page] [--page-size] [--all]
st crm locations-get   LOCATION_ID

st crm bookings-list   [--page] [--page-size] [--all]
st crm bookings-get    BOOKING_ID
st crm bookings-create --data JSON
st crm bookings-update BOOKING_ID --data JSON

st crm contacts-list   [--page] [--page-size] [--all]
st crm contacts-get    CONTACT_ID
```

### Jobs

Jobs, appointments, projects (the `jpm` module).

```bash
st jobs list [--status TEXT] [--customer-id INT] [--range] [--from-date] [--to-date] [--page] [--page-size] [--all]
st jobs get    JOB_ID
st jobs create --data JSON
st jobs update JOB_ID --data JSON
st jobs cancel JOB_ID

st jobs appointments-list [--job-id INT] [--page] [--page-size]
st jobs appointments-get  APPOINTMENT_ID

st jobs projects-list [--page] [--page-size]
st jobs projects-get  PROJECT_ID
```

### Dispatch

Shifts, assignments, who's busy, events, zones, teams, capacity.

```bash
st dispatch shifts-list [--range] [--from-date] [--to-date] [--page] [--page-size] [--all]

st dispatch assignments-list [--technician-id INT] [--page] [--page-size] [--all]

# Cross-references shifts with appointments to compute per-tech booked vs. available hours
st dispatch who-busy [--range today] [--from-date] [--to-date]

st dispatch events-list   [--page] [--page-size]
st dispatch events-create --data JSON

st dispatch zones-list [--active/--no-active] [--page] [--page-size] [--all]
st dispatch teams-list [--active/--no-active] [--page] [--page-size] [--all]

# Capacity planning (max 14-day window, per ServiceTitan).
# POST /dispatch/v2/tenant/{tenant}/capacity — body matches Dispatch.V2.CapacityRequestArgs.
st dispatch capacity \
  [--range this-week] [--from-date] [--to-date] \
  [--bu-ids 1,2,3] [--job-type-id 10] [--skill-based] [--json]
```

The `capacity` response is rendered as one row per availability time frame, with start/end, business units, total/open hours, and the `isAvailable` / `isExceedingIdealBookingPercentage` flags from the API.

### Accounting

```bash
st accounting invoices-list  [--status] [--range] [--from-date] [--to-date] [--page] [--page-size] [--all]
st accounting invoices-get   INVOICE_ID

st accounting estimates-list [--status] [--range] [--from-date] [--to-date] [--page] [--page-size] [--all]
st accounting estimates-get  ESTIMATE_ID

st accounting payments-list  [--range] [--from-date] [--to-date] [--page] [--page-size] [--all]
```

### Memberships

```bash
st memberships list       [--page] [--page-size] [--all]
st memberships get        MEMBERSHIP_ID
st memberships types-list [--page] [--page-size]
```

### Reporting

Run ServiceTitan reports programmatically. **Rate limit: 5 calls per minute per report per tenant.**

```bash
# Discover what's available
st reporting categories
st reporting reports CATEGORY_ID
st reporting fields  CATEGORY_ID REPORT_ID

# Pull data
st reporting data CATEGORY_ID REPORT_ID \
  [--from YYYY-MM-DD] [--to YYYY-MM-DD] \
  [--params '[{"name":"TechnicianId","value":"99999"}]'] \
  [--page] [--page-size] [--all]
```

### Settings

```bash
st settings business-units-list [--active/--no-active] [--page] [--page-size] [--all]
st settings job-types-list      [--active/--no-active] [--page] [--page-size] [--all]
```

---

## MCP Server

`st-mcp` exposes the same operations as tools for an MCP client (e.g. Claude Code, Claude Desktop) over stdio.

```bash
st-mcp
```

### Pagination model

MCP tools auto-paginate up to a `max_results` cap rather than exposing `--all`:

| Parameter      | Default | Description                                |
|----------------|---------|--------------------------------------------|
| `page`         | none    | Specific page (disables auto-paginate)     |
| `page_size`    | 50      | Items per page                             |
| `max_results`  | 200     | Auto-paginate cap (hard limit: 1000)       |

### Available tools

Naming: `st_{module}_{resource}_{action}`.

| Tool | Notes |
|---|---|
| `st_crm_customers_list` / `_get` / `_create` / `_update` | name/email/phone filters |
| `st_crm_locations_list` / `_get` | |
| `st_crm_bookings_list` / `_get` / `_create` / `_update` | |
| `st_crm_contacts_list` / `_get` | |
| `st_jpm_jobs_list` / `_get` / `_create` / `_update` / `_cancel` | status, customer_id, date range |
| `st_jpm_appointments_list` / `_get` | |
| `st_jpm_projects_list` / `_get` | |
| `st_dispatch_shifts_list` | date filters |
| `st_dispatch_assignments_list` | technician_id filter |
| `st_dispatch_who_busy` | per-tech availability summary |
| `st_dispatch_events_list` / `_create` | |
| `st_dispatch_zones_list` / `st_dispatch_teams_list` | |
| `st_dispatch_capacity` | flat body (`businessUnitIds`, `jobTypeId`, `skillBasedAvailability`); 14-day cap |
| `st_accounting_invoices_list` / `_get` | |
| `st_accounting_estimates_list` / `_get` | |
| `st_accounting_payments_list` | |
| `st_memberships_list` / `_get` / `_types_list` | |
| `st_reporting_categories_list` / `_reports_list` / `_report_fields` / `_report_data` | |
| `st_settings_business_units_list` / `_get` | |
| `st_settings_job_types_list` / `_get` | |

### Error mapping

CLI exceptions map to FastMCP `ToolError`s:

| Source             | MCP behavior        |
|--------------------|---------------------|
| `AuthenticationError` | `ToolError`      |
| `APIError`         | `ToolError`         |
| `ConfigError`      | `ToolError`         |

### Hooking it up to Claude Code

`~/.claude/settings.json` (or project `.claude/settings.json`):

```json
{
  "mcpServers": {
    "servicetitan": {
      "command": "st-mcp"
    }
  }
}
```

Then `/mcp` in Claude Code will list `servicetitan` and its tools.

---

## Development

```bash
# Tests
uv run pytest                                  # full suite
uv run pytest tests/commands/test_dispatch.py  # one file
uv run pytest -x                               # stop on first failure

# Lint + format
uv run ruff check src/ tests/
uv run ruff format src/ tests/
uv run mypy src/
```

### Architecture notes

- `client.py` — httpx-based `ServiceTitanClient` with auth refresh and 429 backoff.
- `auth.py` — OAuth 2.0 Client Credentials with two-tier (memory + disk) cache.
- `pagination.py` — `fetch_page` / `fetch_all` cursor helpers.
- `dates.py` — Human-friendly date-range parser; `validate_max_range` enforces caps like 14 days for `dispatch capacity`.
- `availability.py` — Pure function: shifts + appointments → per-tech availability rows.
- `output.py` — Rich table rendering (CLI only).
- `commands/<module>.py` — Typer sub-apps for each ServiceTitan module.
- `mcp_server.py` — FastMCP wrappers over the same client/pagination/date helpers.

URL pattern for every API call: `/{module}/v2/tenant/{tenant_id}/{resource}`.

### Tests

- HTTP-level mocking with `respx` for `client.py`.
- CLI tests use Typer's `CliRunner` plus the `mock_client` fixture and a `make_envelope()` helper for ServiceTitan-style paginated responses.
- `time-machine` is available for date-dependent tests.

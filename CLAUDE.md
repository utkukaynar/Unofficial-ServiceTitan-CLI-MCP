# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

`st-cli` is a CLI tool and MCP server for the ServiceTitan REST API v2. It provides two interfaces to the same API:
1. **`st` CLI** — Typer-based command-line tool for humans (rich tables or JSON output)
2. **`st-mcp` MCP server** — FastMCP server exposing the same operations as tools for AI agents (stdio transport)

## Commands

```bash
# Install (editable, with dev deps)
pip install -e ".[dev]"

# Run tests
pytest
pytest tests/test_client.py                    # single file
pytest tests/test_client.py::TestServiceTitanClient::test_get_success  # single test
pytest -x                                      # stop on first failure

# Lint & type check
ruff check src/ tests/
ruff format --check src/ tests/
mypy src/

# Auto-fix lint
ruff check --fix src/ tests/
ruff format src/ tests/

# Run the CLI
st --help
st crm customers-list --range last-week
st jobs list --all --json

# Run the MCP server
st-mcp
```

## Architecture

### Dual-interface pattern (CLI + MCP share core logic)

Both `main.py` (Typer CLI) and `mcp_server.py` (FastMCP) are thin wrappers over the same core modules. They share:
- `client.py` — `ServiceTitanClient` (httpx-based, handles retry/auth refresh)
- `pagination.py` — `fetch_page` / `fetch_all` (cursor-based auto-pagination)
- `dates.py` — `apply_date_params` / `parse_date_range` (human-friendly date ranges like `last-week`, `this-month`)
- `availability.py` — `_build_busy_summary` (pure function: shifts + appointments → availability rows)
- `output.py` — Rich table rendering (CLI only)

When adding a new endpoint, you usually do **not** hand-write it. The full 24-module
surface (~390 commands/tools) is generated from one declarative spec:

- `registry.py` — declares every module → resource → ops (`L`/`R`/`C`/`U`/`D`/`P`) +
  domain `Action`s + `export_feeds`. The 7 hand-written groups appear in `EXTENSIONS`
  (gap ops only, to avoid name collisions); the other 17 modules in `MODULES`.
- `engine.py` — closure factories that turn a `Resource` into Typer commands
  (`add_resource_commands` / `build_cli_app`) and FastMCP tools (`register_mcp_tools`
  via `McpDeps`). Each generated callable is a distinct closure with a *fixed*
  signature, so both Typer and FastMCP introspect it normally (no dynamic-signature
  hacking). A resource named after its module gets bare command names
  (`st findings list`, not `findings-list`).

**To add a resource:** add a `Resource(...)` to the right `Module` in `registry.py`.
Both interfaces pick it up automatically. Only hand-write a command/tool (in
`commands/<module>.py` + `mcp_server.py`) when it needs bespoke logic the generic
archetypes can't express (e.g. `dispatch capacity`, `dispatch who-busy`, reporting,
typed list filters). Generated list commands take a generic repeatable
`--filter key=value` (MCP: a `filters` dict) instead of typed per-field options.

> Note: estimates live in `salestech` (not `accounting`) and job types in `jpm`
> (not `settings`) — two prior routing bugs, now fixed. The hand-written
> `accounting estimates-*` / `settings job-types-*` commands were removed; the
> registry provides them under the correct modules.

### ServiceTitan API URL structure

All API calls follow: `/{module}/v2/tenant/{tenant_id}/{resource}`

Each command module defines its own `MODULE` constant (e.g., `"crm"`, `"jpm"`, `"dispatch"`, `"accounting"`, `"memberships"`). The client builds the full URL from module + resource.

### Authentication flow

`auth.py` implements OAuth 2.0 Client Credentials with two-tier caching (in-memory + file at `~/.st_cli/token_cache.json`). The client auto-refreshes on 401 and retries with exponential backoff on 429.

### Config

`pydantic-settings` loads config from env vars prefixed `ST_` (e.g., `ST_CLIENT_ID`, `ST_TENANT_ID`). Supports `production` and `integration` environments which map to different API/auth base URLs. The CLI accepts `--env` to point to a specific `.env` file.

### Command module pattern

Each command module in `src/st_cli/commands/` follows the same structure:
- `MODULE = "..."` constant for the API module name
- `*_COLUMNS` lists defining `(display_name, api_field_key)` tuples for table output
- Commands get `client` and `json` flag from `ctx.obj` (set by the root callback in `main.py`)
- List commands support `--page`/`--page-size` or `--all` for auto-pagination
- Date-filterable commands accept `--range`, `--from-date`, `--to-date`

### MCP server differences from CLI

- Uses `_paginate()` helper with `max_results` cap (default 200, hard cap 1000) instead of raw `--all`
- `_handle_errors` decorator maps `STCLIError` subtypes to `ToolError`
- Client is created in `_lifespan` context manager, shared across all tool calls
- Tool names follow `st_{module}_{resource}_{action}` convention

### Testing patterns

- Tests use `respx` to mock HTTP at the transport layer (for `client.py` tests)
- CLI command tests use Typer's `CliRunner` with a mocked client via the `invoke` fixture in `conftest.py`
- `make_envelope()` helper builds ServiceTitan-style paginated response envelopes
- `time-machine` is available for date-dependent tests (e.g., `dates.py` tests)

### Date range handling

Dispatch endpoints use `startsOnOrAfter`/`startsBefore` keys while other modules use `createdOnOrAfter`/`createdBefore`. The `apply_date_params()` function accepts `start_key`/`end_key` overrides for this.

## Ruff config

Line length 100, target Python 3.11, lint rules: E, F, I, N, W. mypy is strict.

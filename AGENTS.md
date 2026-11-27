# AGENTS.md

Entry point for any agent (Claude Code, Codex, etc.) working in this repo. `CLAUDE.md` is a
symlink to this file — always edit `AGENTS.md`, never replace the symlink with a copy.

## What This Is

`st-cli` is a CLI tool and MCP server for the ServiceTitan REST API v2. It provides two interfaces to the same API:
1. **`st` CLI** — Typer-based command-line tool for humans (rich tables or JSON output)
2. **`st-mcp` MCP server** — FastMCP server exposing the same operations as tools for AI agents (stdio transport)

## Verify a Change

Run all of these before calling a change done:

```bash
uv run python -m pytest                 # must pass
uv run ruff check src/ tests/           # must pass
uv run ruff format --check src/ tests/  # must pass
uv run mypy src/                        # pre-existing errors (86 as of 2026-11-27) — don't add new ones
```

`tests/test_spec_conformance.py` only runs when ServiceTitan's OpenAPI documents
are in `specs/` (see Hard Constraints). Download them before touching
`registry.py` — that test is what catches wrong verbs, paths and module URLs.

## Hard Constraints

- **Add endpoints through `registry.py`, not by hand — and check the spec first.** Both
  interfaces are generated from the registry, so a registry entry keeps the CLI and MCP surfaces
  in lockstep. Before 2026-11 the registry was written from memory and 119 of its operations
  called endpoints that don't exist; confirm verb, path, version, paging and body against
  `specs/` and run the conformance test. Use a `Resource` for numeric-id CRUD, an `Endpoint` for
  anything else (parent ids in the path, string ids, bulk ops, v3). Hand-write a command/tool
  only when it needs logic the archetypes can't express, and add its operation to
  `HANDWRITTEN` in `tests/test_spec_conformance.py`.
- **Never commit ServiceTitan's OpenAPI documents (`specs/` is gitignored).** ServiceTitan's API
  Terms §9.1 treat API documentation as confidential and the repo is public. Download them per
  `docs/development.md#spec-conformance`.
- **Keep `docs/terms.md` and the README terms section accurate.** They summarise ServiceTitan's
  API Terms for users of a public repo — notably that `st-mcp` is an "AI System" needing
  ServiceTitan's disclosure and approval (§3.4). Re-check the clause text and section numbers
  against https://www.servicetitan.com/legal/api-terms before changing them; don't paraphrase
  from memory.
- **Generated callables keep fixed signatures (closure factories in `engine.py`).** Typer and
  FastMCP build their CLI options / tool schemas by introspecting the function signature;
  dynamic-signature tricks break one or both.
- **URL segment, MCP name and CLI group can all differ.** `Module.name` drives MCP tool names,
  `Module.url` the URL segment, `Module.group` the CLI group. ServiceTitan serves six modules
  without the hyphen (`/equipmentsystems/`, `/taskmanagement/`, `/schedulingpro/`,
  `/marketingads/`, `/marketingreputation/`, `/fleetpro/`); estimates are `/sales/` (CLI
  `salestech`); job types live in `jpm`, not `settings`. Every one of these was a 404 bug —
  don't "tidy" them back.
- **Date-filterable MCP list tools default to `sort=-modifiedOn` (newest first).** ServiceTitan
  has no documented default order and returns oldest-first in practice, so "latest X" queries
  were returning January records. Resources whose sort enum rejects `modifiedOn` must set
  `Resource.default_sort` (e.g. `payroll/gross-pay-items` uses `-date`), otherwise the
  default request 400s. Precedence: `filters["sort"]` > `sort` kwarg > `default_sort` > none.
- **MCP list results are capped** (`max_results` default 200, hard cap 1000) so a single tool
  call can't flood an agent's context or hammer the API with unbounded pagination.
- **Never commit credentials.** Config comes from `ST_*` env vars / `.env` (gitignored); OAuth
  tokens are cached in `~/.st_cli/token_cache.json`, outside the repo.
- **Docs may only reference real commands/tools.** `tests/test_docs.py` checks every `st …`
  command and `st_…` tool in README.md and docs/. Regenerate `docs/api-coverage.md` with
  `uv run python scripts/gen_api_coverage.py` after registry changes.
- **mypy is strict; ruff line length is 100** (target Python 3.11, rules E, F, I, N, W).

## Commands

```bash
# Install (editable, with dev deps)
pip install -e ".[dev]"

# Run tests
pytest
pytest tests/test_client.py                    # single file
pytest tests/test_client.py::TestServiceTitanClient::test_get_success  # single test
pytest -x                                      # stop on first failure

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

When adding a new endpoint, you usually do **not** hand-write it. The full 25-module
surface (~600 commands/tools, every operation in ServiceTitan's OpenAPI documents) is
generated from one declarative spec:

- `registry.py` — declares every module → resource → ops (`L`/`R`/`C`/`U`/`D`/`P`) +
  domain `Action`s + `export_feeds`, plus `Endpoint`s (one verb on a path template) for
  everything CRUD can't express. Builders (`_custom_fields`, `_mark_exported`, `_nested_crud`,
  `_tagging`) declare ServiceTitan's repeated shapes once. The 7 hand-written groups appear in
  `EXTENSIONS` (gap ops only, to avoid name collisions); the other 18 modules in `MODULES`.
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

### ServiceTitan API URL structure

All API calls follow: `/{module}/{version}/tenant/{tenant_id}/{resource}` — `v2` except a few
`v3`-only endpoints (CRM leads create, telecom calls feed and opt-outs). Every client method
takes `version=`.

Each command module defines its own `MODULE` constant (e.g., `"crm"`, `"jpm"`, `"dispatch"`, `"accounting"`, `"memberships"`). The client builds the full URL from module + resource. In the registry, `Module.url` overrides the URL segment and `Module.group` the CLI group when they differ from `Module.name` (see Hard Constraints).

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
- Tool names follow `st_{module}_{resource}_{action}` convention (`Module.name`, not the URL)
- Endpoint tools take a `path` dict, validated before any API call (`UsageError` → `ToolError`)
- List tools accept an optional `sort` (e.g. `-completedOn`, `+createdOn`); generated
  date-filterable list tools default to newest-first (see Hard Constraints)

### Testing patterns

- Tests use `respx` to mock HTTP at the transport layer (for `client.py` tests)
- CLI command tests use Typer's `CliRunner` with a mocked client via the `invoke` fixture in `conftest.py`
- `make_envelope()` helper builds ServiceTitan-style paginated response envelopes
- `mcp_ctx` / `deps` fixtures (conftest) give MCP tool factories a mock client
- `test_spec_conformance.py` checks the registry against `specs/` (skipped when absent)
- `time-machine` is available for date-dependent tests (e.g., `dates.py` tests)

### Date range handling

Dispatch endpoints use `startsOnOrAfter`/`startsBefore` keys while other modules use `createdOnOrAfter`/`createdBefore`. The `apply_date_params()` function accepts `start_key`/`end_key` overrides for this.

Explicit ranges accept either `:` or `..` as the separator (`2026-01-01:2026-01-31` or
`2026-01-01..2026-01-31`) — LLM callers routinely emit the `..` form.

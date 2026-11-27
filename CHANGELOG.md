# Changelog

All notable changes to `st-cli` (the `st` CLI and `st-mcp` MCP server) are
documented here. Format follows [Keep a Changelog](https://keepachangelog.com/);
this project aims for [Semantic Versioning](https://semver.org/).

## [Unreleased] · Spec conformance

Checked the whole surface against ServiceTitan's published OpenAPI documents
(25 APIs, 607 operations, downloaded from developer.servicetitan.io on
2026-11-27). **119 of the commands/tools shipped in 0.2.0 called endpoints that
don't exist** (404/405), and 333 documented operations weren't exposed at all.
Both are fixed, and a test now keeps them fixed.

| | 0.2.0 | Unreleased |
|---|---|---|
| Spec operations exposed | 274 / 607 | **606 / 607** (1 deliberately omitted) |
| Calls to non-existent endpoints | 119 | **0** |
| CLI commands / MCP tools | 393 / 394 | **608 / 608** |
| Modules | 24 | **25** (adds Fleet Pro) |

### Fixed

- **Six modules were unreachable.** ServiceTitan serves them without the hyphen:
  `/equipmentsystems/`, `/taskmanagement/`, `/schedulingpro/`, `/marketingads/`,
  `/marketingreputation/` (and the new `/fleetpro/`). Every command in those
  groups returned 404. CLI groups and MCP tool names are unchanged.
- **Wrong HTTP verbs:** `jobs cancel`, estimate `sell` / `unsell` / `dismiss`,
  appointment `hold` / `confirm` / `reschedule`, arrival-window `activate`,
  purchase-order/receipt/return `cancel`, recurring-service-event
  `mark-complete` / `mark-incomplete`.
- **Wrong paths:** recurring services and events (`recurring-services`, not
  `location-recurring-services`), materials markup (`materialsmarkup`),
  client-specific pricing (`clientspecificpricing`), location findings, payroll
  settings / payrolls / timesheets / splits, mark-as-exported
  (`markasexported`), technician-skill assignment, project `attach-job`.
- **`jobs cancel`** now sends the required `{reasonId, memo}` body
  (`--reason-id`, `--memo`; MCP `reason_id`, `memo`).
- **`accounting invoices-get`** — ServiceTitan has no single-invoice route; it now
  filters the invoice list by id and reports "not found" cleanly.
- **`crm contacts-get`** takes the contact's GUID (it was typed as an integer).
- **Telecom `calls-list`** uses the v3 calls feed, which supports `sort` (the v2
  list ignored the newest-first default).
- MCP server instructions named tools that don't exist
  (`st_salestech_estimates_sell` → `st_sales_estimates_sell`).

### Added

- **`Endpoint` archetype** in the registry for operations CRUD can't express:
  parent IDs in the path, string IDs, bulk operations, `v3`-only endpoints. CLI
  takes path parameters positionally; MCP takes a `path` dict validated before
  any API call.
- **332 newly exposed operations**, including contact methods / preferences /
  relationships, customer and location notes, contacts and tags, custom fields
  and mark-as-exported across accounting and inventory, job notes / history /
  equipment, project daily logs, work-breakdown-structure budget codes,
  expense transactions, equipment systems, finding attachments, booking-provider
  bookings, SMS opt-outs, long-running report queries, and 25 more export feeds.
- **Fleet Pro** module (`st fleet-pro`, `st_fleet_pro_*`).
- `st settings business-units-get` (the MCP tool already existed).
- **`tests/test_spec_conformance.py`** — every operation st-cli sends must exist
  in the specs; every spec operation must be exposed or explicitly listed; list
  commands must hit paginated endpoints; date-filtered lists must accept their
  date keys and default sort. Skipped when `specs/` isn't downloaded (the specs
  aren't committed — ServiceTitan's API Terms treat API documentation as
  confidential).
- **`tests/test_docs.py`** — docs may only mention commands and tools that exist.
- **[ServiceTitan API Terms](docs/terms.md)** page and README section: AI-agent
  disclosure and approval, 24-hour cache limit, credentials, rate limits,
  confidentiality, affiliation.

### Changed (breaking)

Commands that never worked were removed or renamed to the real operation:

| Removed / renamed | Use instead |
|---|---|
| `crm bookings-create` / `bookings-update` | `crm provider-bookings-create` / `-update` (bookings are created per booking provider) |
| `crm customers-delete`, `crm locations-delete` | — (no such endpoint) |
| `crm contacts-create/update/delete` (int id) | same names, now take the GUID |
| `inventory purchase-orders-approve` / `-reject` | `inventory purchase-order-requests-approve` / `-reject` |
| `settings employees-activate` / `-deactivate` (and technicians) | `settings employees-account-action ID --data '{"action":"Deactivate"}'` |
| `dispatch skills-assign` (POST) | `dispatch skills-assign` (PATCH, no id) |
| `dispatch events-update` | `dispatch events-replace` (PUT) |
| `findings list/get/create/…`, `finding-assets-list` | `findings location-findings-*`, `assets-upload` / `assets-download` |
| `jobs budget-codes-*` | `jobs budget-codes-list/create/…` and `wbs-*` (work breakdown structure) |
| `payroll employee-payroll-settings-*`, `timesheets-list`, `job-splits-list` | `payroll employee-payroll-settings ID`, `job-timesheets-list`, `job-splits-list` (`jobs/splits`) |
| `salestech proposal-types-list/get` | `salestech proposal-types-list` |
| `scheduling-pro sessions-list`, `schedulers-get` | `scheduling-pro scheduler-sessions ID` |
| `marketing-ads *-attributions-post` | `marketing-ads *-attributions-create` |
| Single-record `-get` / `-update` on resources without that route (e.g. `payments-get`, `tag-types-get`) | the list command with `--filter ids=…` |

## [0.2.0] — 2026-06-03 · Full ServiceTitan API coverage

The headline release: `st` and `st-mcp` now span the **entire ServiceTitan REST
API v2** — **all 24 modules**, **393 CLI commands**, and **394 MCP tools** — up
from ~40 hand-written endpoints across 7 modules. The expansion is generated
from a single declarative spec, so the surface stays consistent and cheap to
extend instead of being hand-maintained one function at a time.

### TL;DR

| | Before (0.1.x) | After (0.2.0) |
|---|---|---|
| Modules | 7 | **24** |
| CLI commands | ~40 | **393** |
| MCP tools | ~40 | **394** |
| Source of truth | hand-written per endpoint | one declarative registry |
| Tests | — | **248 passing** |

### Added

- **Registry-driven coverage of all 24 modules.** A new `registry.py` declares
  every module → resource → operation, and a new `engine.py` turns each
  `Resource` into both Typer commands and FastMCP tools from the same spec.
  Newly covered modules include: `pricebook`, `inventory`, `salestech`
  (estimates), `payroll`, `marketing`, `marketing-ads`, `timesheets`,
  `equipment-systems`, `findings`, `task-management`, `telecom`,
  `customer-interactions`, `forms`, `job-booking` (`jbce`),
  `marketing-reputation`, `scheduling-pro`, and `service-agreements` — plus
  gap operations layered onto the existing `crm`, `jobs` (`jpm`), `dispatch`,
  `accounting`, `memberships`, and `settings` groups.
- **Full CRUD + domain actions.** Beyond list/get, generated resources support
  create (`POST`), update (`PATCH`), replace (`PUT`), delete, and documented
  domain actions (e.g. `salestech estimates-sell`, `inventory
  purchase-orders-approve`, `dispatch assignments-assign-technicians`).
- **Export change-feeds.** Modules with change-feeds expose `export-<feed>`
  commands/tools that stream the dataset and return a `continueFrom` token for
  incremental resume (`pagination.fetch_export_page` / `fetch_export_all`).
- **HTTP verbs.** `client.py` gained `put()` and `delete()` (delete accepts
  query params and an optional body) to back the new write operations.
- **Generic list filtering.** Generated list commands take a repeatable
  `--filter key=value` (MCP: a `filters` dict), with light bool/int coercion.
- **Docs set.** A multi-page `docs/` tree (installation, configuration, usage,
  CLI reference, **API coverage**, MCP server, architecture, development) plus a
  per-module **[Examples & recipes](docs/examples.md)** page with timeframes and
  paired CLI ↔ MCP samples. `scripts/gen_api_coverage.py` regenerates the
  coverage inventory from the live command/tool trees.
- **Tests.** New `test_registry.py` (spec invariants, collision and routing
  checks) and `test_engine.py` (factory + generated-command behavior), alongside
  expanded client/pagination/MCP coverage — 248 tests total.

### Fixed

- **Estimates routing.** `estimates` now correctly live under `salestech`
  (`/salestech/...`), not `accounting`. The old `accounting estimates-*`
  commands/tools were removed.
- **Job types routing.** `job-types` now correctly live under `jpm`/`jobs`
  (`/jpm/...`), not `settings`. The old `settings job-types-*` command was
  removed.
- **Reporting rate-limit note** corrected to "1 of the same report per minute
  per tenant."

### Changed

- Both `main.py` (CLI) and `mcp_server.py` (MCP) are now thin wrappers that wire
  the registry through the engine; the 7 original modules keep their hand-tuned
  typed filters as bespoke escapes where the generic archetypes don't fit.
- A resource named after its module gets bare names (`st findings list`,
  `st_findings_list`) rather than a redundant slug.
- MCP tool names follow `st_{module}_{resource}_{action}`; note `jobs`→`jpm` and
  `estimates`→`salestech` in the module segment.

### Migration notes

- `st accounting estimates-list/get` → **`st salestech estimates-list/get`**
  (MCP: `st_accounting_estimates_*` → `st_salestech_estimates_*`).
- `st settings job-types-list` → **`st jobs job-types-list`**
  (MCP: `st_settings_job_types_*` → `st_jpm_job_types_*`).
- No changes to auth, configuration (`ST_*` env vars), or the seven original
  groups' existing commands.

## [0.1.0] — Initial release

- `st` Typer CLI and `st-mcp` FastMCP server over a shared core (client, auth,
  pagination, human-friendly date ranges, rich table output).
- Hand-written coverage of `crm`, `jobs`, `dispatch`, `accounting`,
  `memberships`, `reporting`, and `settings`, including dispatch availability
  (`who-busy`, `capacity`).

[0.2.0]: https://github.com/utkukaynar/Unofficial-ServiceTitan-CLI-MCP/releases/tag/v0.2.0

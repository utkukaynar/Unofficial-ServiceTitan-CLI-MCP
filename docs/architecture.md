# Architecture

Two front ends — the `st` CLI and the `st-mcp` server — sit on **one shared
core**. They never speak HTTP, parse dates, or paginate themselves; they delegate
to the same helpers. The ~390-command surface is generated from a single
declarative spec rather than hand-written per endpoint, and checked against
ServiceTitan's own OpenAPI documents by `tests/test_spec_conformance.py`.

```
            st (CLI)                         st-mcp (MCP server)
        commands/*.py (bespoke)          mcp_server.py (bespoke tools)
                 \                                  /
                  \         registry.py            /
                   \   (declares every module)    /
                    \           |                /
                     \      engine.py           /
                      \  (generates commands   /
                       \   + tools from spec) /
                        \         |          /
                         ────── shared core ──────
              client.py · auth.py · pagination.py · dates.py · output.py
                                   |
                       ServiceTitan REST API
          /{module}/{v2|v3}/tenant/{tenant_id}/{resource}
```

## Why generated, not hand-written

Hand-writing all ~560 operations twice (CLI + MCP) would be ~10,000 lines of
near-identical boilerplate — a DRY disaster where one pagination fix means
hundreds of edits. Instead:

- **`registry.py`** — *data*, not code. Each `Resource` declares which standard
  operations it supports (the string `"LRCUDP"` — **L**ist, **R**ead, **C**reate,
  **U**pdate/PATCH, **D**elete, **P**ut), plus domain `Action`s (`sell`, `approve`,
  `cancel`…) and `export_feeds`. Anything that doesn't fit that shape is an
  `Endpoint` (see below).
- **`engine.py`** — turns each `Resource` and `Endpoint` into Typer commands and
  FastMCP tools. Fixes propagate everywhere at once.
- **The 7 original modules stay hand-written** as bespoke escapes (typed filters,
  `dispatch who-busy`, `dispatch capacity`, reporting). The registry only fills
  their *gaps*, so no command/tool names collide.

This is the "hybrid registry + bespoke escapes" pattern: DRY for the bulk,
explicit where ergonomics or special logic demand it.

## The generation technique: closure factories

Typer and FastMCP both build their schemas by **introspecting a function's
signature** (`inspect.signature`). So each generated command must be a real
function with a real signature. The engine uses **closure factories**: each call
to `_make_list_cmd(module, resource)` returns a fresh inner function with a
*fixed* signature that closes over the per-resource data.

```python
def _make_list_cmd(module, resource):
    cols, path, title = ...              # captured per resource
    def _cmd(ctx, filter_=..., page=..., all_pages=...):
        ...                              # uses the captured values
    return _cmd                          # distinct function, fixed signature
```

No `exec`, no dynamically-built `inspect.Signature`. Two consequences worth
knowing (both bit us once):

- The MCP factories capture via the **enclosing factory scope**, not via
  default-argument tricks (`_p=path`). A leaked default arg would show up as a
  *tool parameter the model could pass* — FastMCP reads the whole signature.
- `engine.py` imports `Context` at **module scope** (not locally) because
  `from __future__ import annotations` makes annotations strings that FastMCP
  resolves against module globals at runtime.

## Endpoints: everything CRUD can't express

About a third of ServiceTitan's operations don't fit "resource + numeric id":
parent IDs in the path (`contacts/{contactId}/contact-methods/{id}`), string
IDs (contacts, journal entries, technician skills), bulk operations with no ID
(`invoices/custom-fields`), and endpoints that exist only under `v3`. Each is
declared as one `Endpoint` — a verb on a path template:

```python
Endpoint(
    "contacts-methods-get",                                   # command / tool suffix
    "GET",
    "contacts/{contactId}/contact-methods/{contactMethodId}", # placeholders, in order
    paged=False,          # True → standard page envelope, gets --page/--all
    body=False,           # True → requires --data / data
    version="v2",
)
```

The engine still uses fixed-signature closures: the CLI takes the placeholders
as positional arguments (count checked against the template), the MCP tool takes
a `path` dict and validates every key **before** calling the API. Small builders
in `registry.py` (`_custom_fields`, `_mark_exported`, `_nested_crud`, `_tagging`)
declare ServiceTitan's repeated shapes once.

## Module URL ≠ module name

`Module.name` drives MCP tool names (`st_equipment_systems_*`); `Module.url`
overrides the URL segment where ServiceTitan differs — it serves Equipment
Systems at `/equipmentsystems/`, Task Management at `/taskmanagement/`, and so on.
`Module.group` likewise overrides the CLI group (`sales` → `st salestech`).

## Naming conventions

- A resource named after its module gets **bare** command/tool names:
  `st memberships update` → `st_memberships_update` (not `memberships-update` /
  `st_memberships_memberships_update`). Matches the original `jobs list` /
  `memberships list` style.
- Everything else is `<resource>-<action>` (CLI) / `st_{module}_{resource}_{action}`
  (MCP).
- Endpoints: their `name` verbatim — `st crm contacts-methods-get` /
  `st_crm_contacts_methods_get`.
- Export feeds: `export-<feed>` / `st_{module}_export_{feed}`; nested feeds flatten
  (`customers/contacts` → `export-customers-contacts`).

## Adding a resource

Check the operation in ServiceTitan's OpenAPI document first (see
[Development → Spec conformance](development.md#spec-conformance)): verb, path,
API version, whether the list is paginated, whether the body is required. Then
add one `Resource(...)` — or an `Endpoint(...)` if it doesn't fit CRUD — to the
right `Module` in `registry.py`. Both front ends pick it up automatically.

```python
# in registry.py, inside the relevant Module(...)
Resource(
    "warranties",          # CLI/tool slug
    ops="LRCUD",           # list, get, create, update, delete
    id_param="warranty_id",
    date_filter=True,      # exposes --range/--from-date/--to-date
    actions=(
        Action("void", help="Void a warranty"),                       # POST .../{id}/void
        Action("bulk-create", needs_id=False, needs_body=True),       # POST .../bulk-create
    ),
),
```

Then run the conformance test and regenerate the coverage doc:

```bash
uv run pytest tests/test_spec_conformance.py
uv run python scripts/gen_api_coverage.py
```

**Only hand-write** a command/tool (in `commands/<module>.py` + `mcp_server.py`)
when it needs logic the generic archetypes can't express — a computed view, a
non-standard request body, or typed list filters you really want. The hand-tuned
groups are the template.

## Shared core modules

| Module | Responsibility |
|--------|----------------|
| `client.py` | httpx `ServiceTitanClient`: `get/post/patch/put/delete`, auth header + `ST-App-Key`, 401-refresh, 429-backoff |
| `auth.py` | OAuth 2.0 Client Credentials, two-tier (memory + disk) token cache |
| `pagination.py` | `fetch_page` / `fetch_all` (page cursors) and `fetch_export_page` / `fetch_export_all` (change-feed tokens) |
| `dates.py` | Human date-range parser; `validate_max_range` enforces caps (e.g. 14 days for capacity) |
| `availability.py` | Pure function: shifts + appointments → per-tech availability rows (`who-busy`) |
| `output.py` | Rich table / JSON rendering (CLI only) |
| `config.py` | `pydantic-settings`, `ST_*` env vars, production/integration environments |
| `registry.py` | Declarative API spec (`Module` / `Resource` / `Action` / `Endpoint`) |
| `engine.py` | Generates Typer commands + FastMCP tools from the registry |

Every API call follows `/{module}/{version}/tenant/{tenant_id}/{resource}` —
`v2` everywhere except the few `v3`-only endpoints.

---

← [MCP server](mcp-server.md) · [Docs index](README.md) · [Development →](development.md)

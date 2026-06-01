# Usage

Shared mechanics for every `st` command. For per-module commands see the
[CLI reference](cli-reference.md) and the full [API coverage](api-coverage.md).

## Quick start

```bash
# 1. Configure (see Configuration)
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

## Global options

```text
st [--json] [--env PATH] COMMAND [ARGS]
```

| Option   | Description                                       |
|----------|---------------------------------------------------|
| `--json` | Output raw JSON instead of a rich table           |
| `--env`  | Path to a `.env` file (overrides default lookup)  |

A handful of commands (e.g. `dispatch capacity`) also accept a local `--json`
flag at the end for ergonomics.

## Date ranges

Date-filterable commands accept `--range`, `--from-date`, and `--to-date`.
Explicit dates win over `--range`.

| Range                                              | Resolves to            |
|----------------------------------------------------|------------------------|
| `today` / `yesterday` / `tomorrow`                 | One-day window         |
| `last-7-days` / `last-30-days` / `last-90-days`    | Rolling N-day window   |
| `this-week` / `last-week` / `next-week`            | Mon–Sun                |
| `this-month` / `last-month` / `next-month`         | Calendar month         |
| `this-quarter` / `last-quarter` / `next-quarter`   | Calendar quarter       |
| `this-year` / `last-year`                          | Calendar year          |
| `2025-03-15`                                       | Single date            |
| `2025-01-01:2025-03-31`                            | Explicit `start:end`   |

> Dispatch endpoints filter on `startsOnOrAfter` / `startsBefore`; other modules
> use `createdOnOrAfter` / `createdBefore`. The CLI handles the mapping for you.

## Pagination

Standard list commands support:

| Option         | Default | Description                       |
|----------------|---------|-----------------------------------|
| `--page`       | 1       | Page number                       |
| `--page-size`  | 50      | Items per page                    |
| `--all`        | off     | Auto-paginate through every page  |

```bash
st crm customers-list --page 3 --page-size 25
st jobs list --all --range this-month
```

## Filtering generated list commands

Generated list commands (everything outside the seven hand-tuned groups) take a
repeatable `--filter key=value` instead of typed per-field options. Values are
coerced to bool/int where obvious:

```bash
st pricebook services-list --filter active=true --filter categoryId=5
st inventory purchase-orders-list --filter businessUnitId=3 --range this-month
```

The hand-tuned groups keep their typed filters (`--name`, `--status`, etc.) — see
the [CLI reference](cli-reference.md).

## Export change-feeds

Modules with an `Export` change-feed expose `export-<feed>` commands. They stream
the whole dataset and print a `continueFrom` token you can pass back later to
fetch only newer changes:

```bash
st telecom export-calls --all --json        # drain the whole feed
st jpm export-jobs --from "<token>"          # resume from a saved token
st jpm export-jobs --max 500                 # stop after N records
```

---

← [Configuration](configuration.md) · [Docs index](README.md) · [CLI reference →](cli-reference.md)

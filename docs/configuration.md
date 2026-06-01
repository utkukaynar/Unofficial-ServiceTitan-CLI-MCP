# Configuration

Create a `.env` file in the working directory (or pass `--env <path>` to any
command):

```dotenv
ST_CLIENT_ID=your-client-id
ST_CLIENT_SECRET=your-client-secret
ST_APP_KEY=your-app-key
ST_TENANT_ID=123456789
ST_ENVIRONMENT=production       # or "integration"
```

## Variables

| Variable           | Required | Description                              |
|--------------------|----------|------------------------------------------|
| `ST_CLIENT_ID`     | Yes      | OAuth 2.0 client ID                      |
| `ST_CLIENT_SECRET` | Yes      | OAuth 2.0 client secret                  |
| `ST_APP_KEY`       | Yes      | ServiceTitan application key             |
| `ST_TENANT_ID`     | Yes      | Your ServiceTitan tenant (account) ID    |
| `ST_ENVIRONMENT`   | No       | `production` (default) or `integration`  |

Config is loaded by `pydantic-settings`; any of these can also be set as real
environment variables (the `ST_` prefix is required either way).

## Environments

| Environment   | Auth URL                                                  | API Base URL                              |
|---------------|-----------------------------------------------------------|-------------------------------------------|
| `production`  | `https://auth.servicetitan.io/connect/token`              | `https://api.servicetitan.io`             |
| `integration` | `https://auth-integration.servicetitan.io/connect/token`  | `https://api-integration.servicetitan.io` |

## Authentication & token caching

OAuth 2.0 Client Credentials, handled automatically:

- Tokens are cached **in-memory** for the process lifetime and **on disk** at
  `~/.st_cli/token_cache.json`.
- Refreshed ~60s before expiry.
- On `401` the client refreshes the token and retries once.
- On `429` it backs off exponentially (up to 3 retries).

## Rate limits (ServiceTitan)

- **60 calls/second per application per tenant** for all APIs (default; higher on
  request).
- **Reporting: 1 of the same report per minute per tenant** — much stricter, so
  cache report results. See [CLI reference → Reporting](cli-reference.md#reporting).

> ⚠️ Keep `ST_APP_KEY` / `ST_CLIENT_SECRET` with you — this is a **Customer-Built
> App**. Don't hand credentials to a third party to run on your behalf (the
> disallowed "Tunneled App" pattern). See the [README](../README.md#intended-integration-path-customer-built-apps-only).

---

← [Installation](installation.md) · [Docs index](README.md) · [Usage →](usage.md)

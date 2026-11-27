# ServiceTitan API Terms

Calling the ServiceTitan API — through this tool or any other — is governed by
ServiceTitan's **[API Terms of Use](https://www.servicetitan.com/legal/api-terms)**
(last updated April 15, 2026 at the time of writing), alongside your ServiceTitan
customer agreement and the general
[Terms of Use](https://www.servicetitan.com/legal/terms-of-use). This page points
out the clauses that matter most for a self-hosted CLI and MCP server.

> **This is not legal advice, and it is not a substitute for reading the terms.**
> The terms change; the section numbers below refer to the April 15, 2026
> version. If anything here disagrees with the terms, the terms win. If you're
> unsure whether your use is allowed, ask ServiceTitan
> (integrations@servicetitan.com) or your counsel.

## Using `st-mcp` with an AI agent (§3.4)

This is the clause most likely to affect you. The API Terms define an
**AI System** broadly — bots, RPA, and AI, agentic or otherwise — and:

- an AI System must not independently decide which API endpoints to call, what
  data to request or change, or what actions to take; calls must be limited to
  predefined operations within your application's certified scope;
- using an AI System with the APIs **requires disclosure to ServiceTitan and its
  approval**; the terms treat undisclosed use as a material breach.

`st-mcp` hands an AI model a catalogue of ~600 tools and lets it choose — the
pattern this clause describes. **Before connecting `st-mcp` to a tenant with real
data, disclose it to ServiceTitan and get approval in writing.** The tools are
tagged `read` / `write` (see [MCP server](mcp-server.md)) to help you scope what
you ask approval for.

## Your app, your keys (§2.2, §2.3)

- Access the API only through the integration environment ServiceTitan
  provisions for you, and only for tenants you own (a "Custom Application").
- Never use credentials issued to someone else, and don't give a third party
  access to your account or credentials.
- Report a lost or compromised credential to security@servicetitan.com
  immediately.

This is why the [README](../README.md#intended-integration-path-customer-built-apps-only)
limits this repo to the **Customer-Built App** path and warns against tunneling.

## Data you pull out (§5.2–§5.4)

- Don't store or cache API content for **longer than 24 hours**, unless the terms
  or documentation expressly allow it, and delete it within 24 hours of a written
  request from ServiceTitan.
- `st` doesn't persist API responses itself (it only caches the OAuth token, in
  `~/.st_cli/token_cache.json`). Anything you save — `--json` output, export-feed
  dumps — is your responsibility to expire.

## Rate limits (§3.4)

Don't exceed or work around rate limits or quotas. The client backs off and
retries on HTTP 429; don't parallelise around that. Reporting has its own,
stricter limit (one run of the same report per minute per tenant).

## API documentation is confidential (§9.1)

The terms list information related to the APIs and their documentation as
ServiceTitan confidential information. That's why this repo **does not include**
ServiceTitan's OpenAPI documents: the spec conformance test reads them from a
local, gitignored `specs/` folder that you download yourself with your own
developer-portal login (see [Development](development.md#spec-conformance)).

## Name and affiliation (§6.2–§6.3)

This project is not affiliated with or endorsed by ServiceTitan, Inc. Don't
describe your use of it as a ServiceTitan "partner" integration, and don't
publicise an integration with ServiceTitan without their written consent.

## Open-source licensing (§3.4)

The terms prohibit using the APIs in a way that subjects the API or the
ServiceTitan Platform to an open-source license. This repository contains client
code only — no ServiceTitan API, platform code, or documentation — and currently
carries no open-source license. If you fork or redistribute it, read this clause
first.

## Security incidents (§7.2)

If a security incident involves your use of the API, notify
security@servicetitan.com **within 24 hours** of becoming aware of it.

## Other documents

- [API Terms of Use](https://www.servicetitan.com/legal/api-terms)
- [Terms of Use](https://www.servicetitan.com/legal/terms-of-use)
- [App Marketplace Program Guide](https://www.servicetitan.com/legal/app-marketplace-program-guide)
  — the route if you want to distribute a tool like this to other customers
- [Customer Integration Paths](https://developer.servicetitan.io/integration-paths)

---

← [MCP server](mcp-server.md) · [Docs index](README.md)

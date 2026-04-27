# st-cli Usage Guide

A CLI tool and MCP server for the ServiceTitan REST API v2. Two interfaces to the same API:

- **`st` CLI** -- Typer-based command-line tool with rich table or JSON output
- **`st-mcp` MCP server** -- FastMCP server exposing the same operations as tools for AI agents

---

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Global Options](#global-options)
- [Date Ranges](#date-ranges)
- [Pagination](#pagination)
- [Commands](#commands)
  - [CRM](#crm)
  - [Jobs](#jobs)
  - [Dispatch](#dispatch)
  - [Accounting](#accounting)
  - [Memberships](#memberships)
  - [Reporting](#reporting)
- [MCP Server](#mcp-server)
- [Examples](#examples)

---

## Installation

```bash
# Editable install with dev dependencies
pip install -e ".[dev]"

# Verify
st --help
```

---

## Configuration

Create a `.env` file with the following variables:

```dotenv
ST_CLIENT_ID=your-client-id
ST_CLIENT_SECRET=your-client-secret
ST_APP_KEY=your-app-key
ST_TENANT_ID=123456789
ST_ENVIRONMENT=production   # or "integration"
```

| Variable           | Required | Description                              |
|--------------------|----------|------------------------------------------|
| `ST_CLIENT_ID`     | Yes      | OAuth 2.0 client ID                      |
| `ST_CLIENT_SECRET` | Yes      | OAuth 2.0 client secret                  |
| `ST_APP_KEY`       | Yes      | ServiceTitan application key             |
| `ST_TENANT_ID`     | Yes      | Your ServiceTitan tenant (account) ID    |
| `ST_ENVIRONMENT`   | No       | `production` (default) or `integration`  |

### Environments

| Environment   | Auth URL                                                    | API Base URL                          |
|---------------|-------------------------------------------------------------|---------------------------------------|
| `production`  | `https://auth.servicetitan.io/connect/token`                | `https://api.servicetitan.io`         |
| `integration` | `https://auth-integration.servicetitan.io/connect/token`    | `https://api-integration.servicetitan.io` |

### Authentication

Authentication is handled automatically via OAuth 2.0 Client Credentials. Tokens are cached in two tiers:

1. **In-memory** -- for the duration of the process
2. **File-based** -- at `~/.st_cli/token_cache.json`, persists across invocations

Tokens are refreshed automatically 60 seconds before expiry. On a 401 response, the client auto-refreshes and retries. On 429 (rate limit), exponential backoff is applied.

---

## Global Options

These options apply to every command:

```
st [OPTIONS] COMMAND [ARGS]
```

| Option    | Type   | Default | Description                           |
|-----------|--------|---------|---------------------------------------|
| `--json`  | Flag   | Off     | Output raw JSON instead of a table    |
| `--env`   | Path   | None    | Path to a `.env` file for config      |

**Examples:**

```bash
# Use a custom .env file
st --env /path/to/.env crm customers-list

# Get JSON output
st --json jobs list --range today
```

---

## Date Ranges

Many commands accept `--range`, `--from-date`, and `--to-date` to filter by date. The `--range` option supports human-friendly strings:

| Range              | Description                              |
|--------------------|------------------------------------------|
| `today`            | Current day                              |
| `yesterday`        | Previous day                             |
| `tomorrow`         | Next day                                 |
| `last-7-days`      | Past 7 days                              |
| `last-30-days`     | Past 30 days                             |
| `last-90-days`     | Past 90 days                             |
| `this-week`        | Current week (Monday--Sunday)            |
| `last-week`        | Previous week                            |
| `next-week`        | Next week                                |
| `this-month`       | Current calendar month                   |
| `last-month`       | Previous calendar month                  |
| `next-month`       | Next calendar month                      |
| `this-quarter`     | Current quarter                          |
| `last-quarter`     | Previous quarter                         |
| `next-quarter`     | Next quarter                             |
| `this-year`        | Current calendar year                    |
| `last-year`        | Previous calendar year                   |
| `2025-01-15`       | Single specific date                     |
| `2025-01-01:2025-01-31` | Explicit date range                |

You can also use `--from-date` and `--to-date` directly with `YYYY-MM-DD` dates for full control.

> **Note:** Dispatch commands filter on `startsOnOrAfter`/`startsBefore`, while other modules filter on `createdOnOrAfter`/`createdBefore`.

---

## Pagination

List commands support pagination with these options:

| Option         | Type | Default | Description                      |
|----------------|------|---------|----------------------------------|
| `--page`       | Int  | 1       | Page number to fetch             |
| `--page-size`  | Int  | 50      | Number of items per page         |
| `--all`        | Flag | Off     | Auto-paginate through all pages  |

```bash
# Get page 3 with 25 items per page
st crm customers-list --page 3 --page-size 25

# Fetch everything (auto-paginate)
st jobs list --all --range this-month
```

---

## Commands

### CRM

Customer Relationship Management -- customers, locations, bookings, and contacts.

#### `st crm customers-list`

List customers with optional filters.

```
st crm customers-list [OPTIONS]
```

| Option         | Type   | Description              |
|----------------|--------|--------------------------|
| `--name`       | Text   | Filter by customer name  |
| `--email`      | Text   | Filter by email          |
| `--phone`      | Text   | Filter by phone          |
| `--page`       | Int    | Page number (default: 1) |
| `--page-size`  | Int    | Page size (default: 50)  |
| `--all`        | Flag   | Fetch all pages          |

```bash
st crm customers-list --name "John"
st crm customers-list --all --json
```

#### `st crm customers-get`

Get a single customer by ID.

```bash
st crm customers-get 12345
```

#### `st crm customers-create`

Create a new customer.

```
st crm customers-create --name TEXT [--data TEXT]
```

| Option   | Required | Description                        |
|----------|----------|------------------------------------|
| `--name` | Yes      | Customer name                      |
| `--data` | No       | Additional fields as JSON string   |

```bash
st crm customers-create --name "Jane Doe"
st crm customers-create --name "Jane Doe" --data '{"type": "Residential"}'
```

#### `st crm customers-update`

Update an existing customer.

```
st crm customers-update CUSTOMER_ID [--name TEXT] [--data TEXT]
```

```bash
st crm customers-update 12345 --name "Jane Smith"
st crm customers-update 12345 --data '{"email": "jane@example.com"}'
```

#### `st crm locations-list`

List customer locations.

```
st crm locations-list [--page INT] [--page-size INT] [--all]
```

#### `st crm locations-get`

Get a single location by ID.

```bash
st crm locations-get 67890
```

#### `st crm bookings-list`

List bookings.

```
st crm bookings-list [--page INT] [--page-size INT] [--all]
```

#### `st crm bookings-get`

Get a single booking by ID.

```bash
st crm bookings-get 11111
```

#### `st crm bookings-create`

Create a new booking.

```
st crm bookings-create --data TEXT
```

| Option   | Required | Description                |
|----------|----------|----------------------------|
| `--data` | Yes      | Booking data as JSON       |

```bash
st crm bookings-create --data '{"source": "Phone", "customerId": 12345}'
```

#### `st crm bookings-update`

Update an existing booking.

```
st crm bookings-update BOOKING_ID --data TEXT
```

```bash
st crm bookings-update 11111 --data '{"status": "Confirmed"}'
```

#### `st crm contacts-list`

List contacts.

```
st crm contacts-list [--page INT] [--page-size INT] [--all]
```

#### `st crm contacts-get`

Get a single contact by ID.

```bash
st crm contacts-get 22222
```

---

### Jobs

Job and project management -- jobs, appointments, and projects.

#### `st jobs list`

List jobs with optional filters.

```
st jobs list [OPTIONS]
```

| Option          | Type   | Description                        |
|-----------------|--------|------------------------------------|
| `--status`      | Text   | Filter by job status               |
| `--range`       | Text   | Date range (e.g., `last-week`)     |
| `--from-date`   | Text   | Created on or after (YYYY-MM-DD)   |
| `--to-date`     | Text   | Created before (YYYY-MM-DD)        |
| `--customer-id` | Int    | Filter by customer ID              |
| `--page`        | Int    | Page number (default: 1)           |
| `--page-size`   | Int    | Page size (default: 50)            |
| `--all`         | Flag   | Fetch all pages                    |

```bash
st jobs list --range this-week
st jobs list --status "Completed" --all --json
st jobs list --customer-id 12345 --range last-month
```

#### `st jobs get`

Get a single job by ID.

```bash
st jobs get 33333
```

#### `st jobs create`

Create a new job.

```
st jobs create --data TEXT
```

```bash
st jobs create --data '{"customerId": 12345, "typeId": 1}'
```

#### `st jobs update`

Update an existing job.

```
st jobs update JOB_ID --data TEXT
```

```bash
st jobs update 33333 --data '{"priority": "High"}'
```

#### `st jobs cancel`

Cancel a job.

```bash
st jobs cancel 33333
```

#### `st jobs appointments-list`

List appointments.

```
st jobs appointments-list [--job-id INT] [--page INT] [--page-size INT]
```

| Option     | Type | Description            |
|------------|------|------------------------|
| `--job-id` | Int  | Filter by job ID       |

```bash
st jobs appointments-list --job-id 33333
```

#### `st jobs appointments-get`

Get a single appointment by ID.

```bash
st jobs appointments-get 44444
```

#### `st jobs projects-list`

List projects.

```
st jobs projects-list [--page INT] [--page-size INT]
```

#### `st jobs projects-get`

Get a single project by ID.

```bash
st jobs projects-get 55555
```

---

### Dispatch

Dispatch operations -- shifts, assignments, technician availability, and events.

#### `st dispatch shifts-list`

List technician shifts.

```
st dispatch shifts-list [OPTIONS]
```

| Option        | Type   | Description                          |
|---------------|--------|--------------------------------------|
| `--range`     | Text   | Date range (e.g., `today`)           |
| `--from-date` | Text   | Starts on or after (YYYY-MM-DD)      |
| `--to-date`   | Text   | Starts before (YYYY-MM-DD)           |
| `--page`      | Int    | Page number (default: 1)             |
| `--page-size` | Int    | Page size (default: 50)              |
| `--all`       | Flag   | Fetch all pages                      |

```bash
st dispatch shifts-list --range today
st dispatch shifts-list --from-date 2025-03-01 --to-date 2025-03-31 --all
```

#### `st dispatch assignments-list`

List dispatch assignments.

```
st dispatch assignments-list [OPTIONS]
```

| Option            | Type | Description              |
|-------------------|------|--------------------------|
| `--technician-id` | Int  | Filter by technician ID  |
| `--page`          | Int  | Page number (default: 1) |
| `--page-size`     | Int  | Page size (default: 50)  |
| `--all`           | Flag | Fetch all pages          |

```bash
st dispatch assignments-list --technician-id 99999
```

#### `st dispatch who-busy`

Show technician availability: shifts, booked hours, available hours, and percentage booked.

```
st dispatch who-busy [OPTIONS]
```

| Option        | Type   | Default | Description                      |
|---------------|--------|---------|----------------------------------|
| `--range`     | Text   | `today` | Date range                       |
| `--from-date` | Text   | None    | Starts on or after (YYYY-MM-DD)  |
| `--to-date`   | Text   | None    | Starts before (YYYY-MM-DD)       |

Output columns: Technician ID, Name, Shifts, Shift Hours, Appointments, Booked Hours, Available Hours, % Booked.

```bash
st dispatch who-busy
st dispatch who-busy --range this-week
st dispatch who-busy --json
```

#### `st dispatch events-list`

List dispatch events.

```
st dispatch events-list [--page INT] [--page-size INT]
```

#### `st dispatch events-create`

Create a dispatch event.

```
st dispatch events-create --data TEXT
```

```bash
st dispatch events-create --data '{"technicianId": 99999, "type": "Break"}'
```

---

### Accounting

Invoices, estimates, and payments.

#### `st accounting invoices-list`

List invoices with optional filters.

```
st accounting invoices-list [OPTIONS]
```

| Option        | Type   | Description                        |
|---------------|--------|------------------------------------|
| `--status`    | Text   | Filter by invoice status           |
| `--range`     | Text   | Date range (e.g., `this-month`)    |
| `--from-date` | Text   | Created on or after (YYYY-MM-DD)   |
| `--to-date`   | Text   | Created before (YYYY-MM-DD)        |
| `--page`      | Int    | Page number (default: 1)           |
| `--page-size` | Int    | Page size (default: 50)            |
| `--all`       | Flag   | Fetch all pages                    |

```bash
st accounting invoices-list --range this-month --status "Posted"
st accounting invoices-list --all --json
```

#### `st accounting invoices-get`

Get a single invoice by ID.

```bash
st accounting invoices-get 66666
```

#### `st accounting estimates-list`

List estimates with optional filters.

```
st accounting estimates-list [OPTIONS]
```

| Option        | Type   | Description                        |
|---------------|--------|------------------------------------|
| `--status`    | Text   | Filter by estimate status          |
| `--range`     | Text   | Date range                         |
| `--from-date` | Text   | Created on or after (YYYY-MM-DD)   |
| `--to-date`   | Text   | Created before (YYYY-MM-DD)        |
| `--page`      | Int    | Page number (default: 1)           |
| `--page-size` | Int    | Page size (default: 50)            |
| `--all`       | Flag   | Fetch all pages                    |

```bash
st accounting estimates-list --range last-quarter
```

#### `st accounting estimates-get`

Get a single estimate by ID.

```bash
st accounting estimates-get 77777
```

#### `st accounting payments-list`

List payments.

```
st accounting payments-list [OPTIONS]
```

| Option        | Type   | Description                        |
|---------------|--------|------------------------------------|
| `--range`     | Text   | Date range                         |
| `--from-date` | Text   | Created on or after (YYYY-MM-DD)   |
| `--to-date`   | Text   | Created before (YYYY-MM-DD)        |
| `--page`      | Int    | Page number (default: 1)           |
| `--page-size` | Int    | Page size (default: 50)            |
| `--all`       | Flag   | Fetch all pages                    |

```bash
st accounting payments-list --range this-month --json
```

---

### Memberships

Membership management.

#### `st memberships list`

List memberships.

```
st memberships list [--page INT] [--page-size INT] [--all]
```

```bash
st memberships list --all
```

#### `st memberships get`

Get a single membership by ID.

```bash
st memberships get 88888
```

#### `st memberships types-list`

List membership types.

```
st memberships types-list [--page INT] [--page-size INT]
```

```bash
st memberships types-list
```

---

### Reporting

Run ServiceTitan reports programmatically. Reports are organized into categories, each containing one or more reports with specific fields and parameters.

> **Rate limit:** 5 calls per minute per report per tenant.

#### `st reporting categories`

List available report categories.

```
st reporting categories [--page INT] [--page-size INT]
```

```bash
st reporting categories
```

#### `st reporting reports`

List reports within a category.

```
st reporting reports CATEGORY_ID [--page INT] [--page-size INT]
```

```bash
st reporting reports 1
```

#### `st reporting fields`

Show a report's fields and required parameters (metadata). Use this to discover what parameters a report accepts before fetching data.

```
st reporting fields CATEGORY_ID REPORT_ID
```

```bash
st reporting fields 1 42
```

#### `st reporting data`

Fetch report data.

```
st reporting data CATEGORY_ID REPORT_ID [OPTIONS]
```

| Option        | Type   | Description                                            |
|---------------|--------|--------------------------------------------------------|
| `--from`      | Text   | From date (YYYY-MM-DD)                                 |
| `--to`        | Text   | To date (YYYY-MM-DD)                                   |
| `--params`    | Text   | Extra params as JSON, e.g. `'[{"name":"X","value":"Y"}]'` |
| `--page`      | Int    | Page number (default: 1)                               |
| `--page-size` | Int    | Page size (default: 50)                                |
| `--all`       | Flag   | Fetch all pages                                        |

```bash
# Fetch a report for a date range
st reporting data 1 42 --from 2025-01-01 --to 2025-01-31

# With extra parameters
st reporting data 1 42 --from 2025-03-01 --to 2025-03-31 \
  --params '[{"name": "TechnicianId", "value": "99999"}]'

# All pages as JSON
st reporting data 1 42 --from 2025-01-01 --to 2025-03-31 --all --json
```

---

## MCP Server

The MCP server exposes the same operations as tools for AI agents over stdio transport.

### Running the MCP Server

```bash
st-mcp
```

### MCP Pagination

MCP tools use a slightly different pagination model:

| Parameter      | Type | Default | Description                                   |
|----------------|------|---------|-----------------------------------------------|
| `page`         | Int  | None    | Fetch a specific page                         |
| `page_size`    | Int  | 50      | Items per page                                |
| `max_results`  | Int  | 200     | Auto-pagination limit (hard cap: 1000)        |

When `page` is not set, the server auto-paginates up to `max_results` items.

### Available Tools

All tools follow the naming convention `st_{module}_{resource}_{action}`.

| Tool                             | Description                              |
|----------------------------------|------------------------------------------|
| `st_crm_customers_list`         | List customers (filters: name, email, phone) |
| `st_crm_customers_get`          | Get customer by ID                       |
| `st_crm_customers_create`       | Create a customer                        |
| `st_crm_customers_update`       | Update a customer                        |
| `st_crm_locations_list`         | List locations                           |
| `st_crm_locations_get`          | Get location by ID                       |
| `st_crm_bookings_list`          | List bookings                            |
| `st_crm_bookings_get`           | Get booking by ID                        |
| `st_crm_bookings_create`        | Create a booking                         |
| `st_crm_bookings_update`        | Update a booking                         |
| `st_crm_contacts_list`          | List contacts                            |
| `st_crm_contacts_get`           | Get contact by ID                        |
| `st_jpm_jobs_list`              | List jobs (filters: status, customer_id, date_range) |
| `st_jpm_jobs_get`               | Get job by ID                            |
| `st_jpm_jobs_create`            | Create a job                             |
| `st_jpm_jobs_update`            | Update a job                             |
| `st_jpm_jobs_cancel`            | Cancel a job                             |
| `st_jpm_appointments_list`      | List appointments                        |
| `st_jpm_appointments_get`       | Get appointment by ID                    |
| `st_jpm_projects_list`          | List projects                            |
| `st_jpm_projects_get`           | Get project by ID                        |
| `st_dispatch_shifts_list`       | List shifts (date filters)               |
| `st_dispatch_assignments_list`  | List assignments (filter: technician_id) |
| `st_dispatch_who_busy`          | Technician availability summary          |
| `st_dispatch_events_list`       | List dispatch events                     |
| `st_dispatch_events_create`     | Create a dispatch event                  |
| `st_accounting_invoices_list`   | List invoices (filters: status, dates)   |
| `st_accounting_invoices_get`    | Get invoice by ID                        |
| `st_accounting_estimates_list`  | List estimates (filters: status, dates)  |
| `st_accounting_estimates_get`   | Get estimate by ID                       |
| `st_accounting_payments_list`   | List payments (date filters)             |
| `st_memberships_list`           | List memberships                         |
| `st_memberships_get`            | Get membership by ID                     |
| `st_memberships_types_list`     | List membership types                    |
| `st_reporting_categories_list`  | List report categories                   |
| `st_reporting_reports_list`     | List reports in a category               |
| `st_reporting_report_fields`    | Get report field metadata                |
| `st_reporting_report_data`      | Fetch report data                        |

### Error Handling

MCP tools map CLI errors to `ToolError` responses:

| CLI Exception        | MCP Behavior            |
|----------------------|-------------------------|
| `AuthenticationError`| Returns `ToolError`     |
| `APIError`           | Returns `ToolError`     |
| `ConfigError`        | Returns `ToolError`     |

---

## Examples

### Quick Start

```bash
# 1. Set up your .env file
cat > .env << 'EOF'
ST_CLIENT_ID=my-client-id
ST_CLIENT_SECRET=my-secret
ST_APP_KEY=my-app-key
ST_TENANT_ID=123456789
ST_ENVIRONMENT=production
EOF

# 2. Install
pip install -e ".[dev]"

# 3. List customers
st crm customers-list

# 4. Get today's jobs as JSON
st --json jobs list --range today
```

### Common Workflows

```bash
# Check technician availability for this week
st dispatch who-busy --range this-week

# Pull all invoices from last month as JSON
st --json accounting invoices-list --range last-month --all

# Look up a specific customer and their jobs
st crm customers-get 12345
st jobs list --customer-id 12345 --range this-year

# Explore available reports
st reporting categories
st reporting reports 1
st reporting fields 1 42
st reporting data 1 42 --from 2025-01-01 --to 2025-03-31

# Use a different environment
st --env staging.env dispatch shifts-list --range today
```

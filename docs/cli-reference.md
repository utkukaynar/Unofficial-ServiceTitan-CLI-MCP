# CLI reference

This page documents the **seven hand-tuned command groups** in depth (they carry
typed filters and bespoke commands). For the full list of every command across
all 24 modules, see [API coverage](api-coverage.md). For shared options
(`--json`, date ranges, pagination, `--filter`), see [Usage](usage.md).

> **Two groups gained/lost commands to fix routing bugs:** estimates moved from
> `accounting` to [`salestech`](api-coverage.md#salestech), and job types moved
> from `settings` to [`jobs`](#jobs) (`st jobs job-types-list`). The old
> misrouted commands were removed.

## CRM

Customers, locations, bookings, contacts, leads.

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

Generated additions: `customers-delete`, `locations-create/update/delete`,
`contacts-create/update/delete`, `leads-*` (with `dismiss`/`follow-up`),
`booking-provider-tags-*`, and `export-{customers,locations,bookings}`. See
[API coverage → crm](api-coverage.md#crm).

## Jobs

Jobs, appointments, projects, job types (the `jpm` module).

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

st jobs job-types-list   # moved here from `settings`
```

Generated additions include appointment lifecycle actions
(`appointments-reschedule/hold/remove-hold/confirm/remove-confirmation`),
`projects-create/update` (+ `note`, `attach-job`), `budget-codes-*`, and
`export-{jobs,appointments,projects}`. See [API coverage → jobs](api-coverage.md#jobs).

## Dispatch

Shifts, assignments, who's busy, events, zones, teams, capacity, skills, arrival
windows.

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

The `capacity` response renders one row per availability time frame, with
start/end, business units, total/open hours, and the `isAvailable` /
`isExceedingIdealBookingPercentage` flags from the API.

Generated additions: assignment actions (`assignments-assign-technicians` /
`unassign-technicians`), full CRUD for shifts/zones/teams/events, `skills-*`,
`arrival-windows-*` (+ `activate`), `business-hours-*`, and export feeds. See
[API coverage → dispatch](api-coverage.md#dispatch).

## Accounting

Invoices, payments, GL accounts, journal entries, AP bills/credits/payments.

```bash
st accounting invoices-list  [--status] [--range] [--from-date] [--to-date] [--page] [--page-size] [--all]
st accounting invoices-get   INVOICE_ID

st accounting payments-list  [--range] [--from-date] [--to-date] [--page] [--page-size] [--all]
```

> **Estimates moved.** Estimates live in the `salestech` module, not `accounting`
> — use `st salestech estimates-list` / `estimates-get`. The old
> `accounting estimates-*` commands hit a non-existent endpoint and were removed.

Generated additions: `invoices-update` / `invoices-mark-exported`,
`payments-get/update/update-status`, `gl-accounts-*`, `journal-entries-*`,
`credit-memos-*`, `ap-bills/ap-credits/ap-payments/inventory-bills-*`,
`bank-deposits-*`, and read-only reference data (`payment-terms`,
`payment-types`, `tax-zones`). See [API coverage → accounting](api-coverage.md#accounting).

## Memberships

```bash
st memberships list       [--page] [--page-size] [--all]
st memberships get        MEMBERSHIP_ID
st memberships types-list [--page] [--page-size]
```

Generated additions: `create`/`update`, `invoice-templates-*`,
`recurring-services-*`, `recurring-service-events-*` (+ `mark-complete` /
`mark-incomplete`), and export feeds. See
[API coverage → memberships](api-coverage.md#memberships).

## Reporting

Run ServiceTitan reports programmatically. **Rate limit: 1 of the same report per
minute per tenant** (far stricter than the general 60 calls/sec — cache results).

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

## Settings

```bash
st settings business-units-list [--active/--no-active] [--page] [--page-size] [--all]
```

> **Job types moved.** Job types live in the `jpm` module, not `settings` — use
> `st jobs job-types-list`. The old `settings job-types-list` command hit a
> non-existent endpoint and was removed.

Generated additions: `business-units-update`, `employees-*` and `technicians-*`
(each with `activate` / `deactivate`), `tag-types-*`, `user-roles-*`, and export
feeds. See [API coverage → settings](api-coverage.md#settings).

## Everything else (generated)

The other 17 modules — pricebook, inventory, salestech, payroll, marketing,
marketing-ads, timesheets, equipment-systems, findings, task-management, telecom,
customer-interactions, forms, job-booking, marketing-reputation, scheduling-pro,
service-agreements — are generated from the registry with uniform command names:

```bash
st <module> <resource>-list   [--filter key=value ...] [--range|--from-date|--to-date] [--page|--page-size|--all]
st <module> <resource>-get    RECORD_ID
st <module> <resource>-create --data JSON
st <module> <resource>-update RECORD_ID --data JSON
st <module> <resource>-delete RECORD_ID
st <module> <resource>-<action> [RECORD_ID] [--data JSON]   # domain actions
st <module> export-<feed>     [--from TOKEN] [--max N] [--all]   # change-feeds
```

A few high-value examples:

```bash
st salestech estimates-sell 12345 --data '{"soldBy": 99}'
st inventory purchase-orders-approve 678
st pricebook services-create --data '{"code": "AC-TUNE", "displayName": "AC Tune-Up", "price": 129}'
st jobs appointments-reschedule 555 --data '{"start": "2026-06-01T09:00:00", "end": "2026-06-01T11:00:00"}'
st telecom export-calls --all --json
```

Run `st <module> --help` to list a group's commands, or browse the full
[API coverage](api-coverage.md).

---

← [Usage](usage.md) · [Docs index](README.md) · [Examples & recipes →](examples.md)

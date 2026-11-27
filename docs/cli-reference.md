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

st crm contacts-list   [--page] [--page-size] [--all]
st crm contacts-get    CONTACT_ID            # a GUID string
```

Bookings are created and updated **through a booking provider** — ServiceTitan
has no tenant-level create/update — so those are the generated
`provider-bookings-*` commands (`st crm provider-bookings-create PROVIDER_ID --data JSON`).

Generated additions: `locations-create/update`, contacts CRUD and contact
methods/preferences/relationships (`contacts-*`), customer and location notes,
contacts and tags (`customers-notes-list`, `locations-contacts-create`,
`customers-tag-add`, …), custom fields, `leads-*` (with `dismiss`/`follow-up`/
`note`, plus `leads-create-v3`), `booking-provider-tags-*`, and export feeds
including `export-customers-contacts`. See [API coverage → crm](api-coverage.md#crm).

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

`st jobs cancel JOB_ID --reason-id N --memo TEXT` cancels a job; reason IDs come
from `st jobs job-cancel-reasons-list`.

Generated additions include appointment lifecycle actions
(`appointments-reschedule/hold/remove-hold/confirm/remove-confirmation/
special-instructions/summary`), job notes, history, equipment and
`job-remove-cancellation`, `projects-create/update/note` plus
`projects-attach-job` / `projects-detach-job`, project daily logs, project
statuses/sub-statuses/types, the work-breakdown-structure budget codes
(`budget-codes-*`, `wbs-*`), and seven export feeds. See
[API coverage → jobs](api-coverage.md#jobs).

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
`unassign-technicians`), shifts (+ `shifts-bulk-delete`), zones, teams, events
(non-job appointments — `events-replace` is a full PUT), `skills-*`,
`arrival-windows-*` (+ `activate` and configuration), business hours,
`technician-tracking`, GPS pings, and export feeds. See
[API coverage → dispatch](api-coverage.md#dispatch).

## Accounting

Invoices, payments, GL accounts, journal entries, AP bills/credits/payments.

```bash
st accounting invoices-list  [--status] [--range] [--from-date] [--to-date] [--page] [--page-size] [--all]
st accounting invoices-get   INVOICE_ID     # ServiceTitan has no single-invoice route; filters the list by id

st accounting payments-list  [--range] [--from-date] [--to-date] [--page] [--page-size] [--all]
```

> **Estimates moved.** Estimates live in the `salestech` module, not `accounting`
> — use `st salestech estimates-list` / `estimates-get`. The old
> `accounting estimates-*` commands hit a non-existent endpoint and were removed.

Generated additions: adjustment invoices (`invoices-create`), invoice items and
tasks, `payments-update` / `payments-update-status`, `gl-accounts-*`,
`journal-entries-*` (string IDs), `credit-memos-*`, AP bills/credits/payments,
inventory bills, bank deposits, expense transactions, remittance vendors,
`*-custom-fields` / `*-custom-fields-update` and `*-mark-exported` for every
exportable record, reference data (`payment-terms`, `payment-types`,
`tax-zones` + `tax-zones-resolve`), and export feeds. See
[API coverage → accounting](api-coverage.md#accounting).

## Memberships

```bash
st memberships list       [--page] [--page-size] [--all]
st memberships get        MEMBERSHIP_ID
st memberships types-list [--page] [--page-size]
```

Generated additions: `update`, `memberships-sale`, status changes, custom
fields, membership-type details (`membership-types-get`, discounts, billing
options, included recurring services), `invoice-templates-*`,
`recurring-services-*`, `recurring-service-events-*` (+ `mark-complete` /
`mark-incomplete`), and seven export feeds. See
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

`st settings business-units-get BUSINESS_UNIT_ID` fetches one business unit.

Generated additions: `business-units-update`, `business-units-intacct`,
`employees-*` and `technicians-*` (each with `account-action` — `Activate`,
`Deactivate`, `SendInvite`, `SendPasswordResetLink` — and custom fields),
`tag-types-*`, `user-roles-list`, and export feeds. See
[API coverage → settings](api-coverage.md#settings).

## Everything else (generated)

The other 18 modules — pricebook, inventory, salestech, payroll, marketing,
marketing-ads, timesheets, equipment-systems, findings, fleet-pro,
task-management, telecom, customer-interactions, forms, job-booking,
marketing-reputation, scheduling-pro, service-agreements — are generated from the
registry with uniform command names:

```bash
st <module> <resource>-list   [--filter key=value ...] [--range|--from-date|--to-date] [--page|--page-size|--all]
st <module> <resource>-get    RECORD_ID
st <module> <resource>-create --data JSON
st <module> <resource>-update RECORD_ID --data JSON
st <module> <resource>-delete RECORD_ID
st <module> <resource>-replace RECORD_ID --data JSON          # PUT endpoints
st <module> <resource>-<action> [RECORD_ID] [--data JSON]   # domain actions
st <module> <endpoint> [PATH_ARG ...] [--data JSON] [--filter key=value ...]   # path templates
st <module> export-<feed>     [--from TOKEN] [--max N] [--all]   # change-feeds
```

Endpoint-style commands cover nested paths, string IDs and bulk operations; their
`--help` lists the path arguments in order, e.g.
`st crm contacts-methods-get CONTACTID CONTACTMETHODID`.

A few high-value examples:

```bash
st salestech estimates-sell 12345 --data '{"soldBy": 99}'
st inventory purchase-order-requests-approve 678
st pricebook services-create --data '{"code": "AC-TUNE", "displayName": "AC Tune-Up", "price": 129}'
st jobs appointments-reschedule 555 --data '{"start": "2026-06-01T09:00:00", "end": "2026-06-01T11:00:00"}'
st telecom export-calls --all --json
```

Run `st <module> --help` to list a group's commands, or browse the full
[API coverage](api-coverage.md).

---

← [Usage](usage.md) · [Docs index](README.md) · [Examples & recipes →](examples.md)

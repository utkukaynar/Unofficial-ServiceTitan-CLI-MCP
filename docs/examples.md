# Examples & recipes

A broad sample of real commands across **all 25 ServiceTitan modules** — at least
one endpoint per module, with realistic timeframes where the endpoint is
date-filterable. Each block pairs the `st` CLI command with its `st-mcp` tool so
you can use whichever interface fits.

For the full inventory see [API coverage](api-coverage.md); for shared mechanics
(date ranges, pagination, `--filter`) see [Usage](usage.md).

## How to read these

Every generated command has an MCP twin. The mapping is mechanical:

| CLI | MCP tool | MCP args |
|-----|----------|----------|
| `st pricebook services-list --filter active=true` | `st_pricebook_services_list` | `{"filters": {"active": true}}` |
| `st telecom calls-list --range last-7-days` | `st_telecom_calls_list` | `{"date_range": "last-7-days"}` |
| `st findings location-findings-get 123` | `st_findings_location_findings_get` | `{"record_id": 123}` |
| `st crm contacts-methods-get C_ID M_ID` | `st_crm_contacts_methods_get` | `{"path": {"contactId": "C_ID", "contactMethodId": "M_ID"}}` |
| `st jobs export-jobs --from TOKEN` | `st_jpm_export_jobs` | `{"continue_from": "TOKEN"}` |

Notes that hold throughout:

- **List filters:** generated list commands take repeatable `--filter key=value`
  (MCP: a `filters` dict). The seven hand-tuned groups keep typed flags
  (`--name`, `--status`, …).
- **Timeframes:** `--range` accepts `today`, `last-7-days`, `this-month`,
  `last-quarter`, `2025-01-01:2025-03-31`, etc. (MCP: `date_range`). Only
  date-filterable endpoints honor it — they're called out below.
- **Endpoint-style commands** (nested or string IDs, bulk operations) take their
  path parameters positionally, in the order shown by `--help` (MCP: a `path`
  dict keyed by parameter name).
- **MCP module ≠ CLI group in three spots:** the `jobs` CLI group is the `jpm`
  module (`st_jpm_*`), `salestech` is the `sales` module (`st_sales_*`), and
  `job-booking` is `jbce` (`st_jbce_*`).

---

## CRM — `st crm` · `st_crm_*`

Customers, locations, contacts, and (date-filterable) leads.

```bash
# Leads created this week, auto-paginated
st crm leads-list --range this-week --all
st crm leads-get 90210
st crm leads-dismiss 90210
st crm customers-note 4567 --data '{"text":"Called back, left VM"}'

# Bulk sync: drain the customers change-feed, save the token
st crm export-customers --all --json
```

MCP: `st_crm_leads_list {"date_range": "this-week"}` ·
`st_crm_customers_note {"record_id": 4567, "data": {"text": "..."}}` ·
`st_crm_export_customers {}`

## Jobs — `st jobs` · `st_jpm_*`

Jobs, appointments, projects, and **job types** (these live in `jpm`, not
`settings`).

```bash
st jobs list --range this-month --all          # hand-tuned: typed filters
st jobs job-types-list --filter active=true
st jobs appointments-reschedule 55012 --data '{"start":"2026-06-10T15:00:00Z"}'
st jobs export-jobs --max 500                   # change-feed, first 500 records
st jobs export-appointments --from "<token>"    # resume a prior poll
```

MCP: `st_jpm_job_types_list {"filters": {"active": true}}` ·
`st_jpm_export_jobs {"max_records": 500}`

## Dispatch — `st dispatch` · `st_dispatch_*`

Shifts, zones, teams, skills, arrival windows. Dispatch filters on
`startsOnOrAfter`/`startsBefore` — the CLI maps `--range` for you.

```bash
st dispatch who-busy --range this-week          # hand-tuned availability view
st dispatch capacity --range this-week --bu-ids 1,2
st dispatch zones-get 7
st dispatch assignments-assign-technicians --data '{"jobAppointmentId":1,"technicianIds":[10,11]}'
st dispatch arrival-windows-activate 3 --data '{"isActive": true}'
st dispatch skills-get 6f1c…                    # technician-skill ids are strings
```

MCP: `st_dispatch_zones_get {"record_id": 7}` ·
`st_dispatch_assignments_assign_technicians {"data": {...}}`

## Accounting — `st accounting` · `st_accounting_*`

Invoices, payments, GL, journal entries, AP. (Estimates are **not** here — see
Sales below.)

```bash
st accounting invoices-list --range last-month --status Posted   # hand-tuned filters
st accounting payments-update 8800 --data '{"memo":"Check #1042"}'
st accounting invoices-mark-exported --data '[{"invoiceId":5521,"externalId":"QB-881"}]'
st accounting gl-accounts-list --filter active=true
st accounting journal-entries-list --range this-quarter
st accounting export-invoices --all --json
```

MCP: `st_accounting_invoices_list {"date_range": "last-month", "filters": {"status": "Posted"}}`

## Memberships — `st memberships` · `st_memberships_*`

Customer memberships, recurring services, invoice templates.

```bash
st memberships list --filter status=Active --all
st memberships recurring-services-list --filter locationId=321
st memberships recurring-service-events-mark-complete 77 --data '{"jobId":4567}'
st memberships export-memberships --all
```

MCP: `st_memberships_recurring_service_events_mark_complete {"record_id": 77, "data": {"jobId": 4567}}`

## Settings — `st settings` · `st_settings_*`

Employees, technicians, business units, tag types, user roles.

```bash
st settings employees-list --filter active=true
st settings technicians-account-action 142 --data '{"action":"Deactivate"}'
st settings tag-types-list
st settings business-units-update 3 --data '{"name":"HVAC North"}'
st settings export-technicians --all
```

MCP: `st_settings_technicians_account_action {"record_id": 142, "data": {"action": "Deactivate"}}`

---

## Pricebook — `st pricebook` · `st_pricebook_*`

Services, materials, equipment, categories, discounts (full CRUD).

```bash
st pricebook services-list --filter active=true --filter categoryId=5
st pricebook materials-get 9001
st pricebook equipment-create --data '{"code":"AC-3T","displayName":"3-Ton AC"}'
st pricebook discounts-and-fees-list
st pricebook export-services --all --json
```

## Inventory — `st inventory` · `st_inventory_*`

Purchase orders (date-filterable), receipts, returns, transfers, trucks, vendors.

```bash
st inventory purchase-orders-list --range this-month --filter businessUnitId=3
st inventory purchase-order-requests-list
st inventory purchase-order-requests-approve 4521
st inventory receipts-cancel 880 --data '{"canceledReason":"Duplicate"}'
st inventory vendors-list --filter active=true
st inventory export-purchase-orders --all
```

MCP: `st_inventory_purchase_orders_list {"date_range": "this-month", "filters": {"businessUnitId": 3}}`

## Sales & Estimates — `st salestech` · `st_sales_*`

Estimates (date-filterable) and templates. **Estimates live here, not in
accounting.**

```bash
st salestech estimates-list --range last-30-days --filter soldById=10
st salestech estimates-sell 33001 --data '{"soldBy":10}'
st salestech estimates-unsell 33001
st salestech estimate-templates-list
st salestech export-estimates --all
```

MCP: `st_sales_estimates_list {"date_range": "last-30-days"}` ·
`st_sales_estimates_sell {"record_id": 33001, "data": {"soldBy": 10}}`

## Payroll — `st payroll` · `st_payroll_*`

Gross pay items (date-filterable), adjustments, settings, payrolls, timesheets.

```bash
st payroll gross-pay-items-list --range last-week
st payroll employee-payrolls 10                 # payrolls for employee 10
st payroll job-timesheets-for-job 4567
st payroll activity-codes-list
st payroll export-gross-pay-items --all --json
```

MCP: `st_payroll_gross_pay_items_list {"date_range": "last-week"}`

## Marketing — `st marketing` · `st_marketing_*`

Campaigns, categories, costs.

```bash
st marketing campaigns-list --filter active=true
st marketing campaigns-get 12
st marketing costs-list --filter campaignId=12
st marketing categories-create --data '{"name":"Paid Search"}'
```

## Marketing Ads — `st marketing-ads` · `st_marketing_ads_*`

Attribution and performance analytics (mostly read + attribution POSTs).

```bash
st marketing-ads attributed-leads-list --filter fromUtc=2026-05-01
st marketing-ads performance-list
st marketing-ads external-call-attributions-create --data '{"webSessionData":{…},"externalCallData":{…}}'
```

MCP: `st_marketing_ads_external_call_attributions_create {"data": {...}}`

## Timesheets — `st timesheets` · `st_timesheets_*`

Activities (date-filterable) and their categories/types.

```bash
st timesheets activities-list --range this-week --filter employeeId=10
st timesheets activities-get 7700
st timesheets activity-types-list
st timesheets export-activities --all
```

MCP: `st_timesheets_activities_list {"date_range": "this-week"}`

## Equipment Systems — `st equipment-systems` · `st_equipment_systems_*`

Equipment systems, installed equipment, and equipment types. (ServiceTitan
serves this module at `/equipmentsystems/` — the CLI handles that for you.)

```bash
st equipment-systems installed-equipment-list --filter locationId=321
st equipment-systems installed-equipment-get 5500
st equipment-systems add-equipment 77 --data '{"equipmentIds":[5500]}'
st equipment-systems export-installed-equipment --all
```

## Findings — `st findings` · `st_findings_*`

Location findings, their attachments, and uploaded assets.

```bash
st findings location-findings-list --filter locationId=321
st findings location-findings-get 123
st findings location-findings-create --data '{"locationId":321,"name":"Cracked heat exchanger"}'
st findings location-findings-attachments-list 123
st findings assets-upload --data '{"file":"<base64>"}'
```

MCP: `st_findings_location_findings_list {"filters": {"locationId": 321}}` ·
`st_findings_location_findings_attachments_list {"path": {"id": 123}}`

## Fleet Pro — `st fleet-pro` · `st_fleet_pro_*`

Vehicles and historical (older than 7 days) GPS and event data.

```bash
st fleet-pro vehicles-list
st fleet-pro gps-history --data '{"startTime":"2026-10-01T00:00:00Z","endTime":"2026-10-02T00:00:00Z"}'
```

## Task Management — `st task-management` · `st_task_management_*`

Tasks and subtasks.

```bash
st task-management tasks-list --filter status=Open
st task-management tasks-create --data '{"name":"Reconcile PO #4521"}'
st task-management tasks-subtask 4040 --data '{"name":"Call vendor"}'
```

## Telecom — `st telecom` · `st_telecom_*`

Calls (date-filterable), recordings, voicemail, and SMS opt-outs.

```bash
st telecom calls-list --range last-7-days --all    # v3 calls feed
st telecom calls-get 778899
st telecom calls-update 778899 --data '{"campaignId":12}'
st telecom calls-recording 778899
st telecom optouts-status --data '{"contactNumbers":["+15555550100"]}'
st telecom export-calls --all --json
```

MCP: `st_telecom_calls_list {"date_range": "last-7-days"}` ·
`st_telecom_calls_get {"path": {"id": 778899}}`

## Customer Interactions — `st customer-interactions` · `st_customer_interactions_*`

Technician ratings.

```bash
st customer-interactions technician-ratings-list --filter technicianId=142
st customer-interactions technician-ratings-create --data '{"jobId":4567,"technicianId":142,"value":5}'
```

## Forms — `st forms` · `st_forms_*`

Form definitions, submissions (read), job attachments.

```bash
st forms list
st forms submissions-list --filter formId=15
st forms job-attachments-list 4567
```

## Job Booking — `st job-booking` · `st_jbce_*`

Call reasons (read-only).

```bash
st job-booking call-reasons-list
```

MCP: `st_jbce_call_reasons_list {}`

## Marketing Reputation — `st marketing-reputation` · `st_marketing_reputation_*`

Online reviews (date-filterable, read-only).

```bash
st marketing-reputation reviews-list --range last-month --all
```

MCP: `st_marketing_reputation_reviews_list {"date_range": "last-month"}`

## Scheduling Pro — `st scheduling-pro` · `st_scheduling_pro_*`

Schedulers, routers, their sessions and performance (read-only).

```bash
st scheduling-pro schedulers-list
st scheduling-pro scheduler-sessions 8c1e…
st scheduling-pro scheduler-performance 8c1e…
```

## Service Agreements — `st service-agreements` · `st_service_agreements_*`

Agreements (date-filterable, read-only; primary resource → bare names).

```bash
st service-agreements list --range this-year --all
st service-agreements get 20100
st service-agreements export-service-agreements --all
```

MCP: `st_service_agreements_list {"date_range": "this-year"}`

---

## Common timeframe patterns

```bash
# Today's activity
st jobs list --range today
st telecom calls-list --range today

# Trailing windows
st salestech estimates-list --range last-7-days
st accounting invoices-list --range last-30-days

# Calendar periods
st timesheets activities-list --range this-week
st payroll gross-pay-items-list --range last-month
st inventory purchase-orders-list --range this-quarter
st service-agreements list --range this-year

# Explicit start:end
st crm leads-list --from-date 2026-01-01 --to-date 2026-03-31
st marketing-reputation reviews-list --range 2026-01-01:2026-03-31
```

---

← [CLI reference](cli-reference.md) · [Docs index](README.md) · [API coverage →](api-coverage.md)

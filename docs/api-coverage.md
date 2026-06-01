# API coverage

> **Auto-generated reference.** Regenerate with the snippet at the bottom of this page.

`st` / `st-mcp` cover **all 24 ServiceTitan API v2 modules** — **393 CLI commands** and **394 MCP tools** total.

Each CLI group below maps to one ServiceTitan module. The MCP tool for any command is `st_{module}_{resource}_{action}` (job types live under `jpm`, estimates under `salestech`). Run `st <group> --help` or `st <group> <command> --help` for options.

Legend: most commands follow the generated archetypes — `…-list`, `…-get`, `…-create`, `…-update`, `…-delete`, domain actions, and `export-<feed>` change-feeds. See [CLI reference](cli-reference.md) for shared options and [Architecture](architecture.md) for how they're generated.

## `crm`

*CRM — customers, locations, contacts, leads* — _hand-tuned + generated_  ·  34 commands

```text
st crm booking-provider-tags-create
st crm booking-provider-tags-get
st crm booking-provider-tags-list
st crm booking-provider-tags-update
st crm bookings-create
st crm bookings-get
st crm bookings-list
st crm bookings-update
st crm contacts-create
st crm contacts-delete
st crm contacts-get
st crm contacts-list
st crm contacts-update
st crm customers-create
st crm customers-delete
st crm customers-get
st crm customers-list
st crm customers-note
st crm customers-update
st crm export-bookings
st crm export-customers
st crm export-locations
st crm leads-create
st crm leads-dismiss
st crm leads-follow-up
st crm leads-get
st crm leads-list
st crm leads-update
st crm locations-create
st crm locations-delete
st crm locations-get
st crm locations-list
st crm locations-note
st crm locations-update
```

## `jobs`

*Jobs — jobs, appointments, projects, job types* — _hand-tuned + generated_  ·  31 commands

```text
st jobs appointments-confirm
st jobs appointments-create
st jobs appointments-delete
st jobs appointments-get
st jobs appointments-hold
st jobs appointments-list
st jobs appointments-remove-confirmation
st jobs appointments-remove-hold
st jobs appointments-reschedule
st jobs appointments-update
st jobs budget-codes-create
st jobs budget-codes-get
st jobs budget-codes-list
st jobs cancel
st jobs create
st jobs export-appointments
st jobs export-jobs
st jobs export-projects
st jobs get
st jobs job-types-create
st jobs job-types-get
st jobs job-types-list
st jobs job-types-update
st jobs list
st jobs projects-attach-job
st jobs projects-create
st jobs projects-get
st jobs projects-list
st jobs projects-note
st jobs projects-update
st jobs update
```

## `dispatch`

*Dispatch — shifts, assignments, zones, teams, skills, arrival windows* — _hand-tuned + generated_  ·  39 commands

```text
st dispatch arrival-windows-activate
st dispatch arrival-windows-create
st dispatch arrival-windows-get
st dispatch arrival-windows-list
st dispatch arrival-windows-update
st dispatch assignments-assign-technicians
st dispatch assignments-list
st dispatch assignments-unassign-technicians
st dispatch business-hours-create
st dispatch business-hours-list
st dispatch capacity
st dispatch events-create
st dispatch events-delete
st dispatch events-get
st dispatch events-list
st dispatch events-update
st dispatch export-appointment-assignments
st dispatch export-technician-shifts
st dispatch shifts-create
st dispatch shifts-delete
st dispatch shifts-get
st dispatch shifts-list
st dispatch shifts-update
st dispatch skills-assign
st dispatch skills-create
st dispatch skills-delete
st dispatch skills-get
st dispatch skills-list
st dispatch teams-create
st dispatch teams-delete
st dispatch teams-get
st dispatch teams-list
st dispatch teams-update
st dispatch who-busy
st dispatch zones-create
st dispatch zones-delete
st dispatch zones-get
st dispatch zones-list
st dispatch zones-update
```

## `accounting`

*Accounting — invoices, payments, GL, journal entries, AP* — _hand-tuned + generated_  ·  43 commands

```text
st accounting ap-bills-get
st accounting ap-bills-list
st accounting ap-bills-update
st accounting ap-credits-get
st accounting ap-credits-list
st accounting ap-credits-update
st accounting ap-payments-get
st accounting ap-payments-list
st accounting ap-payments-update
st accounting bank-deposits-get
st accounting bank-deposits-list
st accounting credit-memos-get
st accounting credit-memos-list
st accounting credit-memos-update
st accounting export-inventory-bills
st accounting export-invoices
st accounting export-payments
st accounting gl-accounts-create
st accounting gl-accounts-get
st accounting gl-accounts-list
st accounting gl-accounts-update
st accounting inventory-bills-get
st accounting inventory-bills-list
st accounting inventory-bills-update
st accounting invoices-get
st accounting invoices-list
st accounting invoices-mark-exported
st accounting invoices-update
st accounting journal-entries-create
st accounting journal-entries-delete
st accounting journal-entries-get
st accounting journal-entries-list
st accounting journal-entries-update
st accounting payment-terms-get
st accounting payment-terms-list
st accounting payment-types-get
st accounting payment-types-list
st accounting payments-get
st accounting payments-list
st accounting payments-update
st accounting payments-update-status
st accounting tax-zones-get
st accounting tax-zones-list
```

## `memberships`

*Memberships — customer memberships, recurring services, invoice templates* — _hand-tuned + generated_  ·  20 commands

```text
st memberships create
st memberships export-memberships
st memberships export-recurring-services
st memberships get
st memberships invoice-templates-create
st memberships invoice-templates-get
st memberships invoice-templates-list
st memberships invoice-templates-update
st memberships list
st memberships recurring-service-events-get
st memberships recurring-service-events-list
st memberships recurring-service-events-mark-complete
st memberships recurring-service-events-mark-incomplete
st memberships recurring-service-types-get
st memberships recurring-service-types-list
st memberships recurring-services-get
st memberships recurring-services-list
st memberships recurring-services-update
st memberships types-list
st memberships update
```

## `reporting`

*Reporting — discover and pull ServiceTitan reports (e.g. Technician Scorecard)* — _hand-tuned + generated_  ·  4 commands

```text
st reporting categories
st reporting data
st reporting fields
st reporting reports
```

## `settings`

*Settings — employees, technicians, business units, tag types* — _hand-tuned + generated_  ·  23 commands

```text
st settings business-units-list
st settings business-units-update
st settings employees-activate
st settings employees-create
st settings employees-deactivate
st settings employees-get
st settings employees-list
st settings employees-update
st settings export-business-units
st settings export-employees
st settings export-technicians
st settings tag-types-create
st settings tag-types-get
st settings tag-types-list
st settings tag-types-update
st settings technicians-activate
st settings technicians-create
st settings technicians-deactivate
st settings technicians-get
st settings technicians-list
st settings technicians-update
st settings user-roles-get
st settings user-roles-list
```

## `pricebook`

*Pricebook — services, materials, equipment, categories, discounts* — _generated_  ·  36 commands

```text
st pricebook categories-create
st pricebook categories-delete
st pricebook categories-get
st pricebook categories-list
st pricebook categories-update
st pricebook client-specific-pricing-list
st pricebook client-specific-pricing-update
st pricebook discounts-and-fees-create
st pricebook discounts-and-fees-delete
st pricebook discounts-and-fees-get
st pricebook discounts-and-fees-list
st pricebook discounts-and-fees-update
st pricebook equipment-create
st pricebook equipment-delete
st pricebook equipment-get
st pricebook equipment-list
st pricebook equipment-update
st pricebook export-equipment
st pricebook export-materials
st pricebook export-services
st pricebook images-create
st pricebook images-list
st pricebook materials-create
st pricebook materials-delete
st pricebook materials-get
st pricebook materials-list
st pricebook materials-markup-create
st pricebook materials-markup-get
st pricebook materials-markup-list
st pricebook materials-markup-update
st pricebook materials-update
st pricebook services-create
st pricebook services-delete
st pricebook services-get
st pricebook services-list
st pricebook services-update
```

## `inventory`

*Inventory — purchase orders, receipts, returns, transfers, trucks, vendors* — _generated_  ·  50 commands

```text
st inventory adjustments-list
st inventory adjustments-update
st inventory export-adjustments
st inventory export-purchase-orders
st inventory export-receipts
st inventory export-returns
st inventory export-transfers
st inventory inventory-templates-list
st inventory purchase-order-markups-create
st inventory purchase-order-markups-delete
st inventory purchase-order-markups-get
st inventory purchase-order-markups-list
st inventory purchase-order-markups-update
st inventory purchase-order-types-create
st inventory purchase-order-types-get
st inventory purchase-order-types-list
st inventory purchase-order-types-update
st inventory purchase-orders-approve
st inventory purchase-orders-cancel
st inventory purchase-orders-create
st inventory purchase-orders-get
st inventory purchase-orders-list
st inventory purchase-orders-reject
st inventory purchase-orders-update
st inventory receipts-cancel
st inventory receipts-create
st inventory receipts-get
st inventory receipts-list
st inventory receipts-update
st inventory return-types-create
st inventory return-types-get
st inventory return-types-list
st inventory return-types-update
st inventory returns-cancel
st inventory returns-create
st inventory returns-get
st inventory returns-list
st inventory returns-update
st inventory transfers-list
st inventory transfers-update
st inventory trucks-create
st inventory trucks-get
st inventory trucks-list
st inventory trucks-update
st inventory vendors-create
st inventory vendors-get
st inventory vendors-list
st inventory vendors-update
st inventory warehouses-list
st inventory warehouses-update
```

## `salestech`

*Sales & Estimates — estimates, estimate/proposal templates* — _generated_  ·  21 commands

```text
st salestech estimate-templates-create
st salestech estimate-templates-delete
st salestech estimate-templates-get
st salestech estimate-templates-list
st salestech estimate-templates-update
st salestech estimates-create
st salestech estimates-dismiss
st salestech estimates-get
st salestech estimates-list
st salestech estimates-put-item
st salestech estimates-sell
st salestech estimates-unsell
st salestech estimates-update
st salestech export-estimates
st salestech proposal-templates-create
st salestech proposal-templates-delete
st salestech proposal-templates-get
st salestech proposal-templates-list
st salestech proposal-templates-update
st salestech proposal-types-get
st salestech proposal-types-list
```

## `payroll`

*Payroll — gross pay items, adjustments, settings, timesheets (read)* — _generated_  ·  25 commands

```text
st payroll activity-codes-get
st payroll activity-codes-list
st payroll employee-payroll-settings-list
st payroll employee-payroll-settings-update
st payroll employee-payrolls-list
st payroll export-gross-pay-items
st payroll export-payrolls
st payroll gross-pay-items-create
st payroll gross-pay-items-delete
st payroll gross-pay-items-get
st payroll gross-pay-items-list
st payroll gross-pay-items-update
st payroll job-splits-list
st payroll location-labor-types-list
st payroll payroll-adjustments-create
st payroll payroll-adjustments-get
st payroll payroll-adjustments-list
st payroll payrolls-get
st payroll payrolls-list
st payroll technician-payroll-settings-list
st payroll technician-payroll-settings-update
st payroll technician-payrolls-list
st payroll timesheet-codes-get
st payroll timesheet-codes-list
st payroll timesheets-list
```

## `marketing`

*Marketing — campaigns, categories, costs* — _generated_  ·  12 commands

```text
st marketing campaigns-create
st marketing campaigns-get
st marketing campaigns-list
st marketing campaigns-update
st marketing categories-create
st marketing categories-get
st marketing categories-list
st marketing categories-update
st marketing costs-create
st marketing costs-get
st marketing costs-list
st marketing costs-update
```

## `marketing-ads`

*Marketing Ads — attribution & performance analytics* — _generated_  ·  6 commands

```text
st marketing-ads attributed-leads-list
st marketing-ads capacity-warnings-list
st marketing-ads external-call-attributions-post
st marketing-ads performance-list
st marketing-ads web-booking-attributions-post
st marketing-ads web-lead-form-attributions-post
```

## `timesheets`

*Timesheets — activities, activity categories/types* — _generated_  ·  8 commands

```text
st timesheets activities-create
st timesheets activities-delete
st timesheets activities-get
st timesheets activities-list
st timesheets activities-update
st timesheets activity-categories-list
st timesheets activity-types-list
st timesheets export-activities
```

## `equipment-systems`

*Equipment Systems — installed equipment, equipment types* — _generated_  ·  10 commands

```text
st equipment-systems equipment-types-create
st equipment-systems equipment-types-get
st equipment-systems equipment-types-list
st equipment-systems equipment-types-update
st equipment-systems export-installed-equipment
st equipment-systems installed-equipment-attachment
st equipment-systems installed-equipment-create
st equipment-systems installed-equipment-get
st equipment-systems installed-equipment-list
st equipment-systems installed-equipment-update
```

## `findings`

*Findings — findings and finding assets* — _generated_  ·  7 commands

```text
st findings attachment
st findings create
st findings delete
st findings finding-assets-list
st findings get
st findings list
st findings update
```

## `task-management`

*Task Management — tasks and subtasks* — _generated_  ·  5 commands

```text
st task-management client-side-data-list
st task-management tasks-create
st task-management tasks-get
st task-management tasks-list
st task-management tasks-subtask
```

## `telecom`

*Telecom — calls (read + update)* — _generated_  ·  4 commands

```text
st telecom calls-get
st telecom calls-list
st telecom calls-update
st telecom export-calls
```

## `customer-interactions`

*Customer Interactions — technician ratings* — _generated_  ·  3 commands

```text
st customer-interactions technician-ratings-create
st customer-interactions technician-ratings-get
st customer-interactions technician-ratings-list
```

## `forms`

*Forms — form definitions, submissions (read), job attachments* — _generated_  ·  4 commands

```text
st forms get
st forms job-attachments-upload
st forms list
st forms submissions-list
```

## `job-booking`

*Job Booking — call reasons (read-only)* — _generated_  ·  1 commands

```text
st job-booking call-reasons-list
```

## `marketing-reputation`

*Marketing Reputation — online reviews (read-only)* — _generated_  ·  1 commands

```text
st marketing-reputation reviews-list
```

## `scheduling-pro`

*Scheduling Pro — schedulers, router (read-only)* — _generated_  ·  3 commands

```text
st scheduling-pro schedulers-get
st scheduling-pro schedulers-list
st scheduling-pro sessions-list
```

## `service-agreements`

*Service Agreements — agreements (read-only)* — _generated_  ·  3 commands

```text
st service-agreements export-service-agreements
st service-agreements get
st service-agreements list
```

---

## Regenerating this page

This page is derived from the live command tree so it can't drift from the code:

```bash
uv run python scripts/gen_api_coverage.py
```

← [Back to docs index](README.md) · [CLI reference](cli-reference.md) · [MCP server](mcp-server.md)

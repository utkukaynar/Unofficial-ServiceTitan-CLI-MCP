# API coverage

> **Auto-generated reference.** Regenerate with the snippet at the bottom of this page.

`st` / `st-mcp` cover **all 25 ServiceTitan API modules** — **608 CLI commands** and **608 MCP tools** total.

Each CLI group below maps to one ServiceTitan module. The MCP tool for any command is `st_{module}_{resource}_{action}`, where the module is the API module — it differs from the CLI group for `jobs` (`jpm`), `salestech` (`sales`) and `job-booking` (`jbce`). Run `st <group> --help` or `st <group> <command> --help` for options, including the path arguments of endpoint-style commands.

Legend: most commands follow the generated archetypes — `…-list`, `…-get`, `…-create`, `…-update`, `…-delete`, domain actions, and `export-<feed>` change-feeds. See [CLI reference](cli-reference.md) for shared options and [Architecture](architecture.md) for how they're generated.

## `crm`

*CRM — customers, locations, contacts, leads, bookings* — _hand-tuned + generated_  ·  87 commands

```text
st crm booking-provider-tags-create
st crm booking-provider-tags-get
st crm booking-provider-tags-list
st crm booking-provider-tags-update
st crm bookings-contacts-list
st crm bookings-get
st crm bookings-list
st crm contacts-by-relationship
st crm contacts-create
st crm contacts-delete
st crm contacts-get
st crm contacts-list
st crm contacts-methods-create
st crm contacts-methods-delete
st crm contacts-methods-get
st crm contacts-methods-list
st crm contacts-methods-preference-get
st crm contacts-methods-preference-update
st crm contacts-methods-preferences
st crm contacts-methods-replace
st crm contacts-methods-search
st crm contacts-methods-update
st crm contacts-preferences-metadata
st crm contacts-relationship-create
st crm contacts-relationship-delete
st crm contacts-relationships-list
st crm contacts-replace
st crm contacts-update
st crm customers-contacts-create
st crm customers-contacts-delete
st crm customers-contacts-list
st crm customers-contacts-search
st crm customers-contacts-update
st crm customers-create
st crm customers-custom-fields
st crm customers-get
st crm customers-list
st crm customers-note
st crm customers-note-delete
st crm customers-notes-list
st crm customers-tag-add
st crm customers-tag-remove
st crm customers-update
st crm export-bookings
st crm export-customers
st crm export-customers-contacts
st crm export-leads
st crm export-locations
st crm export-locations-contacts
st crm leads-create
st crm leads-create-v3
st crm leads-dismiss
st crm leads-follow-up
st crm leads-form-submit
st crm leads-get
st crm leads-list
st crm leads-note
st crm leads-notes-list
st crm leads-update
st crm locations-contacts-create
st crm locations-contacts-delete
st crm locations-contacts-list
st crm locations-contacts-search
st crm locations-contacts-update
st crm locations-create
st crm locations-custom-fields
st crm locations-get
st crm locations-list
st crm locations-note
st crm locations-note-delete
st crm locations-notes-list
st crm locations-preferred-technician
st crm locations-preferred-technician-set
st crm locations-tag-add
st crm locations-tag-remove
st crm locations-update
st crm provider-bookings-contacts-create
st crm provider-bookings-contacts-delete
st crm provider-bookings-contacts-list
st crm provider-bookings-contacts-update
st crm provider-bookings-create
st crm provider-bookings-dismiss
st crm provider-bookings-get
st crm provider-bookings-list
st crm provider-bookings-update
st crm tags-bulk-add
st crm tags-bulk-remove
```

## `jobs`

*Jobs — jobs, appointments, projects, job types, budget codes* — _hand-tuned + generated_  ·  77 commands

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
st jobs appointments-special-instructions
st jobs appointments-summary
st jobs budget-codes-create
st jobs budget-codes-create-batch
st jobs budget-codes-create-partial
st jobs budget-codes-create-partial-batch
st jobs budget-codes-list
st jobs budget-codes-match
st jobs cancel
st jobs create
st jobs export-appointments
st jobs export-job-canceled-logs
st jobs export-job-history
st jobs export-job-notes
st jobs export-jobs
st jobs export-project-notes
st jobs export-projects
st jobs get
st jobs job-booked-log
st jobs job-cancel-reasons-list
st jobs job-canceled-log
st jobs job-equipment-attach
st jobs job-equipment-detach
st jobs job-equipment-detach-one
st jobs job-equipment-list
st jobs job-history
st jobs job-hold-reasons-list
st jobs job-note-create
st jobs job-notes-list
st jobs job-remove-cancellation
st jobs job-types-create
st jobs job-types-get
st jobs job-types-list
st jobs job-types-update
st jobs jobs-cancel-reasons-by-job
st jobs jobs-custom-fields
st jobs jobs-hold-reasons-by-job
st jobs list
st jobs project-budget-codes-list
st jobs project-budget-codes-match
st jobs project-daily-log-attachment-add
st jobs project-daily-log-attachment-delete
st jobs project-daily-log-attachment-get
st jobs project-daily-log-get
st jobs project-daily-log-upsert
st jobs project-daily-logs-list
st jobs project-statuses-get
st jobs project-statuses-list
st jobs project-substatuses-get
st jobs project-substatuses-list
st jobs project-types-get
st jobs project-types-list
st jobs projects-attach-job
st jobs projects-create
st jobs projects-custom-fields
st jobs projects-detach-job
st jobs projects-get
st jobs projects-list
st jobs projects-note
st jobs projects-notes-list
st jobs projects-update
st jobs update
st jobs wbs-project-segment-item-children
st jobs wbs-project-segment-items
st jobs wbs-project-segments
st jobs wbs-segment-item-children
st jobs wbs-segment-items
st jobs wbs-segments
```

## `dispatch`

*Dispatch — shifts, assignments, zones, teams, skills, arrival windows* — _hand-tuned + generated_  ·  42 commands

```text
st dispatch arrival-windows-activate
st dispatch arrival-windows-config
st dispatch arrival-windows-config-update
st dispatch arrival-windows-create
st dispatch arrival-windows-get
st dispatch arrival-windows-list
st dispatch arrival-windows-replace
st dispatch assignments-assign-technicians
st dispatch assignments-list
st dispatch assignments-unassign-technicians
st dispatch business-hours-create
st dispatch business-hours-get
st dispatch capacity
st dispatch events-create
st dispatch events-delete
st dispatch events-get
st dispatch events-list
st dispatch events-replace
st dispatch export-appointment-assignments
st dispatch gps-pings-create
st dispatch shifts-bulk-delete
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
st dispatch technician-tracking
st dispatch who-busy
st dispatch zones-create
st dispatch zones-delete
st dispatch zones-get
st dispatch zones-list
st dispatch zones-update
```

## `accounting`

*Accounting — invoices, payments, GL, journal entries, AP, expenses* — _hand-tuned + generated_  ·  78 commands

```text
st accounting ap-bills-custom-fields
st accounting ap-bills-custom-fields-update
st accounting ap-bills-get
st accounting ap-bills-list
st accounting ap-bills-mark-exported
st accounting ap-credits-custom-fields
st accounting ap-credits-custom-fields-update
st accounting ap-credits-list
st accounting ap-credits-mark-exported
st accounting ap-payments-custom-fields
st accounting ap-payments-custom-fields-update
st accounting ap-payments-list
st accounting ap-payments-mark-exported
st accounting bank-deposits-list
st accounting bank-deposits-mark-exported
st accounting bank-deposits-transactions
st accounting credit-memos-custom-fields
st accounting credit-memos-custom-fields-update
st accounting credit-memos-items
st accounting credit-memos-items-all
st accounting credit-memos-list
st accounting credit-memos-mark-exported
st accounting credit-memos-splits
st accounting credit-memos-update
st accounting expense-transactions-custom-fields
st accounting expense-transactions-custom-fields-update
st accounting expense-transactions-get
st accounting expense-transactions-list
st accounting expense-transactions-mark-exported
st accounting export-inventory-bills
st accounting export-invoice-items
st accounting export-invoices
st accounting export-payments
st accounting gl-account-types-list
st accounting gl-accounts-create
st accounting gl-accounts-get
st accounting gl-accounts-list
st accounting gl-accounts-update
st accounting gl-accounts-well-known
st accounting inventory-bills-custom-fields
st accounting inventory-bills-custom-fields-update
st accounting inventory-bills-list
st accounting inventory-bills-mark-exported
st accounting inventory-bills-paginated
st accounting invoices-create
st accounting invoices-custom-fields
st accounting invoices-custom-fields-update
st accounting invoices-get
st accounting invoices-item-delete
st accounting invoices-items-update
st accounting invoices-list
st accounting invoices-mark-exported
st accounting invoices-tasks-create
st accounting invoices-tasks-list
st accounting invoices-tasks-update
st accounting invoices-update
st accounting journal-entries-create
st accounting journal-entries-delete
st accounting journal-entries-details
st accounting journal-entries-get
st accounting journal-entries-list
st accounting journal-entries-replace
st accounting journal-entries-summary
st accounting journal-entries-sync
st accounting journal-entries-update
st accounting payment-terms-get
st accounting payment-terms-list
st accounting payment-types-get
st accounting payment-types-list
st accounting payments-custom-fields
st accounting payments-custom-fields-update
st accounting payments-list
st accounting payments-update
st accounting payments-update-status
st accounting remittance-vendors-get
st accounting remittance-vendors-list
st accounting tax-zones-list
st accounting tax-zones-resolve
```

## `memberships`

*Memberships — customer memberships, recurring services, invoice templates* — _hand-tuned + generated_  ·  30 commands

```text
st memberships export-invoice-templates
st memberships export-membership-status-changes
st memberships export-membership-types
st memberships export-memberships
st memberships export-recurring-service-events
st memberships export-recurring-service-types
st memberships export-recurring-services
st memberships get
st memberships invoice-templates-create
st memberships invoice-templates-get
st memberships invoice-templates-list
st memberships invoice-templates-update
st memberships list
st memberships membership-types-discounts
st memberships membership-types-duration-billing-items
st memberships membership-types-get
st memberships membership-types-recurring-service-items
st memberships memberships-custom-fields
st memberships memberships-sale
st memberships memberships-status-changes
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

*Reporting — report categories, reports, report data* — _hand-tuned + generated_  ·  8 commands

```text
st reporting categories
st reporting data
st reporting data-query-cancel
st reporting data-query-result
st reporting data-query-start
st reporting dynamic-value-set
st reporting fields
st reporting reports
```

## `settings`

*Settings — employees, technicians, business units, tag types* — _hand-tuned + generated_  ·  24 commands

```text
st settings business-units-get
st settings business-units-intacct
st settings business-units-list
st settings business-units-update
st settings employees-account-action
st settings employees-create
st settings employees-custom-fields
st settings employees-get
st settings employees-list
st settings employees-update
st settings export-business-units
st settings export-employees
st settings export-tag-types
st settings export-technicians
st settings tag-types-create
st settings tag-types-list
st settings tag-types-update
st settings technicians-account-action
st settings technicians-create
st settings technicians-custom-fields
st settings technicians-get
st settings technicians-list
st settings technicians-update
st settings user-roles-list
```

## `pricebook`

*Pricebook — services, materials, equipment, categories, discounts* — _generated_  ·  40 commands

```text
st pricebook bulk-create
st pricebook bulk-update
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
st pricebook export-categories
st pricebook export-equipment
st pricebook export-materials
st pricebook export-services
st pricebook images-create
st pricebook images-download
st pricebook materials-cost-types
st pricebook materials-create
st pricebook materials-delete
st pricebook materials-get
st pricebook materials-list
st pricebook materials-markup-create
st pricebook materials-markup-get
st pricebook materials-markup-list
st pricebook materials-markup-replace
st pricebook materials-update
st pricebook services-create
st pricebook services-delete
st pricebook services-get
st pricebook services-list
st pricebook services-update
```

## `inventory`

*Inventory — purchase orders, receipts, returns, transfers, trucks, vendors* — _generated_  ·  53 commands

```text
st inventory adjustments-create
st inventory adjustments-custom-fields-update
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
st inventory purchase-order-requests-approve
st inventory purchase-order-requests-list
st inventory purchase-order-requests-reject
st inventory purchase-order-types-create
st inventory purchase-order-types-list
st inventory purchase-order-types-update
st inventory purchase-orders-cancel
st inventory purchase-orders-create
st inventory purchase-orders-custom-fields-update
st inventory purchase-orders-get
st inventory purchase-orders-list
st inventory purchase-orders-update
st inventory receipts-cancel
st inventory receipts-create
st inventory receipts-custom-fields-update
st inventory receipts-list
st inventory return-types-create
st inventory return-types-list
st inventory return-types-update
st inventory returns-cancel
st inventory returns-create
st inventory returns-custom-fields-update
st inventory returns-list
st inventory returns-update
st inventory transfers-custom-fields-update
st inventory transfers-list
st inventory transfers-update
st inventory trucks-create
st inventory trucks-list
st inventory trucks-update
st inventory vendors-create
st inventory vendors-custom-fields
st inventory vendors-custom-fields-update
st inventory vendors-get
st inventory vendors-list
st inventory vendors-update
st inventory warehouses-list
st inventory warehouses-update
```

## `salestech`

*Sales & Estimates — estimates, estimate/proposal templates, contracts* — _generated_  ·  25 commands

```text
st salestech contracts-list
st salestech estimate-templates-create
st salestech estimate-templates-delete
st salestech estimate-templates-get
st salestech estimate-templates-list
st salestech estimate-templates-update
st salestech estimates-create
st salestech estimates-dismiss
st salestech estimates-export-legacy
st salestech estimates-get
st salestech estimates-item-delete
st salestech estimates-items
st salestech estimates-list
st salestech estimates-put-item
st salestech estimates-replace
st salestech estimates-sell
st salestech estimates-status-changes
st salestech estimates-unsell
st salestech export-estimates
st salestech proposal-templates-create
st salestech proposal-templates-delete
st salestech proposal-templates-get
st salestech proposal-templates-list
st salestech proposal-templates-update
st salestech proposal-types-list
```

## `payroll`

*Payroll — gross pay items, adjustments, settings, timesheets, splits* — _generated_  ·  38 commands

```text
st payroll activity-codes-get
st payroll activity-codes-list
st payroll employee-payroll-settings
st payroll employee-payroll-settings-update
st payroll employee-payrolls
st payroll export-activity-codes
st payroll export-gross-pay-items
st payroll export-jobs-splits
st payroll export-jobs-timesheets
st payroll export-payroll-adjustments
st payroll export-payroll-settings
st payroll export-timesheet-codes
st payroll gross-pay-items-create
st payroll gross-pay-items-delete
st payroll gross-pay-items-list
st payroll gross-pay-items-replace
st payroll job-splits-for-job
st payroll job-splits-list
st payroll job-timesheets-for-job
st payroll job-timesheets-list
st payroll labor-types-create
st payroll labor-types-get
st payroll labor-types-list
st payroll labor-types-replace
st payroll location-rates-list
st payroll non-job-timesheets-list
st payroll payroll-adjustments-create
st payroll payroll-adjustments-delete
st payroll payroll-adjustments-get
st payroll payroll-adjustments-list
st payroll payroll-adjustments-replace
st payroll payroll-settings-list
st payroll payrolls-list
st payroll technician-payroll-settings
st payroll technician-payroll-settings-update
st payroll technician-payrolls
st payroll timesheet-codes-get
st payroll timesheet-codes-list
```

## `marketing`

*Marketing — campaigns, categories, costs, SMS opt-ins* — _generated_  ·  16 commands

```text
st marketing campaign-cost-summary
st marketing campaigns-costs
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
st marketing email-channel-cost
st marketing sms-optin-import
```

## `marketing-ads`

*Marketing Ads — attribution & performance analytics* — _generated_  ·  7 commands

```text
st marketing-ads attributed-leads-list
st marketing-ads capacity-warnings
st marketing-ads external-call-attributions-create
st marketing-ads job-attributions-create
st marketing-ads performance-list
st marketing-ads web-booking-attributions-create
st marketing-ads web-lead-form-attributions-create
```

## `timesheets`

*Timesheets — activities, activity categories/types* — _generated_  ·  12 commands

```text
st timesheets activities-create
st timesheets activities-delete
st timesheets activities-get
st timesheets activities-list
st timesheets activities-replace
st timesheets activity-categories-get
st timesheets activity-categories-list
st timesheets activity-types-get
st timesheets activity-types-list
st timesheets export-activities
st timesheets export-activity-categories
st timesheets export-activity-types
```

## `equipment-systems`

*Equipment Systems — equipment systems, installed equipment, equipment types* — _generated_  ·  22 commands

```text
st equipment-systems add-equipment
st equipment-systems create
st equipment-systems delete
st equipment-systems equipment-systems-custom-field-types
st equipment-systems equipment-types-create
st equipment-systems equipment-types-get
st equipment-systems equipment-types-list
st equipment-systems equipment-types-update
st equipment-systems export-equipment-systems
st equipment-systems export-installed-equipment
st equipment-systems get
st equipment-systems installed-equipment-attachment-download
st equipment-systems installed-equipment-attachment-upload
st equipment-systems installed-equipment-bulk-create
st equipment-systems installed-equipment-create
st equipment-systems installed-equipment-custom-field-types
st equipment-systems installed-equipment-get
st equipment-systems installed-equipment-list
st equipment-systems installed-equipment-update
st equipment-systems list
st equipment-systems remove-equipment
st equipment-systems update
```

## `findings`

*Findings — location findings and their attachments, assets* — _generated_  ·  11 commands

```text
st findings assets-download
st findings assets-upload
st findings location-findings-attachment-get
st findings location-findings-attachments-create
st findings location-findings-attachments-delete
st findings location-findings-attachments-list
st findings location-findings-attachments-update
st findings location-findings-create
st findings location-findings-get
st findings location-findings-list
st findings location-findings-update
```

## `fleet-pro`

*Fleet Pro — vehicles, historical GPS and events* — _generated_  ·  3 commands

```text
st fleet-pro events-history
st fleet-pro gps-history
st fleet-pro vehicles-list
```

## `task-management`

*Task Management — tasks and subtasks* — _generated_  ·  5 commands

```text
st task-management client-side-data
st task-management tasks-create
st task-management tasks-get
st task-management tasks-list
st task-management tasks-subtask
```

## `telecom`

*Telecom — calls, recordings, opt-outs* — _generated_  ·  9 commands

```text
st telecom calls-get
st telecom calls-list
st telecom calls-recording
st telecom calls-update
st telecom calls-voicemail
st telecom export-calls
st telecom optouts-add
st telecom optouts-list
st telecom optouts-status
```

## `customer-interactions`

*Customer Interactions — technician ratings* — _generated_  ·  4 commands

```text
st customer-interactions export-technician-ratings
st customer-interactions technician-rating-upsert
st customer-interactions technician-ratings-create
st customer-interactions technician-ratings-list
```

## `forms`

*Forms — form definitions, submissions, job attachments* — _generated_  ·  6 commands

```text
st forms job-attachment-download
st forms job-attachments-create
st forms job-attachments-delete
st forms job-attachments-list
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

*Scheduling Pro — schedulers, routers, sessions, performance (read-only)* — _generated_  ·  5 commands

```text
st scheduling-pro router-performance
st scheduling-pro router-sessions
st scheduling-pro scheduler-performance
st scheduling-pro scheduler-sessions
st scheduling-pro schedulers-list
```

## `service-agreements`

*Service Agreements — agreements (read-only)* — _generated_  ·  4 commands

```text
st service-agreements export-service-agreements
st service-agreements get
st service-agreements list
st service-agreements service-agreements-custom-fields
```

---

## Regenerating this page

This page is derived from the live command tree so it can't drift from the code:

```bash
uv run python scripts/gen_api_coverage.py
```

← [Examples & recipes](examples.md) · [Docs index](README.md) · [MCP server →](mcp-server.md)

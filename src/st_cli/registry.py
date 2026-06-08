"""Declarative spec of the ServiceTitan API v2 surface.

This is the single source of truth that ``engine.py`` turns into both ``st`` CLI
commands and ``st-mcp`` tools. It deliberately avoids hand-writing one function
per operation (~560 of them); instead each :class:`Resource` declares which of
the standard operations it supports and the engine generates them.

Conventions (matching ServiceTitan's consistent REST shape):

* list     ``GET    {module}/v2/tenant/{id}/{path}``
* get      ``GET    {module}/v2/tenant/{id}/{path}/{id}``
* create   ``POST   {module}/v2/tenant/{id}/{path}``
* update   ``PATCH  {module}/v2/tenant/{id}/{path}/{id}``
* replace  ``PUT    {module}/v2/tenant/{id}/{path}/{id}``
* delete   ``DELETE {module}/v2/tenant/{id}/{path}/{id}``
* action   ``{verb} {module}/v2/tenant/{id}/{path}[/{id}]/{action.path}``
* export   ``GET    {module}/v2/tenant/{id}/export/{feed}``  (change-feed)

``ops`` is a string subset of ``"LRCUDP"`` — **L**ist, **R**ead(get),
**C**reate, **U**pdate(PATCH), **D**elete, **P**ut(replace).

The 7 modules that already have rich hand-written commands (crm, jpm/jobs,
dispatch, accounting, memberships, reporting, settings) appear in
:data:`EXTENSIONS` carrying *only* the operations not already wrapped, so no
command/tool names collide. The remaining modules appear in :data:`MODULES`
with full specs and get freshly generated command groups.

Provenance: derived from OPERATOR_ST_API_SCOPE.md (ServiceTitan OpenAPI specs,
2026-05-27). Standard CRUD is generated from the R/C/U/D matrix; domain actions
and export feeds follow ServiceTitan's documented naming.
"""

from __future__ import annotations

from dataclasses import dataclass

Column = tuple[str, str]  # (display_name, api_field_key) — same shape as output.Column

# --- shared column sets (──json always returns full records, so these only
#     shape the human table; a small generic set is fine for most resources) ---
GENERIC: tuple[Column, ...] = (("ID", "id"), ("Name", "name"), ("Active", "active"))
NAMED: tuple[Column, ...] = (("ID", "id"), ("Name", "name"))
TXN: tuple[Column, ...] = (
    ("ID", "id"),
    ("Status", "status"),
    ("Total", "total"),
    ("Created", "createdOn"),
)
DOC: tuple[Column, ...] = (
    ("ID", "id"),
    ("Number", "number"),
    ("Status", "status"),
    ("Total", "total"),
    ("Created", "createdOn"),
)


@dataclass(frozen=True)
class Action:
    """A domain action (non-CRUD POST/PATCH/PUT/DELETE), e.g. ``estimates/{id}/sell``."""

    name: str  # command/tool suffix, e.g. "sell"
    verb: str = "POST"  # POST | PATCH | PUT | DELETE
    path: str = ""  # sub-path after resource[/{id}]; defaults to ``name``
    needs_id: bool = True  # operates on a specific record id
    needs_body: bool = False  # accepts a JSON body
    help: str = ""

    @property
    def subpath(self) -> str:
        return self.path or self.name


@dataclass(frozen=True)
class Resource:
    """One API resource and the standard operations it supports."""

    slug: str  # command/tool base, e.g. "purchase-orders"
    path: str = ""  # API path segment; defaults to ``slug``
    ops: str = ""  # subset of "LRCUDP"
    columns: tuple[Column, ...] = GENERIC
    id_param: str = "id"  # name of the id argument, e.g. "estimate_id"
    date_filter: bool = False
    date_keys: tuple[str, str] = ("createdOnOrAfter", "createdBefore")
    # Override the engine's default newest-first sort. Most ServiceTitan list
    # endpoints accept "-modifiedOn", but a few (e.g. payroll/gross-pay-items)
    # have their own enum and 400 on anything outside it.
    default_sort: str | None = None
    actions: tuple[Action, ...] = ()
    title: str = ""  # table title; defaults to a title-cased slug

    @property
    def api_path(self) -> str:
        return self.path or self.slug


@dataclass(frozen=True)
class Module:
    """An API module = a CLI command group + an MCP tool namespace."""

    name: str  # API module, e.g. "pricebook" (used in URLs + tool tags/names)
    help: str
    resources: tuple[Resource, ...] = ()
    export_feeds: tuple[str, ...] = ()  # change-feed names under export/{feed}
    group: str = ""  # CLI group name; defaults to ``name``

    @property
    def cli_group(self) -> str:
        return self.group or self.name


# Common lifecycle actions reused across modules.
_ACTIVATE = Action("activate", help="Activate the record")
_DEACTIVATE = Action("deactivate", help="Deactivate the record")

# ===========================================================================
# EXTENSIONS — gap operations appended onto the 7 existing hand-written groups.
# Only ops/resources NOT already hand-written appear here (no name collisions).
# ===========================================================================

EXTENSIONS: tuple[Module, ...] = (
    Module(
        name="crm",
        help="CRM — customers, locations, contacts, leads",
        resources=(
            # customers: hand-written has list/get/create/update — add delete + notes
            Resource(
                "customers",
                ops="D",
                columns=(("ID", "id"), ("Name", "name"), ("Active", "active")),
                id_param="customer_id",
                actions=(
                    Action("note", path="notes", needs_body=True, help="Add a note to a customer"),
                ),
            ),
            # locations: hand-written has list/get — add create/update/delete
            Resource(
                "locations",
                ops="CUD",
                columns=(("ID", "id"), ("Name", "name")),
                id_param="location_id",
                actions=(
                    Action("note", path="notes", needs_body=True, help="Add a note to a location"),
                ),
            ),
            # contacts: hand-written has list/get — add create/update/delete
            Resource("contacts", ops="CUD", id_param="contact_id"),
            Resource(
                "leads",
                ops="LRCU",
                columns=(("ID", "id"), ("Status", "status"), ("Created", "createdOn")),
                id_param="lead_id",
                date_filter=True,
                actions=(
                    Action("dismiss", help="Dismiss a lead"),
                    Action("follow-up", path="follow-up", needs_body=True, help="Set follow-up"),
                ),
            ),
            Resource("booking-provider-tags", ops="LRCU", id_param="tag_id"),
        ),
        export_feeds=("customers", "locations", "bookings"),
    ),
    Module(
        name="jpm",
        group="jobs",
        help="Jobs — jobs, appointments, projects, job types",
        resources=(
            # job-types belongs to jpm (fixes the settings routing bug)
            Resource(
                "job-types",
                ops="LRCU",
                columns=(("ID", "id"), ("Name", "name"), ("Active", "active")),
                id_param="job_type_id",
            ),
            Resource("budget-codes", ops="LRC", id_param="budget_code_id"),
            # projects: hand-written has list/get — add create/update + actions
            Resource(
                "projects",
                ops="CU",
                columns=(("ID", "id"), ("Name", "name"), ("Status", "status")),
                id_param="project_id",
                actions=(
                    Action("note", path="notes", needs_body=True, help="Add a note to a project"),
                    Action(
                        "attach-job",
                        path="attachToJob",
                        needs_body=True,
                        help="Attach a job to the project",
                    ),
                ),
            ),
            # appointments: hand-written has list/get — add create/update/delete + lifecycle
            Resource(
                "appointments",
                ops="CUD",
                id_param="appointment_id",
                actions=(
                    Action("reschedule", needs_body=True, help="Reschedule an appointment"),
                    Action("hold", needs_body=True, help="Place an appointment on hold"),
                    Action("remove-hold", path="hold", verb="DELETE", help="Remove a hold"),
                    Action("confirm", needs_body=True, help="Confirm an appointment"),
                    Action(
                        "remove-confirmation",
                        path="confirmation",
                        verb="DELETE",
                        help="Remove a confirmation",
                    ),
                ),
            ),
        ),
        export_feeds=("jobs", "appointments", "projects"),
    ),
    Module(
        name="dispatch",
        help="Dispatch — shifts, assignments, zones, teams, skills, arrival windows",
        resources=(
            Resource("shifts", path="technician-shifts", ops="RCUD", id_param="shift_id"),
            Resource("events", path="non-job-appointments", ops="RUD", id_param="event_id"),
            Resource(
                "assignments",
                path="appointment-assignments",
                actions=(
                    Action(
                        "assign-technicians",
                        path="assign-technicians",
                        needs_id=False,
                        needs_body=True,
                        help="Assign technicians to an appointment",
                    ),
                    Action(
                        "unassign-technicians",
                        path="unassign-technicians",
                        needs_id=False,
                        needs_body=True,
                        help="Unassign technicians from an appointment",
                    ),
                ),
            ),
            Resource("zones", ops="RCUD", id_param="zone_id"),
            Resource("teams", ops="RCUD", id_param="team_id"),
            Resource(
                "skills",
                path="technician-skills",
                ops="LRCD",
                id_param="skill_id",
                actions=(
                    Action(
                        "assign",
                        needs_id=False,
                        needs_body=True,
                        help="Assign a skill to technicians",
                    ),
                ),
            ),
            Resource(
                "arrival-windows",
                ops="LRCU",
                id_param="arrival_window_id",
                actions=(_ACTIVATE,),
            ),
            Resource("business-hours", ops="LC"),
        ),
        export_feeds=("technician-shifts", "appointment-assignments"),
    ),
    Module(
        name="accounting",
        help="Accounting — invoices, payments, GL, journal entries, AP",
        resources=(
            # invoices: hand-written has list/get — add update + delete-item + mark-exported
            Resource(
                "invoices",
                ops="U",
                columns=DOC,
                id_param="invoice_id",
                actions=(
                    Action(
                        "mark-exported",
                        path="export",
                        needs_id=False,
                        needs_body=True,
                        help="Mark invoices as exported to an accounting system",
                    ),
                ),
            ),
            # payments: hand-written has list — add get/update + status
            Resource(
                "payments",
                ops="RU",
                columns=(("ID", "id"), ("Amount", "total"), ("Status", "status")),
                id_param="payment_id",
                actions=(Action("update-status", path="status", verb="PATCH", needs_body=True),),
            ),
            Resource("gl-accounts", ops="LRCU", id_param="gl_account_id"),
            Resource(
                "journal-entries",
                ops="LRCUD",
                columns=(("ID", "id"), ("Name", "name"), ("Status", "status")),
                id_param="journal_entry_id",
            ),
            Resource("credit-memos", ops="LRU", columns=DOC, id_param="credit_memo_id"),
            Resource("ap-bills", ops="LRU", columns=DOC, id_param="ap_bill_id"),
            Resource("ap-credits", ops="LRU", columns=DOC, id_param="ap_credit_id"),
            Resource("ap-payments", ops="LRU", columns=DOC, id_param="ap_payment_id"),
            Resource("inventory-bills", ops="LRU", columns=DOC, id_param="inventory_bill_id"),
            Resource("bank-deposits", ops="LR", id_param="deposit_id"),
            Resource("payment-terms", ops="LR", id_param="term_id"),
            Resource("payment-types", ops="LR", id_param="payment_type_id"),
            Resource("tax-zones", ops="LR", id_param="tax_zone_id"),
        ),
        export_feeds=("invoices", "payments", "inventory-bills"),
    ),
    Module(
        name="memberships",
        help="Memberships — customer memberships, recurring services, invoice templates",
        resources=(
            # memberships: hand-written has list/get — add create/update
            Resource(
                "memberships",
                ops="CU",
                columns=(("ID", "id"), ("Status", "status")),
                id_param="membership_id",
            ),
            Resource("invoice-templates", ops="LRCU", id_param="template_id"),
            Resource(
                "recurring-services",
                path="location-recurring-services",
                ops="LRU",
                id_param="service_id",
            ),
            Resource(
                "recurring-service-events",
                path="location-recurring-service-events",
                ops="LR",
                id_param="event_id",
                actions=(
                    Action("mark-complete", path="complete", help="Mark service event complete"),
                    Action(
                        "mark-incomplete", path="incomplete", help="Mark service event incomplete"
                    ),
                ),
            ),
            Resource("recurring-service-types", ops="LR", id_param="type_id"),
        ),
        export_feeds=("memberships", "recurring-services"),
    ),
    Module(
        name="settings",
        help="Settings — employees, technicians, business units, tag types",
        resources=(
            Resource(
                "employees",
                ops="LRCU",
                id_param="employee_id",
                actions=(_ACTIVATE, _DEACTIVATE),
            ),
            Resource(
                "technicians",
                ops="LRCU",
                id_param="technician_id",
                actions=(_ACTIVATE, _DEACTIVATE),
            ),
            Resource("tag-types", ops="LRCU", id_param="tag_type_id"),
            # business-units: hand-written CLI has list, MCP has list+get — add update
            Resource("business-units", ops="U", id_param="business_unit_id"),
            Resource("user-roles", ops="LR", id_param="role_id"),
        ),
        export_feeds=("employees", "technicians", "business-units"),
    ),
)


# ===========================================================================
# MODULES — brand-new groups (full specs). 17 modules with no existing app.
# ===========================================================================

MODULES: tuple[Module, ...] = (
    Module(
        name="pricebook",
        help="Pricebook — services, materials, equipment, categories, discounts",
        resources=(
            Resource("services", ops="LRCUD", id_param="service_id"),
            Resource("materials", ops="LRCUD", id_param="material_id"),
            Resource("equipment", ops="LRCUD", id_param="equipment_id"),
            Resource("categories", ops="LRCUD", id_param="category_id"),
            Resource("discounts-and-fees", ops="LRCUD", id_param="discount_id"),
            Resource("materials-markup", ops="LRCU", id_param="markup_id"),
            Resource("client-specific-pricing", ops="LU", id_param="pricing_id"),
            Resource("images", ops="LC"),
        ),
        export_feeds=("services", "materials", "equipment"),
    ),
    Module(
        name="inventory",
        help="Inventory — purchase orders, receipts, returns, transfers, trucks, vendors",
        resources=(
            Resource(
                "purchase-orders",
                ops="LRCU",
                columns=DOC,
                id_param="purchase_order_id",
                date_filter=True,
                actions=(
                    Action("cancel", help="Cancel a purchase order"),
                    Action("approve", help="Approve a purchase order request"),
                    Action("reject", help="Reject a purchase order request"),
                ),
            ),
            Resource("purchase-order-markups", ops="LRCUD", id_param="markup_id"),
            Resource("purchase-order-types", ops="LRCU", id_param="po_type_id"),
            Resource(
                "receipts",
                ops="LRCU",
                columns=DOC,
                id_param="receipt_id",
                actions=(Action("cancel", help="Cancel a receipt"),),
            ),
            Resource(
                "returns",
                ops="LRCU",
                columns=DOC,
                id_param="return_id",
                actions=(Action("cancel", help="Cancel a return"),),
            ),
            Resource("return-types", ops="LRCU", id_param="return_type_id"),
            Resource("adjustments", ops="LU", id_param="adjustment_id"),
            Resource("transfers", ops="LU", id_param="transfer_id"),
            Resource("trucks", ops="LRCU", id_param="truck_id"),
            Resource("vendors", ops="LRCU", id_param="vendor_id"),
            Resource("warehouses", ops="LU", id_param="warehouse_id"),
            Resource("inventory-templates", ops="L"),
        ),
        export_feeds=("purchase-orders", "receipts", "returns", "transfers", "adjustments"),
    ),
    Module(
        name="sales",
        group="salestech",
        help="Sales & Estimates — estimates, estimate/proposal templates",
        resources=(
            # estimates live in salestech (fixes the accounting routing bug)
            Resource(
                "estimates",
                ops="LRCU",
                columns=DOC,
                id_param="estimate_id",
                date_filter=True,
                actions=(
                    Action("sell", needs_body=True, help="Mark an estimate as sold"),
                    Action("unsell", help="Reverse a sold estimate"),
                    Action("dismiss", help="Dismiss an estimate"),
                    Action(
                        "put-item",
                        path="items",
                        verb="PUT",
                        needs_body=True,
                        help="Add/replace an estimate line item",
                    ),
                ),
            ),
            Resource("estimate-templates", ops="LRCUD", id_param="template_id"),
            Resource("proposal-templates", ops="LRCUD", id_param="template_id"),
            Resource("proposal-types", ops="LR", id_param="proposal_type_id"),
        ),
        export_feeds=("estimates",),
    ),
    Module(
        name="payroll",
        help="Payroll — gross pay items, adjustments, settings, timesheets (read)",
        resources=(
            Resource(
                "gross-pay-items",
                ops="LRCUD",
                id_param="item_id",
                date_filter=True,
                default_sort="-date",  # endpoint only accepts ±date for sort
            ),
            Resource("payroll-adjustments", ops="LRC", id_param="adjustment_id"),
            Resource(
                "employee-payroll-settings",
                ops="LU",
                id_param="employee_id",
            ),
            Resource(
                "technician-payroll-settings",
                ops="LU",
                id_param="technician_id",
            ),
            Resource("payrolls", ops="LR", id_param="payroll_id"),
            Resource("employee-payrolls", ops="L"),
            Resource("technician-payrolls", ops="L"),
            Resource("timesheets", ops="L"),
            Resource("job-splits", ops="L"),
            Resource("activity-codes", ops="LR", id_param="code_id"),
            Resource("timesheet-codes", ops="LR", id_param="code_id"),
            Resource("location-labor-types", ops="L"),
        ),
        export_feeds=("payrolls", "gross-pay-items"),
    ),
    Module(
        name="marketing",
        help="Marketing — campaigns, categories, costs",
        resources=(
            Resource("campaigns", ops="LRCU", id_param="campaign_id"),
            Resource("categories", path="categories", ops="LRCU", id_param="category_id"),
            Resource("costs", path="costs", ops="LRCU", id_param="cost_id"),
        ),
    ),
    Module(
        name="marketing-ads",
        help="Marketing Ads — attribution & performance analytics",
        resources=(
            Resource("attributed-leads", ops="L"),
            Resource("performance", ops="L"),
            Resource("capacity-warnings", path="capacity-warnings", ops="L"),
            Resource(
                "external-call-attributions",
                actions=(
                    Action(
                        "post",
                        needs_id=False,
                        needs_body=True,
                        help="Post an external-call attribution event",
                    ),
                ),
            ),
            Resource(
                "web-booking-attributions",
                actions=(
                    Action(
                        "post",
                        needs_id=False,
                        needs_body=True,
                        help="Post a web-booking attribution event",
                    ),
                ),
            ),
            Resource(
                "web-lead-form-attributions",
                actions=(
                    Action(
                        "post",
                        needs_id=False,
                        needs_body=True,
                        help="Post a web-lead-form attribution event",
                    ),
                ),
            ),
        ),
    ),
    Module(
        name="timesheets",
        help="Timesheets — activities, activity categories/types",
        resources=(
            Resource("activities", ops="LRCUD", id_param="activity_id", date_filter=True),
            Resource("activity-categories", ops="L"),
            Resource("activity-types", ops="L"),
        ),
        export_feeds=("activities",),
    ),
    Module(
        name="equipment-systems",
        help="Equipment Systems — installed equipment, equipment types",
        resources=(
            Resource(
                "installed-equipment",
                ops="LRCU",
                id_param="equipment_id",
                actions=(
                    Action(
                        "attachment",
                        path="attachments",
                        needs_body=True,
                        help="Post an attachment to installed equipment",
                    ),
                ),
            ),
            Resource("equipment-types", ops="LRCU", id_param="type_id"),
        ),
        export_feeds=("installed-equipment",),
    ),
    Module(
        name="findings",
        help="Findings — findings and finding assets",
        resources=(
            Resource(
                "findings",
                ops="LRCUD",
                id_param="finding_id",
                actions=(
                    Action(
                        "attachment",
                        path="attachments",
                        needs_body=True,
                        help="Add an attachment to a finding",
                    ),
                ),
            ),
            Resource("finding-assets", ops="L"),
        ),
    ),
    Module(
        name="task-management",
        help="Task Management — tasks and subtasks",
        resources=(
            Resource(
                "tasks",
                ops="LRC",
                id_param="task_id",
                actions=(
                    Action(
                        "subtask",
                        path="subtasks",
                        needs_body=True,
                        help="Create a subtask under a task",
                    ),
                ),
            ),
            Resource("client-side-data", path="data", ops="L"),
        ),
    ),
    Module(
        name="telecom",
        help="Telecom — calls (read + update)",
        resources=(
            Resource(
                "calls",
                ops="LRU",
                columns=(("ID", "id"), ("From", "from"), ("To", "to"), ("Created", "createdOn")),
                id_param="call_id",
                date_filter=True,
            ),
        ),
        export_feeds=("calls",),
    ),
    Module(
        name="customer-interactions",
        help="Customer Interactions — technician ratings",
        resources=(Resource("technician-ratings", ops="LRC", id_param="rating_id"),),
    ),
    Module(
        name="forms",
        help="Forms — form definitions, submissions (read), job attachments",
        resources=(
            Resource("forms", ops="LR", id_param="form_id"),
            Resource("submissions", path="submissions", ops="L"),
            Resource(
                "job-attachments",
                actions=(
                    Action(
                        "upload",
                        needs_id=False,
                        needs_body=True,
                        help="Upload an attachment to a job",
                    ),
                ),
            ),
        ),
    ),
    Module(
        name="jbce",
        group="job-booking",
        help="Job Booking — call reasons (read-only)",
        resources=(Resource("call-reasons", ops="L"),),
    ),
    Module(
        name="marketing-reputation",
        help="Marketing Reputation — online reviews (read-only)",
        resources=(Resource("reviews", ops="L", date_filter=True),),
    ),
    Module(
        name="scheduling-pro",
        help="Scheduling Pro — schedulers, router (read-only)",
        resources=(
            Resource("schedulers", ops="LR", id_param="scheduler_id"),
            Resource("sessions", path="sessions", ops="L"),
        ),
    ),
    Module(
        name="service-agreements",
        help="Service Agreements — agreements (read-only)",
        resources=(
            Resource("service-agreements", ops="LR", id_param="agreement_id", date_filter=True),
        ),
        export_feeds=("service-agreements",),
    ),
)


def all_modules() -> tuple[Module, ...]:
    """Every module spec the engine should process (extensions + new)."""
    return EXTENSIONS + MODULES

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

Anything that doesn't fit that shape — parent IDs in the path
(``contacts/{contactId}/contact-methods/{id}``), string IDs, bulk operations
without an ID, ``v3``-only endpoints — is declared as an :class:`Endpoint`: one
verb on one path template.

The 7 modules that already have rich hand-written commands (crm, jpm/jobs,
dispatch, accounting, memberships, reporting, settings) appear in
:data:`EXTENSIONS` carrying *only* the operations not already wrapped, so no
command/tool names collide. The remaining modules appear in :data:`MODULES`
with full specs and get freshly generated command groups.

Provenance: ServiceTitan's OpenAPI documents from developer.servicetitan.io
(downloaded 2026-11-27). ``tests/test_spec_conformance.py`` checks every
operation declared here against those documents when they are present in
``specs/`` (they are not committed — see AGENTS.md).
"""

from __future__ import annotations

import re
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
    version: str = "v2"  # API version segment; a few endpoints exist only under v3

    @property
    def api_path(self) -> str:
        return self.path or self.slug


PATH_PARAM = re.compile(r"\{(\w+)\}")


@dataclass(frozen=True)
class Endpoint:
    """One operation the CRUD archetypes can't express: a verb on a path template.

    ``path`` is relative to the tenant root and may contain ``{placeholders}``
    (filled positionally on the CLI, by name via MCP), e.g.
    ``contacts/{contactId}/contact-methods/{id}``.
    """

    name: str  # command/tool suffix, e.g. "contact-methods-get"
    verb: str  # GET | POST | PUT | PATCH | DELETE
    path: str
    body: bool = False  # accepts a JSON body
    paged: bool = False  # GET returning the standard {data, hasMore, ...} page envelope
    version: str = "v2"
    help: str = ""
    columns: tuple[Column, ...] = GENERIC  # table columns for paged results

    @property
    def path_params(self) -> tuple[str, ...]:
        return tuple(PATH_PARAM.findall(self.path))


@dataclass(frozen=True)
class Module:
    """An API module = a CLI command group + an MCP tool namespace."""

    name: str  # module id for MCP tool names/tags, e.g. "pricebook" -> st_pricebook_*
    help: str
    resources: tuple[Resource, ...] = ()
    export_feeds: tuple[str, ...] = ()  # change-feed names under export/{feed}
    group: str = ""  # CLI group name; defaults to ``name``
    # URL segment when it differs from ``name`` — ServiceTitan drops the hyphen for
    # some modules (/equipmentsystems/v2/...) while tool names keep it readable.
    url: str = ""
    endpoints: tuple[Endpoint, ...] = ()

    @property
    def cli_group(self) -> str:
        return self.group or self.name

    @property
    def api_module(self) -> str:
        return self.url or self.name


# ---------------------------------------------------------------------------
# Builders for shapes ServiceTitan repeats across many resources. Each returns
# plain registry objects — they only remove copy-paste, they add no behaviour.
# ---------------------------------------------------------------------------


def _get(name: str, path: str, help: str = "") -> Endpoint:
    return Endpoint(name, "GET", path, help=help)


def _list(name: str, path: str, help: str = "") -> Endpoint:
    return Endpoint(name, "GET", path, paged=True, help=help)


def _send(verb: str, name: str, path: str, help: str = "", *, body: bool = True) -> Endpoint:
    return Endpoint(name, verb, path, body=body, help=help)


def _custom_fields(slug: str, path: str, *, read: bool = True) -> tuple[Endpoint, ...]:
    """``{path}/custom-fields``: list the custom-field types, bulk-update values."""
    update = _send(
        "PATCH",
        f"{slug}-custom-fields-update",
        f"{path}/custom-fields",
        f"Bulk-update custom field values on {slug}",
    )
    if not read:
        return (update,)
    listing = _list(
        f"{slug}-custom-fields", f"{path}/custom-fields", f"List custom field types for {slug}"
    )
    return (listing, update)


def _mark_exported(what: str) -> Action:
    """``POST {path}/markasexported`` — flag records as synced to an external system."""
    return Action(
        "mark-exported",
        path="markasexported",
        needs_id=False,
        needs_body=True,
        help=f"Mark {what} as exported to an external system",
    )


def _nested_crud(slug: str, parent: str, child: str, ops: str, label: str) -> tuple[Endpoint, ...]:
    """Endpoints for a child collection under ``{parent}/{id}/{child}``.

    ``ops`` uses the registry letters: L list, C create, U update (PATCH),
    D delete. The child's own id placeholder is ``{childId}``.
    """
    base = f"{parent}/{{id}}/{child}"
    out: list[Endpoint] = []
    if "L" in ops:
        out.append(_list(f"{slug}-list", base, f"List {label}"))
    if "C" in ops:
        out.append(_send("POST", f"{slug}-create", base, f"Create a {label[:-1]}"))
    if "U" in ops:
        out.append(
            _send("PATCH", f"{slug}-update", f"{base}/{{childId}}", f"Update a {label[:-1]}")
        )
    if "D" in ops:
        out.append(
            _send(
                "DELETE",
                f"{slug}-delete",
                f"{base}/{{childId}}",
                f"Remove a {label[:-1]}",
                body=False,
            )
        )
    return tuple(out)


def _tagging(slug: str, parent: str) -> tuple[Endpoint, ...]:
    path = f"{parent}/{{id}}/tags/{{tagTypeId}}"
    return (
        _send("POST", f"{slug}-tag-add", path, f"Add a tag to a {slug[:-1]}", body=False),
        _send("DELETE", f"{slug}-tag-remove", path, f"Remove a tag from a {slug[:-1]}", body=False),
    )


# ===========================================================================
# EXTENSIONS — gap operations appended onto the 7 existing hand-written groups.
# Only ops/resources NOT already hand-written appear here (no name collisions).
# ===========================================================================

EXTENSIONS: tuple[Module, ...] = (
    Module(
        name="crm",
        help="CRM — customers, locations, contacts, leads, bookings",
        resources=(
            # customers: hand-written has list/get/create/update
            Resource(
                "customers",
                columns=(("ID", "id"), ("Name", "name"), ("Active", "active")),
                id_param="customer_id",
                actions=(
                    Action("note", path="notes", needs_body=True, help="Add a note to a customer"),
                ),
            ),
            # locations: hand-written has list/get
            Resource(
                "locations",
                ops="CU",
                columns=(("ID", "id"), ("Name", "name")),
                id_param="location_id",
                actions=(
                    Action("note", path="notes", needs_body=True, help="Add a note to a location"),
                ),
            ),
            Resource(
                "leads",
                ops="LRCU",
                columns=(("ID", "id"), ("Status", "status"), ("Created", "createdOn")),
                id_param="lead_id",
                date_filter=True,
                actions=(
                    Action("dismiss", needs_body=True, help="Dismiss a lead"),
                    Action("follow-up", needs_body=True, help="Create a follow-up for a lead"),
                    Action("note", path="notes", needs_body=True, help="Add a note to a lead"),
                ),
            ),
            Resource("booking-provider-tags", ops="LRCU", id_param="tag_id"),
        ),
        endpoints=(
            # customers
            _list("customers-notes-list", "customers/{id}/notes", "List a customer's notes"),
            _send(
                "DELETE",
                "customers-note-delete",
                "customers/{id}/notes/{noteId}",
                "Delete a customer note",
                body=False,
            ),
            *_nested_crud(
                "customers-contacts", "customers", "contacts", "LCUD", "customer contacts"
            ),
            _list(
                "customers-contacts-search",
                "customers/contacts",
                "List customer contacts by modified date or customer IDs",
            ),
            *_tagging("customers", "customers"),
            _list("customers-custom-fields", "customers/custom-fields", "Customer custom fields"),
            _send("PUT", "tags-bulk-add", "tags", "Add tags to many customers at once"),
            _send("DELETE", "tags-bulk-remove", "tags", "Remove tags from many customers at once"),
            # locations
            _list("locations-notes-list", "locations/{id}/notes", "List a location's notes"),
            _send(
                "DELETE",
                "locations-note-delete",
                "locations/{id}/notes/{noteId}",
                "Delete a location note",
                body=False,
            ),
            *_nested_crud(
                "locations-contacts", "locations", "contacts", "LCUD", "location contacts"
            ),
            _list(
                "locations-contacts-search",
                "locations/contacts",
                "List location contacts by modified/created date or location IDs",
            ),
            *_tagging("locations", "locations"),
            _list("locations-custom-fields", "locations/custom-fields", "Location custom fields"),
            _get(
                "locations-preferred-technician",
                "locations/{id}/preferredtechnician",
                "Get a location's preferred technician",
            ),
            _send(
                "POST",
                "locations-preferred-technician-set",
                "locations/{id}/preferredtechnician/{preferredTechnicianId}",
                "Set a location's preferred technician",
                body=False,
            ),
            # contacts — ids are strings (GUIDs), so these are endpoints, not a Resource
            _send("POST", "contacts-create", "contacts", "Create a contact"),
            _send("PATCH", "contacts-update", "contacts/{id}", "Update a contact"),
            _send("PUT", "contacts-replace", "contacts/{id}", "Replace a contact"),
            _send("DELETE", "contacts-delete", "contacts/{id}", "Delete a contact", body=False),
            _list(
                "contacts-methods-list",
                "contacts/{contactId}/contact-methods",
                "List a contact's methods (phone, email, …)",
            ),
            _send(
                "POST",
                "contacts-methods-create",
                "contacts/{contactId}/contact-methods",
                "Add a contact method",
            ),
            _get(
                "contacts-methods-get",
                "contacts/{contactId}/contact-methods/{contactMethodId}",
                "Get a contact method",
            ),
            _send(
                "PUT",
                "contacts-methods-replace",
                "contacts/{contactId}/contact-methods/{contactMethodId}",
                "Replace a contact method",
            ),
            _send(
                "PATCH",
                "contacts-methods-update",
                "contacts/{contactId}/contact-methods/{contactMethodId}",
                "Update a contact method",
            ),
            _send(
                "DELETE",
                "contacts-methods-delete",
                "contacts/{contactId}/contact-methods/{contactMethodId}",
                "Delete a contact method",
                body=False,
            ),
            _get(
                "contacts-methods-preferences",
                "contacts/{contactId}/contact-methods/{contactMethodId}/preferences",
                "List a contact method's preferences",
            ),
            _get(
                "contacts-methods-preference-get",
                "contacts/{contactId}/contact-methods/{contactMethodId}/preferences/{preferenceName}",
                "Get one contact method preference",
            ),
            _send(
                "PATCH",
                "contacts-methods-preference-update",
                "contacts/{contactId}/contact-methods/{contactMethodId}/preferences/{preferenceName}",
                "Update one contact method preference",
            ),
            _list("contacts-methods-search", "contacts/contact-methods", "Search contact methods"),
            _get("contacts-preferences-metadata", "contacts/preferences", "Preference metadata"),
            _list(
                "contacts-by-relationship",
                "contacts/relationships/{relationshipId}",
                "List contacts for a relationship ID",
            ),
            _list(
                "contacts-relationships-list",
                "contacts/{contactId}/relationships",
                "List a contact's relationships",
            ),
            _send(
                "POST",
                "contacts-relationship-create",
                "contacts/{contactId}/relationships/{relatedEntityId}/{typeSlug}",
                "Relate a contact to a customer, location, …",
                body=False,
            ),
            _send(
                "DELETE",
                "contacts-relationship-delete",
                "contacts/{contactId}/relationships/{relatedEntityId}/{typeSlug}",
                "Remove a contact relationship",
                body=False,
            ),
            # leads
            _list("leads-notes-list", "leads/{id}/notes", "List a lead's notes"),
            _send("POST", "leads-form-submit", "leads/form", "Submit a lead form"),
            Endpoint(
                "leads-create-v3",
                "POST",
                "leads",
                body=True,
                version="v3",
                help="Create a lead shown under CRM > Leads (v3; v2 leads-create is legacy)",
            ),
            # bookings (hand-written has list/get; create/update go through a booking provider)
            _list("bookings-contacts-list", "bookings/{id}/contacts", "List a booking's contacts"),
            _list(
                "provider-bookings-list",
                "booking-provider/{bookingProvider}/bookings",
                "List bookings for a booking provider",
            ),
            _send(
                "POST",
                "provider-bookings-create",
                "booking-provider/{bookingProvider}/bookings",
                "Create a booking for a booking provider",
            ),
            _get(
                "provider-bookings-get",
                "booking-provider/{bookingProvider}/bookings/{id}",
                "Get a booking for a booking provider",
            ),
            _send(
                "PATCH",
                "provider-bookings-update",
                "booking-provider/{bookingProvider}/bookings/{id}",
                "Update a booking for a booking provider",
            ),
            _send(
                "POST",
                "provider-bookings-dismiss",
                "booking-provider/{bookingProvider}/bookings/{id}/dismiss",
                "Dismiss a booking for a booking provider",
            ),
            _list(
                "provider-bookings-contacts-list",
                "booking-provider/{bookingProvider}/bookings/{id}/contacts",
                "List a provider booking's contacts",
            ),
            _send(
                "POST",
                "provider-bookings-contacts-create",
                "booking-provider/{bookingProvider}/bookings/{id}/contacts",
                "Add a contact to a provider booking",
            ),
            _send(
                "PATCH",
                "provider-bookings-contacts-update",
                "booking-provider/{bookingProvider}/bookings/{id}/contacts/{contactId}",
                "Update a provider booking's contact",
            ),
            _send(
                "DELETE",
                "provider-bookings-contacts-delete",
                "booking-provider/{bookingProvider}/bookings/{id}/contacts/{contactId}",
                "Remove a contact from a provider booking",
                body=False,
            ),
        ),
        export_feeds=(
            "customers",
            "locations",
            "bookings",
            "leads",
            "customers/contacts",
            "locations/contacts",
        ),
    ),
    Module(
        name="jpm",
        group="jobs",
        help="Jobs — jobs, appointments, projects, job types, budget codes",
        resources=(
            Resource(
                "job-types",
                ops="LRCU",
                columns=(("ID", "id"), ("Name", "name"), ("Active", "active")),
                id_param="job_type_id",
            ),
            Resource("job-cancel-reasons", ops="L", columns=NAMED),
            Resource("job-hold-reasons", ops="L", columns=NAMED),
            # projects: hand-written has list/get
            Resource(
                "projects",
                ops="CU",
                columns=(("ID", "id"), ("Name", "name"), ("Status", "status")),
                id_param="project_id",
                actions=(
                    Action("note", path="notes", needs_body=True, help="Add a note to a project"),
                ),
            ),
            Resource("project-statuses", ops="LR", columns=NAMED, id_param="status_id"),
            Resource("project-substatuses", ops="LR", columns=NAMED, id_param="substatus_id"),
            Resource("project-types", ops="LR", columns=NAMED, id_param="type_id"),
            # appointments: hand-written has list/get
            Resource(
                "appointments",
                ops="CD",
                id_param="appointment_id",
                actions=(
                    Action(
                        "reschedule",
                        verb="PATCH",
                        needs_body=True,
                        help="Reschedule an appointment",
                    ),
                    Action("hold", verb="PUT", needs_body=True, help="Put an appointment on hold"),
                    Action("remove-hold", path="hold", verb="DELETE", help="Remove a hold"),
                    Action(
                        "confirm", path="confirmation", verb="PUT", help="Confirm an appointment"
                    ),
                    Action(
                        "remove-confirmation",
                        path="confirmation",
                        verb="DELETE",
                        help="Remove a confirmation",
                    ),
                    Action(
                        "special-instructions",
                        verb="PUT",
                        needs_body=True,
                        help="Set an appointment's special instructions",
                    ),
                    Action(
                        "summary",
                        path="summaries",
                        needs_body=True,
                        help="Set an appointment's work-performed summary (private preview)",
                    ),
                ),
            ),
        ),
        endpoints=(
            # jobs (hand-written has list/get/create/update/cancel)
            _send(
                "PUT",
                "job-remove-cancellation",
                "jobs/{id}/remove-cancellation",
                "Remove a job's cancellation",
                body=False,
            ),
            _list("job-notes-list", "jobs/{id}/notes", "List a job's notes"),
            _send("POST", "job-note-create", "jobs/{id}/notes", "Add a note to a job"),
            _get("job-history", "jobs/{id}/history", "A job's status history"),
            _list("job-canceled-log", "jobs/{id}/canceled-log", "A job's cancellation log"),
            _get("job-booked-log", "jobs/{id}/booked-log", "A job's booking log"),
            _get("job-equipment-list", "jobs/{id}/equipment", "Equipment IDs attached to a job"),
            _send("POST", "job-equipment-attach", "jobs/{id}/equipment", "Attach equipment"),
            _send("DELETE", "job-equipment-detach", "jobs/{id}/equipment", "Detach equipment"),
            _send(
                "DELETE",
                "job-equipment-detach-one",
                "jobs/{id}/equipment/{equipmentId}",
                "Detach one equipment item",
                body=False,
            ),
            _list("jobs-custom-fields", "jobs/custom-fields", "Job custom field types"),
            _get("jobs-hold-reasons-by-job", "jobs/hold-reasons", "Hold reasons for specific jobs"),
            _get(
                "jobs-cancel-reasons-by-job",
                "jobs/cancel-reasons",
                "Cancel reasons for specific jobs",
            ),
            # projects
            _list("projects-notes-list", "projects/{id}/notes", "List a project's notes"),
            _send(
                "POST",
                "projects-attach-job",
                "projects/{id}/attach-job/{jobId}",
                "Attach a job to a project",
                body=False,
            ),
            _send(
                "POST",
                "projects-detach-job",
                "projects/detach-job/{jobId}",
                "Detach a job from its project",
                body=False,
            ),
            _list("projects-custom-fields", "projects/custom-fields", "Project custom field types"),
            _list(
                "project-daily-logs-list",
                "projects/{projectId}/daily-logs",
                "List a project's daily logs",
            ),
            _get(
                "project-daily-log-get", "projects/{projectId}/daily-logs/{id}", "Get a daily log"
            ),
            _send(
                "PATCH",
                "project-daily-log-upsert",
                "projects/{projectId}/daily-logs/{date}",
                "Create or update the daily log for a date",
            ),
            _send(
                "POST",
                "project-daily-log-attachment-add",
                "projects/{projectId}/daily-logs/{id}/attachments",
                "Attach a file to a daily log",
            ),
            _get(
                "project-daily-log-attachment-get",
                "projects/{projectId}/daily-logs/{id}/attachments/{attachmentId}",
                "Download a daily log attachment",
            ),
            _send(
                "DELETE",
                "project-daily-log-attachment-delete",
                "projects/{projectId}/daily-logs/{id}/attachments/{attachmentId}",
                "Remove a daily log attachment",
                body=False,
            ),
            # work breakdown structure (budget codes)
            _list("wbs-segments", "work-breakdown-structure/segments", "Company WBS segments"),
            _list(
                "wbs-segment-items",
                "work-breakdown-structure/segments/{segmentId}/items",
                "Items in a company WBS segment",
            ),
            _list(
                "wbs-segment-item-children",
                "work-breakdown-structure/segments/{segmentId}/items/{segmentItemId}/children",
                "Children of a company WBS segment item",
            ),
            _list(
                "wbs-project-segments",
                "work-breakdown-structure/projects/{projectId}/segments",
                "A project's WBS segments",
            ),
            _list(
                "wbs-project-segment-items",
                "work-breakdown-structure/projects/{projectId}/segments/{segmentId}/items",
                "Items in a project WBS segment",
            ),
            _list(
                "wbs-project-segment-item-children",
                "work-breakdown-structure/projects/{projectId}/segments/{segmentId}"
                "/items/{segmentItemId}/children",
                "Children of a project WBS segment item",
            ),
            _list("budget-codes-list", "work-breakdown-structure/budget-codes", "Budget codes"),
            _send(
                "POST",
                "budget-codes-create",
                "work-breakdown-structure/budget-codes",
                "Create a budget code",
            ),
            _send(
                "POST",
                "budget-codes-create-partial",
                "work-breakdown-structure/budget-codes/partial",
                "Create a budget code from partial segments",
            ),
            _send(
                "POST",
                "budget-codes-create-batch",
                "work-breakdown-structure/budget-codes/batch",
                "Create many budget codes",
            ),
            _send(
                "POST",
                "budget-codes-create-partial-batch",
                "work-breakdown-structure/budget-codes/partial/batch",
                "Create many budget codes from partial segments",
            ),
            _get(
                "budget-codes-match",
                "work-breakdown-structure/budget-codes/match",
                "Match company budget codes",
            ),
            _list(
                "project-budget-codes-list",
                "work-breakdown-structure/projects/{projectId}/budget-codes",
                "A project's budget codes",
            ),
            _get(
                "project-budget-codes-match",
                "work-breakdown-structure/projects/{projectId}/budget-codes/match",
                "Match a project's budget codes",
            ),
        ),
        export_feeds=(
            "jobs",
            "appointments",
            "projects",
            "job-canceled-logs",
            "job-notes",
            "project-notes",
            "job-history",
        ),
    ),
    Module(
        name="dispatch",
        help="Dispatch — shifts, assignments, zones, teams, skills, arrival windows",
        resources=(
            Resource("shifts", path="technician-shifts", ops="RCUD", id_param="shift_id"),
            Resource("events", path="non-job-appointments", ops="RPD", id_param="event_id"),
            Resource(
                "assignments",
                path="appointment-assignments",
                actions=(
                    Action(
                        "assign-technicians",
                        needs_id=False,
                        needs_body=True,
                        help="Assign technicians to an appointment",
                    ),
                    Action(
                        "unassign-technicians",
                        needs_id=False,
                        needs_body=True,
                        help="Unassign technicians from an appointment",
                    ),
                ),
            ),
            Resource("zones", ops="RCUD", id_param="zone_id"),
            Resource("teams", ops="RCD", id_param="team_id"),
            # technician-skill ids are strings — get/delete are endpoints below
            Resource("skills", path="technician-skills", ops="LC"),
            Resource(
                "arrival-windows",
                ops="LRCP",
                id_param="arrival_window_id",
                actions=(
                    Action(
                        "activate",
                        path="activated",
                        verb="PUT",
                        needs_body=True,
                        help="Activate or deactivate an arrival window",
                    ),
                ),
            ),
            Resource("business-hours", ops="C"),
        ),
        endpoints=(
            _send(
                "POST",
                "shifts-bulk-delete",
                "technician-shifts/bulk-delete",
                "Delete technician shifts matching criteria",
            ),
            _get("skills-get", "technician-skills/{id}", "Get a technician skill"),
            _send(
                "DELETE",
                "skills-delete",
                "technician-skills/{id}",
                "Delete a technician skill association",
                body=False,
            ),
            _send(
                "PATCH",
                "skills-assign",
                "technician-skills",
                "Assign or replace skills on a technician",
            ),
            _get(
                "arrival-windows-config", "arrival-windows/configuration", "Arrival window config"
            ),
            _send(
                "POST",
                "arrival-windows-config-update",
                "arrival-windows/configuration",
                "Update arrival window configuration",
            ),
            _get("business-hours-get", "business-hours", "Get the business hours"),
            _get("technician-tracking", "technician-tracking", "Technician GPS tracking"),
            _send(
                "POST",
                "gps-pings-create",
                "gps-provider/{gpsProvider}/gps-pings",
                "Send GPS pings from a GPS provider",
            ),
        ),
        export_feeds=("appointment-assignments",),
    ),
    Module(
        name="accounting",
        help="Accounting — invoices, payments, GL, journal entries, AP, expenses",
        resources=(
            # invoices: hand-written has list/get
            Resource(
                "invoices",
                ops="CU",
                columns=DOC,
                id_param="invoice_id",
                actions=(_mark_exported("invoices"),),
            ),
            # payments: hand-written has list
            Resource(
                "payments",
                ops="U",
                columns=(("ID", "id"), ("Amount", "total"), ("Status", "status")),
                id_param="payment_id",
                actions=(
                    Action(
                        "update-status",
                        path="status",
                        needs_id=False,
                        needs_body=True,
                        help="Update payment statuses",
                    ),
                ),
            ),
            Resource("gl-accounts", ops="LRCU", id_param="gl_account_id"),
            Resource("gl-account-types", path="gl-accounts/types", ops="L"),
            # journal-entry ids are strings — single-record ops are endpoints below
            Resource(
                "journal-entries",
                ops="LC",
                columns=(("ID", "id"), ("Name", "name"), ("Status", "status")),
            ),
            Resource(
                "credit-memos",
                ops="LU",
                columns=DOC,
                id_param="credit_memo_id",
                actions=(_mark_exported("credit memos"),),
            ),
            Resource(
                "ap-bills",
                ops="LR",
                columns=DOC,
                id_param="ap_bill_id",
                actions=(_mark_exported("AP bills"),),
            ),
            Resource("ap-credits", ops="L", columns=DOC, actions=(_mark_exported("AP credits"),)),
            Resource("ap-payments", ops="L", columns=DOC, actions=(_mark_exported("AP payments"),)),
            Resource(
                "inventory-bills",
                ops="L",
                columns=DOC,
                actions=(_mark_exported("inventory bills"),),
            ),
            Resource("bank-deposits", ops="L", actions=(_mark_exported("bank deposits"),)),
            Resource(
                "expense-transactions",
                ops="LR",
                columns=TXN,
                id_param="expense_id",
                actions=(_mark_exported("expense transactions"),),
            ),
            Resource("payment-terms", ops="LR", id_param="term_id"),
            Resource("payment-types", ops="LR", id_param="payment_type_id"),
            Resource("remittance-vendors", ops="LR", id_param="vendor_id"),
            Resource(
                "tax-zones",
                ops="L",
                actions=(
                    Action(
                        "resolve",
                        needs_id=False,
                        needs_body=True,
                        help="Resolve the tax zone for a street address",
                    ),
                ),
            ),
        ),
        endpoints=(
            _send(
                "PATCH",
                "invoices-items-update",
                "invoices/{invoiceId}/items",
                "Update an invoice's items",
            ),
            _send(
                "DELETE",
                "invoices-item-delete",
                "invoices/{invoiceId}/items/{itemId}",
                "Delete an invoice item",
                body=False,
            ),
            _list("invoices-tasks-list", "invoices/{invoiceId}/tasks", "List an invoice's tasks"),
            _send(
                "POST",
                "invoices-tasks-create",
                "invoices/{invoiceId}/tasks",
                "Create an invoice task from a template",
            ),
            _send(
                "PATCH",
                "invoices-tasks-update",
                "invoices/{invoiceId}/tasks/{taskId}",
                "Update an invoice task",
            ),
            *_custom_fields("invoices", "invoices"),
            *_custom_fields("payments", "payments"),
            *_custom_fields("credit-memos", "credit-memos"),
            *_custom_fields("ap-bills", "ap-bills"),
            *_custom_fields("ap-credits", "ap-credits"),
            *_custom_fields("ap-payments", "ap-payments"),
            *_custom_fields("inventory-bills", "inventory-bills"),
            *_custom_fields("expense-transactions", "expense-transactions"),
            _list("credit-memos-items", "credit-memos/{id}/items", "A credit memo's items"),
            _list(
                "credit-memos-items-all",
                "credit-memos/credit-memo-items",
                "Items across many credit memos",
            ),
            _send("POST", "credit-memos-splits", "credit-memos/{id}/splits", "Add splits"),
            _list(
                "bank-deposits-transactions",
                "bank-deposits/{id}/transactions",
                "A bank deposit's transactions",
            ),
            _list(
                "inventory-bills-paginated",
                "inventory-bills/paginated",
                "Inventory bills (paginated variant)",
            ),
            _get("gl-accounts-well-known", "gl-accounts/well-known", "Well-known GL accounts"),
            _get("journal-entries-get", "journal-entries/{id}", "Get a journal entry"),
            _send("PATCH", "journal-entries-update", "journal-entries/{id}", "Update an entry"),
            _send(
                "PUT",
                "journal-entries-replace",
                "journal-entries/{id}",
                "Replace an external journal entry (send every line)",
            ),
            _send(
                "DELETE",
                "journal-entries-delete",
                "journal-entries/{id}",
                "Delete an external journal entry",
                body=False,
            ),
            _list(
                "journal-entries-summary",
                "journal-entries/{id}/summary",
                "Entry items aggregated by account and business unit",
            ),
            _list(
                "journal-entries-details",
                "journal-entries/{id}/details",
                "Entry items aggregated by account, business unit and more",
            ),
            _send(
                "PATCH",
                "journal-entries-sync",
                "journal-entries/{id}/sync",
                "Update a journal entry's sync state",
            ),
        ),
        export_feeds=("invoices", "invoice-items", "payments", "inventory-bills"),
    ),
    Module(
        name="memberships",
        help="Memberships — customer memberships, recurring services, invoice templates",
        resources=(
            # memberships: hand-written has list/get
            Resource(
                "memberships",
                ops="U",
                columns=(("ID", "id"), ("Status", "status")),
                id_param="membership_id",
            ),
            Resource("membership-types", ops="R", id_param="type_id"),
            Resource("invoice-templates", ops="RCU", id_param="template_id"),
            Resource("recurring-services", ops="LRU", id_param="service_id"),
            Resource(
                "recurring-service-events",
                ops="L",
                actions=(
                    Action("mark-complete", needs_body=True, help="Mark service event complete"),
                    Action(
                        "mark-incomplete", needs_body=True, help="Mark service event incomplete"
                    ),
                ),
            ),
            Resource("recurring-service-types", ops="LR", id_param="type_id"),
        ),
        endpoints=(
            _list(
                "memberships-custom-fields", "memberships/custom-fields", "Membership custom fields"
            ),
            _get(
                "memberships-status-changes",
                "memberships/{id}/status-changes",
                "A membership's status changes",
            ),
            _send(
                "POST", "memberships-sale", "memberships/sale", "Create a membership sale invoice"
            ),
            _get(
                "invoice-templates-list",
                "invoice-templates",
                "Invoice templates by IDs (pass --filter ids=1,2)",
            ),
            _get(
                "membership-types-recurring-service-items",
                "membership-types/{id}/recurring-service-items",
                "Recurring services included in a membership type",
            ),
            _get(
                "membership-types-discounts",
                "membership-types/{id}/discounts",
                "A membership type's discounts",
            ),
            _get(
                "membership-types-duration-billing-items",
                "membership-types/{id}/duration-billing-items",
                "A membership type's duration/billing options",
            ),
        ),
        export_feeds=(
            "memberships",
            "membership-types",
            "membership-status-changes",
            "invoice-templates",
            "recurring-services",
            "recurring-service-types",
            "recurring-service-events",
        ),
    ),
    Module(
        name="reporting",
        help="Reporting — report categories, reports, report data",
        endpoints=(
            _list(
                "dynamic-value-set",
                "dynamic-value-sets/{dynamicSetId}",
                "Values of a dynamic value set (for report parameters)",
            ),
            _send(
                "POST",
                "data-query-start",
                "report-category/{reportCategory}/reports/{reportId}/data/query",
                "Start a long-running report data query (returns a token to poll)",
            ),
            _get(
                "data-query-result",
                "data-queries/{token}",
                "Poll a long-running report data query",
            ),
            _send(
                "DELETE",
                "data-query-cancel",
                "data-queries/{token}",
                "Cancel a long-running report data query",
                body=False,
            ),
        ),
    ),
    Module(
        name="settings",
        help="Settings — employees, technicians, business units, tag types",
        resources=(
            Resource(
                "employees",
                ops="LRCU",
                id_param="employee_id",
                actions=(
                    Action(
                        "account-action",
                        path="account-actions",
                        needs_body=True,
                        help="Perform an account action (e.g. activate, deactivate)",
                    ),
                ),
            ),
            Resource(
                "technicians",
                ops="LRCU",
                id_param="technician_id",
                actions=(
                    Action(
                        "account-action",
                        path="account-actions",
                        needs_body=True,
                        help="Perform an account action (e.g. activate, deactivate)",
                    ),
                ),
            ),
            Resource("tag-types", ops="LCU", id_param="tag_type_id"),
            # business-units: hand-written CLI has list, MCP has list+get
            Resource("business-units", ops="U", id_param="business_unit_id"),
            Resource("user-roles", ops="L"),
        ),
        endpoints=(
            _list("employees-custom-fields", "employees/custom-fields", "Employee custom fields"),
            _list(
                "technicians-custom-fields", "technicians/custom-fields", "Technician custom fields"
            ),
            _list(
                "business-units-intacct",
                "business-units/intacct",
                "Intacct business unit mappings",
            ),
        ),
        export_feeds=("employees", "technicians", "business-units", "tag-types"),
    ),
)


# ===========================================================================
# MODULES — brand-new groups (full specs) with no hand-written app.
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
            Resource("materials-markup", path="materialsmarkup", ops="LRCP", id_param="markup_id"),
            Resource(
                "client-specific-pricing",
                path="clientspecificpricing",
                ops="LU",
                id_param="rate_sheet_id",
            ),
            Resource("images", ops="C"),
        ),
        endpoints=(
            _get("images-download", "images", "Download a pricebook image (--filter path=…)"),
            _get("materials-cost-types", "materials/costtypes", "Material cost types"),
            _send("POST", "bulk-create", "pricebook", "Bulk-create pricebook items"),
            _send("PATCH", "bulk-update", "pricebook", "Bulk-update pricebook items"),
        ),
        export_feeds=("services", "materials", "equipment", "categories"),
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
                    Action(
                        "cancel",
                        path="cancellation",
                        verb="PATCH",
                        needs_body=True,
                        help="Cancel a purchase order",
                    ),
                ),
            ),
            Resource(
                "purchase-order-requests",
                path="purchase-orders/requests",
                ops="L",
                columns=DOC,
                actions=(
                    Action("approve", verb="PATCH", help="Approve a purchase order request"),
                    Action(
                        "reject",
                        verb="PATCH",
                        needs_body=True,
                        help="Reject a purchase order request",
                    ),
                ),
            ),
            Resource("purchase-order-markups", ops="LRCUD", id_param="markup_id"),
            Resource("purchase-order-types", ops="LCU", id_param="po_type_id"),
            Resource(
                "receipts",
                ops="LC",
                columns=DOC,
                actions=(
                    Action(
                        "cancel",
                        path="cancellation",
                        verb="PATCH",
                        needs_body=True,
                        help="Cancel a receipt",
                    ),
                ),
            ),
            Resource(
                "returns",
                ops="LCU",
                columns=DOC,
                id_param="return_id",
                actions=(
                    Action(
                        "cancel",
                        path="cancellation",
                        verb="PATCH",
                        needs_body=True,
                        help="Cancel a return",
                    ),
                ),
            ),
            Resource("return-types", ops="LCU", id_param="return_type_id"),
            Resource("adjustments", ops="LCU", id_param="adjustment_id"),
            Resource("transfers", ops="LU", id_param="transfer_id"),
            Resource("trucks", ops="LCU", id_param="truck_id"),
            Resource("vendors", ops="LRCU", id_param="vendor_id"),
            Resource("warehouses", ops="LU", id_param="warehouse_id"),
            Resource("inventory-templates", ops="L"),
        ),
        endpoints=(
            *_custom_fields("purchase-orders", "purchase-orders", read=False),
            *_custom_fields("receipts", "receipts", read=False),
            *_custom_fields("returns", "returns", read=False),
            *_custom_fields("adjustments", "adjustments", read=False),
            *_custom_fields("transfers", "transfers", read=False),
            *_custom_fields("vendors", "vendors"),
        ),
        export_feeds=("purchase-orders", "receipts", "returns", "transfers", "adjustments"),
    ),
    Module(
        name="sales",
        group="salestech",
        help="Sales & Estimates — estimates, estimate/proposal templates, contracts",
        resources=(
            Resource(
                "estimates",
                ops="LRCP",
                columns=DOC,
                id_param="estimate_id",
                date_filter=True,
                actions=(
                    Action("sell", verb="PUT", needs_body=True, help="Mark an estimate as sold"),
                    Action("unsell", verb="PUT", help="Reverse a sold estimate"),
                    Action("dismiss", verb="PUT", help="Dismiss an estimate"),
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
        ),
        endpoints=(
            _list("estimates-items", "estimates/items", "Line items across estimates"),
            _send(
                "DELETE",
                "estimates-item-delete",
                "estimates/{id}/items/{itemId}",
                "Delete an estimate line item",
                body=False,
            ),
            _get(
                "estimates-status-changes",
                "status/estimates/{id}/changes",
                "An estimate's status changes with UTC timestamps",
            ),
            _get(
                "estimates-export-legacy",
                "estimates/export",
                "Legacy estimates export feed (prefer export-estimates)",
            ),
            _get("proposal-types-list", "proposal-types", "Proposal types"),
            _get("contracts-list", "contracts", "Contracts owned by a job, with statuses"),
        ),
        export_feeds=("estimates",),
    ),
    Module(
        name="payroll",
        help="Payroll — gross pay items, adjustments, settings, timesheets, splits",
        resources=(
            Resource(
                "gross-pay-items",
                ops="LCPD",
                id_param="item_id",
                date_filter=True,
                default_sort="-date",  # endpoint only accepts ±date for sort
            ),
            Resource("payroll-adjustments", ops="LRCPD", id_param="adjustment_id"),
            Resource("payrolls", ops="L"),
            Resource("payroll-settings", ops="L"),
            Resource("labor-types", ops="LRCP", id_param="labor_type_id"),
            Resource("job-splits", path="jobs/splits", ops="L"),
            Resource("job-timesheets", path="jobs/timesheets", ops="L"),
            Resource("non-job-timesheets", ops="L"),
            Resource("location-rates", path="locations/rates", ops="L"),
            Resource("activity-codes", ops="LR", id_param="code_id"),
            Resource("timesheet-codes", ops="LR", id_param="code_id"),
        ),
        endpoints=(
            _list("employee-payrolls", "employees/{employee}/payrolls", "An employee's payrolls"),
            _list(
                "technician-payrolls",
                "technicians/{technician}/payrolls",
                "A technician's payrolls",
            ),
            _get(
                "employee-payroll-settings",
                "employees/{employee}/payroll-settings",
                "An employee's payroll settings",
            ),
            _send(
                "PUT",
                "employee-payroll-settings-update",
                "employees/{employee}/payroll-settings",
                "Update an employee's payroll settings",
            ),
            _get(
                "technician-payroll-settings",
                "technicians/{technician}/payroll-settings",
                "A technician's payroll settings",
            ),
            _send(
                "PUT",
                "technician-payroll-settings-update",
                "technicians/{technician}/payroll-settings",
                "Update a technician's payroll settings",
            ),
            _list("job-splits-for-job", "jobs/{job}/splits", "Splits for one job"),
            _list("job-timesheets-for-job", "jobs/{job}/timesheets", "Timesheets for one job"),
        ),
        export_feeds=(
            "gross-pay-items",
            "payroll-adjustments",
            "payroll-settings",
            "activity-codes",
            "timesheet-codes",
            "jobs/splits",
            "jobs/timesheets",
        ),
    ),
    Module(
        name="marketing",
        help="Marketing — campaigns, categories, costs, SMS opt-ins",
        resources=(
            Resource("campaigns", ops="LRCU", id_param="campaign_id"),
            Resource("categories", ops="LRCU", id_param="category_id"),
            Resource("costs", ops="LRCU", id_param="cost_id"),
        ),
        endpoints=(
            _list("campaigns-costs", "campaigns/{id}/costs", "A campaign's costs"),
            _get("campaign-cost-summary", "campaign-cost-summary", "Campaign cost summary"),
            _get("email-channel-cost", "email-channel-cost", "Email channel cost"),
            _send("POST", "sms-optin-import", "sms/optin/import", "Import external SMS opt-ins"),
        ),
    ),
    Module(
        name="marketing-ads",
        url="marketingads",
        help="Marketing Ads — attribution & performance analytics",
        resources=(
            Resource("attributed-leads", ops="L"),
            Resource("performance", ops="L"),
            Resource("external-call-attributions", ops="C"),
            Resource("job-attributions", ops="C"),
            Resource("web-booking-attributions", ops="C"),
            Resource("web-lead-form-attributions", ops="C"),
        ),
        endpoints=(_get("capacity-warnings", "capacity-warnings", "Capacity awareness warnings"),),
    ),
    Module(
        name="timesheets",
        help="Timesheets — activities, activity categories/types",
        resources=(
            Resource("activities", ops="LRCPD", id_param="activity_id", date_filter=True),
            Resource("activity-categories", ops="LR", id_param="category_id"),
            Resource("activity-types", ops="LR", id_param="type_id"),
        ),
        export_feeds=("activities", "activity-categories", "activity-types"),
    ),
    Module(
        name="equipment-systems",
        url="equipmentsystems",
        help="Equipment Systems — equipment systems, installed equipment, equipment types",
        resources=(
            Resource(
                "equipment-systems",
                ops="LRCUD",
                id_param="system_id",
                actions=(
                    Action(
                        "add-equipment",
                        path="equipment",
                        needs_body=True,
                        help="Add equipment to an equipment system",
                    ),
                    Action(
                        "remove-equipment",
                        path="equipment",
                        verb="DELETE",
                        needs_body=True,
                        help="Remove equipment from an equipment system",
                    ),
                ),
            ),
            Resource(
                "installed-equipment",
                ops="LRCU",
                id_param="equipment_id",
                actions=(
                    Action(
                        "bulk-create",
                        path="bulk",
                        needs_id=False,
                        needs_body=True,
                        help="Create up to 1000 installed equipment records atomically",
                    ),
                    Action(
                        "attachment-upload",
                        path="attachments",
                        needs_id=False,
                        needs_body=True,
                        help="Upload an installed-equipment attachment",
                    ),
                ),
            ),
            Resource("equipment-types", ops="LRCU", id_param="type_id"),
        ),
        endpoints=(
            _list(
                "equipment-systems-custom-field-types",
                "equipment-systems/custom-field-types",
                "Equipment system custom field types",
            ),
            _list(
                "installed-equipment-custom-field-types",
                "installed-equipment/custom-field-types",
                "Installed equipment custom field types",
            ),
            _get(
                "installed-equipment-attachment-download",
                "installed-equipment/attachments",
                "Download an installed-equipment attachment (--filter path=…)",
            ),
        ),
        export_feeds=("installed-equipment", "equipment-systems"),
    ),
    Module(
        name="findings",
        help="Findings — location findings and their attachments, assets",
        resources=(Resource("location-findings", ops="LRCU", id_param="finding_id"),),
        endpoints=(
            *_nested_crud(
                "location-findings-attachments",
                "location-findings",
                "attachments",
                "LCUD",
                "finding attachments",
            ),
            _get(
                "location-findings-attachment-get",
                "location-findings/{id}/attachments/{childId}",
                "Get a finding attachment",
            ),
            _get("assets-download", "assets", "Download an asset by path (--filter path=…)"),
            _send("POST", "assets-upload", "assets", "Upload a file for use in findings"),
        ),
    ),
    Module(
        name="fleet-pro",
        url="fleetpro",
        help="Fleet Pro — vehicles, historical GPS and events",
        endpoints=(
            _get("vehicles-list", "vehicles", "All Fleet Pro vehicles"),
            _send("POST", "gps-history", "gps", "Historical GPS data older than 7 days"),
            _send("POST", "events-history", "events", "Historical event data older than 7 days"),
        ),
    ),
    Module(
        name="task-management",
        url="taskmanagement",
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
        ),
        endpoints=(_get("client-side-data", "data", "Lookup data (task types, priorities, …)"),),
    ),
    Module(
        name="telecom",
        help="Telecom — calls, recordings, opt-outs",
        resources=(
            Resource(
                "calls",
                ops="L",
                version="v3",
                columns=(("ID", "id"), ("From", "from"), ("To", "to"), ("Created", "createdOn")),
                date_filter=True,
            ),
        ),
        endpoints=(
            _get("calls-get", "calls/{id}", "Get a call's details"),
            _send("PUT", "calls-update", "calls/{id}", "Update a call"),
            _get("calls-recording", "calls/{id}/recording", "Get a call's recording"),
            _get("calls-voicemail", "calls/{id}/voicemail", "Get a call's voicemail"),
            Endpoint("optouts-list", "GET", "optinouts/optouts", version="v3", help="All opt-outs"),
            Endpoint(
                "optouts-add",
                "POST",
                "optinouts/optouts",
                body=True,
                version="v3",
                help="Add opt-outs for phone numbers",
            ),
            Endpoint(
                "optouts-status",
                "POST",
                "optinouts/optouts/getlist",
                body=True,
                version="v3",
                help="Opt-out status for each phone number",
            ),
        ),
        export_feeds=("calls",),
    ),
    Module(
        name="customer-interactions",
        help="Customer Interactions — technician ratings",
        resources=(Resource("technician-ratings", ops="LC"),),
        endpoints=(
            _send(
                "PUT",
                "technician-rating-upsert",
                "technician-rating/technician/{technicianId}/job/{jobId}",
                "Add or update a technician's rating for a job",
            ),
        ),
        export_feeds=("technician-ratings",),
    ),
    Module(
        name="forms",
        help="Forms — form definitions, submissions, job attachments",
        resources=(
            Resource("forms", ops="L"),
            Resource("submissions", ops="L"),
        ),
        endpoints=(
            _list("job-attachments-list", "jobs/{jobId}/attachments", "A job's attachments"),
            _send("POST", "job-attachments-create", "jobs/{id}/attachments", "Attach to a job"),
            _send(
                "DELETE",
                "job-attachments-delete",
                "jobs/{id}/attachments/{attachmentId}",
                "Delete a job attachment",
                body=False,
            ),
            _get("job-attachment-download", "jobs/attachment/{id}", "Download a job attachment"),
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
        url="marketingreputation",
        help="Marketing Reputation — online reviews (read-only)",
        resources=(Resource("reviews", ops="L", date_filter=True),),
    ),
    Module(
        name="scheduling-pro",
        url="schedulingpro",
        help="Scheduling Pro — schedulers, routers, sessions, performance (read-only)",
        resources=(Resource("schedulers", ops="L"),),
        endpoints=(
            _list("scheduler-sessions", "schedulers/{id}/sessions", "A scheduler's sessions"),
            _get("scheduler-performance", "schedulers/{id}/performance", "Scheduler performance"),
            _list("router-sessions", "routers/{id}/sessions", "A router's sessions"),
            _get("router-performance", "routers/{id}/performance", "Router performance"),
        ),
    ),
    Module(
        name="service-agreements",
        help="Service Agreements — agreements (read-only)",
        resources=(
            Resource("service-agreements", ops="LR", id_param="agreement_id", date_filter=True),
        ),
        endpoints=(
            _list(
                "service-agreements-custom-fields",
                "service-agreements/custom-fields",
                "Service agreement custom field types",
            ),
        ),
        export_feeds=("service-agreements",),
    ),
)


def all_modules() -> tuple[Module, ...]:
    """Every module spec the engine should process (extensions + new)."""
    return EXTENSIONS + MODULES

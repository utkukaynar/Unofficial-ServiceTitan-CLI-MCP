"""Check the registry against ServiceTitan's own OpenAPI documents.

The specs are downloaded from developer.servicetitan.io into ``specs/`` and are
deliberately not committed (ServiceTitan's API Terms treat API documentation as
confidential — see AGENTS.md). Without them this module is skipped.

What it guards:

* every operation st-cli sends exists in a spec, with the same verb, module
  URL segment and API version (the class of bug that shipped 119 dead calls);
* every spec operation is reachable — from the registry, or from the explicit
  hand-written / intentionally-omitted lists below — so a refreshed spec that
  adds endpoints fails loudly instead of silently going uncovered;
* list commands only target paginated endpoints, and date-filtered lists accept
  their date keys and the default sort field.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from functools import cache
from pathlib import Path
from typing import Any

import pytest

from st_cli.registry import Module, all_modules

SPECS_DIR = Path(__file__).resolve().parent.parent / "specs"

pytestmark = pytest.mark.skipif(
    not any(SPECS_DIR.glob("*.json")),
    reason="ServiceTitan OpenAPI specs not downloaded into specs/ (see AGENTS.md)",
)

# (verb, url module, version, path with {} for every placeholder)
OpKey = tuple[str, str, str, str]

_PLACEHOLDER = re.compile(r"\{[^}]*\}")
_VERBS = ("get", "post", "put", "patch", "delete")

# Operations served by the hand-written commands/tools in commands/*.py and
# mcp_server.py. Each one is also checked against the specs below.
HANDWRITTEN: frozenset[OpKey] = frozenset(
    {
        ("GET", "crm", "v2", "customers"),
        ("GET", "crm", "v2", "customers/{}"),
        ("POST", "crm", "v2", "customers"),
        ("PATCH", "crm", "v2", "customers/{}"),
        ("GET", "crm", "v2", "locations"),
        ("GET", "crm", "v2", "locations/{}"),
        ("GET", "crm", "v2", "bookings"),
        ("GET", "crm", "v2", "bookings/{}"),
        ("GET", "crm", "v2", "contacts"),
        ("GET", "crm", "v2", "contacts/{}"),
        ("GET", "jpm", "v2", "jobs"),
        ("GET", "jpm", "v2", "jobs/{}"),
        ("POST", "jpm", "v2", "jobs"),
        ("PATCH", "jpm", "v2", "jobs/{}"),
        ("PUT", "jpm", "v2", "jobs/{}/cancel"),
        ("GET", "jpm", "v2", "appointments"),
        ("GET", "jpm", "v2", "appointments/{}"),
        ("GET", "jpm", "v2", "projects"),
        ("GET", "jpm", "v2", "projects/{}"),
        ("GET", "dispatch", "v2", "technician-shifts"),
        ("GET", "dispatch", "v2", "appointment-assignments"),
        ("GET", "dispatch", "v2", "non-job-appointments"),
        ("POST", "dispatch", "v2", "non-job-appointments"),
        ("GET", "dispatch", "v2", "zones"),
        ("GET", "dispatch", "v2", "teams"),
        ("POST", "dispatch", "v2", "capacity"),
        ("GET", "accounting", "v2", "invoices"),
        ("GET", "accounting", "v2", "payments"),
        ("GET", "memberships", "v2", "memberships"),
        ("GET", "memberships", "v2", "memberships/{}"),
        ("GET", "memberships", "v2", "membership-types"),
        ("GET", "reporting", "v2", "report-categories"),
        ("GET", "reporting", "v2", "report-category/{}/reports"),
        ("GET", "reporting", "v2", "report-category/{}/reports/{}"),
        ("POST", "reporting", "v2", "report-category/{}/reports/{}/data"),
        ("GET", "settings", "v2", "business-units"),
        ("GET", "settings", "v2", "business-units/{}"),
    }
)

# Spec operations st-cli deliberately does not wrap, with the reason.
INTENTIONALLY_OMITTED: dict[OpKey, str] = {
    ("GET", "telecom", "v2", "calls"): "superseded by the v3 calls feed (supports sort)",
}

# Endpoints whose request body the spec doesn't declare even though the
# operation clearly takes one (a batch create with nothing to create).
SPEC_BODY_GAPS: frozenset[OpKey] = frozenset(
    {
        ("POST", "jpm", "v2", "work-breakdown-structure/budget-codes/batch"),
        ("POST", "jpm", "v2", "work-breakdown-structure/budget-codes/partial/batch"),
    }
)


def _norm(path: str) -> str:
    return _PLACEHOLDER.sub("{}", path.strip("/"))


@cache
def spec_ops() -> dict[OpKey, dict[str, Any]]:
    """Every operation across the downloaded specs, keyed like the registry."""
    ops: dict[OpKey, dict[str, Any]] = {}
    for spec_file in sorted(SPECS_DIR.glob("*.json")):
        spec = json.loads(spec_file.read_text())
        # servers look like https://api.servicetitan.io/crm or …/sales/v2
        module = spec["servers"][0]["url"].split(".io/", 1)[1].split("/")[0]
        for raw_path, item in spec["paths"].items():
            match = re.match(r"^/(v\d+)(/.*)$", raw_path)
            version, path = (match.group(1), match.group(2)) if match else ("v2", raw_path)
            path = re.sub(r"^/tenant/\{tenant\}/?", "", path)
            for verb in _VERBS:
                if verb in item:
                    ops[(verb.upper(), module, version, _norm(path))] = item[verb]
    return ops


def _query_params(op: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {p["name"]: p for p in op.get("parameters", []) if p.get("in") == "query"}


def _is_paged(op: dict[str, Any]) -> bool:
    return "page" in _query_params(op)


def registry_ops() -> Iterator[tuple[str, Module, OpKey]]:
    """Yield (label, module, key) for every operation the registry generates."""
    crud = {"R": "GET", "U": "PATCH", "P": "PUT", "D": "DELETE"}
    for module in all_modules():
        api = module.api_module
        for res in module.resources:
            base = res.api_path
            if "L" in res.ops:
                yield f"{res.slug} list", module, ("GET", api, res.version, _norm(base))
            if "C" in res.ops:
                yield f"{res.slug} create", module, ("POST", api, res.version, _norm(base))
            for letter, verb in crud.items():
                if letter in res.ops:
                    key = (verb, api, res.version, _norm(f"{base}/{{id}}"))
                    yield f"{res.slug} {verb}", module, key
            for action in res.actions:
                path = (
                    f"{base}/{{id}}/{action.subpath}"
                    if action.needs_id
                    else (f"{base}/{action.subpath}")
                )
                key = (action.verb, api, res.version, _norm(path))
                yield f"{res.slug} {action.name}", module, key
        for ep in module.endpoints:
            yield ep.name, module, (ep.verb, api, ep.version, _norm(ep.path))
        for feed in module.export_feeds:
            yield f"export {feed}", module, ("GET", api, "v2", f"export/{feed}")


class TestRegistryMatchesSpecs:
    def test_every_registry_operation_exists(self):
        ops = spec_ops()
        missing = [
            f"{module.name}: {label} -> {key[0]} /{key[1]}/{key[2]}/{key[3]}"
            for label, module, key in registry_ops()
            if key not in ops
        ]
        assert not missing, "operations not in any spec:\n" + "\n".join(missing)

    def test_every_handwritten_operation_exists(self):
        ops = spec_ops()
        assert not sorted(HANDWRITTEN - ops.keys())

    def test_intentional_omissions_still_exist(self):
        """Drop an entry here once ServiceTitan removes the endpoint."""
        assert not sorted(INTENTIONALLY_OMITTED.keys() - spec_ops().keys())

    def test_every_spec_operation_is_covered(self):
        covered = {key for _, _, key in registry_ops()} | HANDWRITTEN
        uncovered = sorted(spec_ops().keys() - covered - INTENTIONALLY_OMITTED.keys())
        assert not uncovered, "spec operations st-cli doesn't expose:\n" + "\n".join(
            f"{v} /{m}/{ver}/{p}" for v, m, ver, p in uncovered
        )


class TestOperationShapes:
    def test_list_resources_target_paginated_endpoints(self):
        ops = spec_ops()
        for module in all_modules():
            for res in module.resources:
                if "L" in res.ops:
                    key = ("GET", module.api_module, res.version, _norm(res.api_path))
                    assert _is_paged(ops[key]), f"{module.name}.{res.slug} list isn't paginated"

    def test_endpoint_paged_flag_matches_spec(self):
        ops = spec_ops()
        for module in all_modules():
            for ep in module.endpoints:
                key = (ep.verb, module.api_module, ep.version, _norm(ep.path))
                if ep.verb == "GET":
                    assert ep.paged == _is_paged(ops[key]), f"{module.name}.{ep.name}"

    def test_endpoint_body_flag_matches_spec(self):
        ops = spec_ops()
        for module in all_modules():
            for ep in module.endpoints:
                key = (ep.verb, module.api_module, ep.version, _norm(ep.path))
                spec_body = "requestBody" in ops[key] or key in SPEC_BODY_GAPS
                assert ep.body == spec_body, f"{module.name}.{ep.name}"

    def test_action_body_flag_matches_spec(self):
        ops = spec_ops()
        for module in all_modules():
            for res in module.resources:
                for action in res.actions:
                    path = (
                        f"{res.api_path}/{{id}}/{action.subpath}"
                        if action.needs_id
                        else f"{res.api_path}/{action.subpath}"
                    )
                    key = (action.verb, module.api_module, res.version, _norm(path))
                    spec_body = "requestBody" in ops[key]
                    assert action.needs_body == spec_body, f"{module.name}.{res.slug}.{action.name}"


class TestDateFilteredLists:
    def _list_op(self, module: Module, slug: str) -> dict[str, Any]:
        res = next(r for r in module.resources if r.slug == slug)
        return spec_ops()[("GET", module.api_module, res.version, _norm(res.api_path))]

    def test_date_keys_are_accepted(self):
        for module in all_modules():
            for res in module.resources:
                if "L" in res.ops and res.date_filter:
                    params = _query_params(self._list_op(module, res.slug))
                    missing = set(res.date_keys) - params.keys()
                    assert not missing, f"{module.name}.{res.slug}: {missing}"

    def test_default_sort_field_is_allowed(self):
        """When the spec lists sortable fields, the default sort must be one of them.

        A field outside the enum 400s — the payroll/gross-pay-items bug.
        """
        for module in all_modules():
            for res in module.resources:
                if not ("L" in res.ops and res.date_filter):
                    continue
                params = _query_params(self._list_op(module, res.slug))
                assert "sort" in params, f"{module.name}.{res.slug} has no sort param"
                desc = params["sort"].get("description") or ""
                listed = re.search(r"(?:Available fields are|possible values):([^.]*)", desc)
                if not listed:
                    continue
                allowed = {f.strip().lower() for f in listed.group(1).split(",")}
                field = (res.default_sort or "-modifiedOn").lstrip("+-").lower()
                assert field in allowed, f"{module.name}.{res.slug}: {field} not in {allowed}"

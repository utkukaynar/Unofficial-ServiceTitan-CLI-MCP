"""The Endpoint archetype (path templates), module URL segments, API versions.

These cover everything the CRUD archetypes can't express: parent IDs in the
path, string IDs, bulk operations without an ID, and v3-only endpoints.
"""

from __future__ import annotations

import asyncio

import pytest
from fastmcp.exceptions import ToolError

from st_cli import engine
from st_cli.exceptions import UsageError
from st_cli.registry import Endpoint
from tests.conftest import make_envelope


def _tool_names() -> dict[str, object]:
    import st_cli.mcp_server as server

    return {t.name: t for t in asyncio.run(server.mcp.list_tools())}


# ---------------------------------------------------------------------------
# Module URL segment, API version, nested export feeds
# ---------------------------------------------------------------------------


class TestRoutingDetails:
    @pytest.mark.parametrize(
        ("group", "command", "url"),
        [
            ("equipment-systems", "equipment-types-list", "equipmentsystems"),
            ("task-management", "tasks-list", "taskmanagement"),
            ("scheduling-pro", "schedulers-list", "schedulingpro"),
            ("marketing-ads", "attributed-leads-list", "marketingads"),
            ("marketing-reputation", "reviews-list", "marketingreputation"),
        ],
    )
    def test_module_url_drops_hyphen(self, invoke, mock_client, group, command, url):
        """ServiceTitan serves these modules without the hyphen (e.g. /equipmentsystems/v2)."""
        mock_client.get.return_value = make_envelope([])
        result = invoke([group, command])
        assert result.exit_code == 0
        assert mock_client.get.call_args[0][0] == url

    def test_mcp_tool_keeps_readable_module_name(self):
        names = _tool_names()
        assert "st_equipment_systems_equipment_types_list" in names
        assert not any(n.startswith("st_equipmentsystems_") for n in names)

    def test_fleet_pro_routes_to_fleetpro(self, invoke, mock_client):
        mock_client.get.return_value = [{"id": 1}]
        result = invoke(["fleet-pro", "vehicles-list"], json_output=True)
        assert result.exit_code == 0
        assert mock_client.get.call_args[0][:2] == ("fleetpro", "vehicles")

    def test_resource_version_is_sent(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([])
        invoke(["telecom", "calls-list"])
        assert mock_client.get.call_args[0][:2] == ("telecom", "calls")
        assert mock_client.get.call_args[1]["version"] == "v3"

    def test_nested_export_feed_gets_flat_name(self, invoke, mock_client):
        mock_client.get.return_value = {"data": [], "hasMore": False, "continueFrom": "t"}
        result = invoke(["crm", "export-customers-contacts"])
        assert result.exit_code == 0
        assert mock_client.get.call_args[0][:2] == ("crm", "export/customers/contacts")

    def test_nested_export_feed_tool_name(self):
        assert "st_payroll_export_jobs_splits" in _tool_names()


# ---------------------------------------------------------------------------
# Endpoint model + path filling
# ---------------------------------------------------------------------------


class TestEndpointModel:
    def test_path_params_in_order(self):
        ep = Endpoint("x", "GET", "contacts/{contactId}/contact-methods/{contactMethodId}")
        assert ep.path_params == ("contactId", "contactMethodId")

    def test_no_path_params(self):
        assert Endpoint("x", "GET", "technician-tracking").path_params == ()

    def test_fill_path(self):
        ep = Endpoint("x", "GET", "a/{one}/b/{two}")
        assert engine._fill_path(ep, {"one": 1, "two": "z"}) == "a/1/b/z"

    def test_fill_path_reports_every_missing_param(self):
        ep = Endpoint("x", "GET", "a/{one}/b/{two}")
        with pytest.raises(UsageError, match="one, two"):
            engine._fill_path(ep, {})

    def test_fill_path_rejects_empty_value(self):
        ep = Endpoint("x", "GET", "a/{one}")
        with pytest.raises(UsageError, match="one"):
            engine._fill_path(ep, {"one": ""})

    def test_fill_path_keeps_zero(self):
        """0 is a valid id and must not be treated as missing."""
        ep = Endpoint("x", "GET", "a/{one}")
        assert engine._fill_path(ep, {"one": 0}) == "a/0"


# ---------------------------------------------------------------------------
# Generated CLI commands for endpoints (through the real `st` app)
# ---------------------------------------------------------------------------


class TestEndpointCommands:
    def test_get_with_two_path_args(self, invoke, mock_client):
        mock_client.get.return_value = {"id": "m1", "type": "Phone"}
        result = invoke(["crm", "contacts-methods-get", "c-1", "m-1"], json_output=True)
        assert result.exit_code == 0
        mock_client.get.assert_called_once_with(
            "crm", "contacts/c-1/contact-methods/m-1", params=None, version="v2"
        )
        assert '"Phone"' in result.output

    def test_too_few_path_args_rejected(self, invoke, mock_client):
        result = invoke(["crm", "contacts-methods-get", "only-one"])
        assert result.exit_code != 0
        mock_client.get.assert_not_called()

    def test_too_many_path_args_rejected(self, invoke, mock_client):
        result = invoke(["dispatch", "skills-get", "a", "b"])
        assert result.exit_code != 0
        mock_client.get.assert_not_called()

    def test_body_endpoint_sends_json_and_query(self, invoke, mock_client):
        mock_client.patch.return_value = None
        result = invoke(
            ["crm", "contacts-update", "c-9", "--data", '{"name": "Pat"}', "--filter", "dry=true"]
        )
        assert result.exit_code == 0
        assert "contacts-update: done." in result.output
        mock_client.patch.assert_called_once_with(
            "crm", "contacts/c-9", json_body={"name": "Pat"}, params={"dry": True}, version="v2"
        )

    def test_body_endpoint_requires_data(self, invoke, mock_client):
        result = invoke(["crm", "contacts-update", "c-9"])
        assert result.exit_code != 0
        mock_client.patch.assert_not_called()

    def test_no_body_delete(self, invoke, mock_client):
        mock_client.delete.return_value = None
        result = invoke(["crm", "customers-note-delete", "5", "77"])
        assert result.exit_code == 0
        mock_client.delete.assert_called_once_with(
            "crm", "customers/5/notes/77", params=None, version="v2"
        )

    def test_endpoint_without_path_args(self, invoke, mock_client):
        mock_client.get.return_value = {"technicians": []}
        result = invoke(["dispatch", "technician-tracking"], json_output=True)
        assert result.exit_code == 0
        mock_client.get.assert_called_once_with(
            "dispatch", "technician-tracking", params=None, version="v2"
        )

    def test_paged_endpoint_single_page(self, invoke, mock_client):
        mock_client.get.return_value = make_envelope([{"id": 1, "name": "Note"}])
        result = invoke(["crm", "customers-notes-list", "5", "--page-size", "10"])
        assert result.exit_code == 0
        args, kwargs = mock_client.get.call_args
        assert args[:2] == ("crm", "customers/5/notes")
        assert kwargs["params"]["pageSize"] == 10
        assert kwargs["version"] == "v2"

    def test_paged_endpoint_all_pages(self, invoke, mock_client):
        mock_client.get.side_effect = [
            make_envelope([{"id": 1}], has_more=True),
            make_envelope([{"id": 2}], has_more=False),
        ]
        result = invoke(["crm", "customers-notes-list", "5", "--all"])
        assert result.exit_code == 0
        assert mock_client.get.call_count == 2

    def test_help_shows_path_args_only_when_needed(self, invoke):
        with_args = invoke(["crm", "contacts-methods-get", "--help"])
        assert "CONTACTID CONTACTMETHODID" in with_args.output
        no_args = invoke(["dispatch", "technician-tracking", "--help"])
        usage = next(line for line in no_args.output.splitlines() if "Usage:" in line)
        assert usage.strip().endswith("[OPTIONS]")

    def test_missing_path_args_is_a_usage_error(self, invoke, mock_client):
        result = invoke(["crm", "contacts-methods-get"])
        assert result.exit_code == 2
        mock_client.get.assert_not_called()

    def test_v3_endpoint(self, invoke, mock_client):
        mock_client.post.return_value = {"id": 3}
        invoke(["crm", "leads-create-v3", "--data", '{"summary": "x"}'])
        assert mock_client.post.call_args[0][:2] == ("crm", "leads")
        assert mock_client.post.call_args[1]["version"] == "v3"


# ---------------------------------------------------------------------------
# Generated MCP tools for endpoints
# ---------------------------------------------------------------------------


class TestEndpointTools:
    def test_paged_tool_fills_path(self, deps, mcp_ctx, mock_client):
        ep = Endpoint("notes", "GET", "customers/{id}/notes", paged=True)
        tool = engine._make_endpoint_tool("crm", ep, deps)
        mock_client.get.return_value = make_envelope([{"id": 1}])
        out = tool(mcp_ctx, path={"id": 5}, page=1)
        assert out["data"] == [{"id": 1}]
        assert mock_client.get.call_args[0][:2] == ("crm", "customers/5/notes")

    def test_paged_tool_respects_max_results(self, deps, mcp_ctx, mock_client):
        ep = Endpoint("notes", "GET", "customers/{id}/notes", paged=True)
        tool = engine._make_endpoint_tool("crm", ep, deps)
        mock_client.get.return_value = make_envelope([{"id": i} for i in range(5)], has_more=True)
        out = tool(mcp_ctx, path={"id": 5}, max_results=3)
        assert len(out["data"]) == 3
        assert out["truncated"] is True

    def test_body_tool(self, deps, mcp_ctx, mock_client):
        ep = Endpoint("upd", "PATCH", "contacts/{id}", body=True)
        tool = engine._make_endpoint_tool("crm", ep, deps)
        mock_client.patch.return_value = None
        assert tool(mcp_ctx, data={"a": 1}, path={"id": "g"}) == {"status": "ok"}
        mock_client.patch.assert_called_once_with(
            "crm", "contacts/g", json_body={"a": 1}, params=None, version="v2"
        )

    def test_body_tool_accepts_list_payload(self, deps, mcp_ctx, mock_client):
        ep = Endpoint("bulk", "POST", "items/bulk", body=True)
        tool = engine._make_endpoint_tool("x", ep, deps)
        mock_client.post.return_value = {"created": 2}
        tool(mcp_ctx, data=[{"a": 1}, {"a": 2}])
        assert mock_client.post.call_args[1]["json_body"] == [{"a": 1}, {"a": 2}]

    def test_missing_path_key_raises_before_calling_api(self, deps, mcp_ctx, mock_client):
        ep = Endpoint("get", "GET", "contacts/{contactId}/contact-methods/{contactMethodId}")
        tool = engine._make_endpoint_tool("crm", ep, deps)
        with pytest.raises(UsageError, match="contactMethodId"):
            tool(mcp_ctx, path={"contactId": "c"})
        mock_client.get.assert_not_called()

    def test_docstring_names_required_path_keys(self, deps):
        ep = Endpoint("get", "GET", "a/{one}/b/{two}", help="Thing")
        tool = engine._make_endpoint_tool("m", ep, deps)
        assert tool.__doc__ is not None
        assert "`one`, `two`" in tool.__doc__

    def test_registered_tools_tagged_by_verb(self):
        tools = _tool_names()
        assert "read" in tools["st_crm_contacts_methods_get"].tags  # type: ignore[attr-defined]
        assert "write" in tools["st_crm_contacts_methods_delete"].tags  # type: ignore[attr-defined]

    def test_usage_error_surfaces_as_tool_error(self):
        import st_cli.mcp_server as server

        async def call() -> None:
            await server.mcp.call_tool("st_crm_contacts_methods_get", {"path": {}})

        with pytest.raises(ToolError, match="contactId"):
            asyncio.run(call())

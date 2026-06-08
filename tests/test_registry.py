"""Integrity of the registry + the full generated CLI/MCP surface.

These guard the invariants the engine relies on (unique names, valid ops/verbs)
and lock in the two routing-bug fixes (estimates -> salestech, job types -> jpm).
"""

from __future__ import annotations

import asyncio

import typer

from st_cli.registry import all_modules

_VALID_OPS = set("LRCUDP")
_VALID_VERBS = {"POST", "PATCH", "PUT", "DELETE"}


def _resolved_command_names(app: typer.Typer) -> list[str]:
    """Resolve every command name a Typer group will expose (pre-dedup)."""
    names = []
    for ci in app.registered_commands:
        if ci.name:
            names.append(ci.name)
        else:
            names.append(ci.callback.__name__.replace("_", "-"))
    return names


class TestRegistryIntegrity:
    def test_module_names_unique(self):
        names = [m.name for m in all_modules()]
        assert len(names) == len(set(names))

    def test_resource_slugs_unique_within_module(self):
        for module in all_modules():
            slugs = [r.slug for r in module.resources]
            assert len(slugs) == len(set(slugs)), f"dup slug in {module.name}"

    def test_ops_are_valid(self):
        for module in all_modules():
            for resource in module.resources:
                assert set(resource.ops) <= _VALID_OPS, f"{module.name}.{resource.slug}"

    def test_action_verbs_valid(self):
        for module in all_modules():
            for resource in module.resources:
                for action in resource.actions:
                    assert action.verb in _VALID_VERBS

    def test_date_keys_are_pairs(self):
        for module in all_modules():
            for resource in module.resources:
                assert len(resource.date_keys) == 2

    def test_covers_all_24_modules(self):
        # 7 hand-written groups (one extension each except reporting) + 17 new
        api_modules = {m.name for m in all_modules()} | {"reporting"}
        assert len(api_modules) == 24


class TestNoCommandCollisions:
    """Generated commands must not shadow hand-written ones in shared groups."""

    def test_cli_group_command_names_unique(self):
        from st_cli.main import app

        for group in app.registered_groups:
            sub = group.typer_instance
            names = _resolved_command_names(sub)
            dupes = {n for n in names if names.count(n) > 1}
            assert not dupes, f"duplicate commands in '{group.name}': {dupes}"

    def test_mcp_tool_names_unique(self):
        import st_cli.mcp_server as server

        tools = asyncio.run(server.mcp.list_tools())
        names = [t.name for t in tools]
        assert len(names) == len(set(names))
        # sizable surface: hand-written + generated
        assert len(names) > 300


class TestRoutingBugFixes:
    def test_job_types_live_under_jpm(self, invoke, mock_client):
        from tests.conftest import make_envelope

        mock_client.get.return_value = make_envelope([{"id": 1, "name": "AC Repair"}])
        result = invoke(["jobs", "job-types-list"])
        assert result.exit_code == 0
        assert "AC Repair" in result.output
        assert mock_client.get.call_args[0][:2] == ("jpm", "job-types")

    def test_settings_no_longer_has_job_types(self):
        from st_cli.commands import settings

        names = _resolved_command_names(settings.app)
        assert "job-types-list" not in names

    def test_estimates_live_under_salestech(self, invoke, mock_client):
        from tests.conftest import make_envelope

        mock_client.get.return_value = make_envelope([{"id": 1, "status": "Open"}])
        result = invoke(["salestech", "estimates-list"])
        assert result.exit_code == 0
        # CLI group is "salestech", but the URL prefix is /sales/v2/ (real ST path)
        assert mock_client.get.call_args[0][:2] == ("sales", "estimates")

    def test_accounting_no_longer_has_estimates(self):
        from st_cli.commands import accounting

        names = _resolved_command_names(accounting.app)
        assert "estimates-list" not in names
        assert "estimates-get" not in names

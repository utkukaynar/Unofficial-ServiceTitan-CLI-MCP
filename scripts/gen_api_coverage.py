#!/usr/bin/env python
"""Regenerate docs/api-coverage.md from the live command tree.

Run: ``uv run python scripts/gen_api_coverage.py``

The coverage page is derived from the actual wired ``st`` app and ``st-mcp``
tool list, so it can never drift from the code. Re-run after adding resources
to ``src/st_cli/registry.py`` or new hand-written commands.
"""

from __future__ import annotations

import asyncio
import pathlib

import typer

from st_cli.main import app
from st_cli.registry import all_modules

HANDWRITTEN = {"crm", "jobs", "dispatch", "accounting", "memberships", "reporting", "settings"}
DOCS = pathlib.Path(__file__).resolve().parent.parent / "docs" / "api-coverage.md"


def main() -> None:
    click_app = typer.main.get_command(app)
    groups = {
        name: sorted(getattr(group, "commands", {}).keys())
        for name, group in click_app.commands.items()
    }
    cli_help = {name: (group.help or "").strip() for name, group in click_app.commands.items()}
    reg_help = {m.cli_group: m.help for m in all_modules()}

    import st_cli.mcp_server as server

    tool_count = len(asyncio.run(server.mcp.list_tools()))
    cmd_count = sum(len(v) for v in groups.values())

    lines: list[str] = []
    w = lines.append
    w("# API coverage")
    w("")
    w("> **Auto-generated reference.** Regenerate with the snippet at the bottom of this page.")
    w("")
    w(
        f"`st` / `st-mcp` cover **all 24 ServiceTitan API v2 modules** — "
        f"**{cmd_count} CLI commands** and **{tool_count} MCP tools** total."
    )
    w("")
    w(
        "Each CLI group below maps to one ServiceTitan module. The MCP tool for any command is "
        "`st_{module}_{resource}_{action}` (job types live under `jpm`, estimates under "
        "`salestech`). Run `st <group> --help` or `st <group> <command> --help` for options."
    )
    w("")
    w(
        "Legend: most commands follow the generated archetypes — `…-list`, `…-get`, `…-create`, "
        "`…-update`, `…-delete`, domain actions, and `export-<feed>` change-feeds. See "
        "[CLI reference](cli-reference.md) for shared options and "
        "[Architecture](architecture.md) for how they're generated."
    )
    w("")

    order = ["crm", "jobs", "dispatch", "accounting", "memberships", "reporting", "settings"]
    order += [g for g in groups if g not in order]

    for group_name in order:
        cmds = groups[group_name]
        badge = "hand-tuned + generated" if group_name in HANDWRITTEN else "generated"
        help_text = reg_help.get(group_name) or cli_help.get(group_name) or ""
        w(f"## `{group_name}`")
        w("")
        prefix = f"*{help_text}* — " if help_text else ""
        w(f"{prefix}_{badge}_  ·  {len(cmds)} commands")
        w("")
        w("```text")
        for cmd in cmds:
            w(f"st {group_name} {cmd}")
        w("```")
        w("")

    w("---")
    w("")
    w("## Regenerating this page")
    w("")
    w("This page is derived from the live command tree so it can't drift from the code:")
    w("")
    w("```bash")
    w("uv run python scripts/gen_api_coverage.py")
    w("```")
    w("")
    w(
        "← [Back to docs index](README.md) · [CLI reference](cli-reference.md) · "
        "[MCP server](mcp-server.md)"
    )
    w("")

    DOCS.write_text("\n".join(lines))
    print(f"wrote {DOCS.relative_to(DOCS.parents[1])}: {cmd_count} commands, {tool_count} tools")


if __name__ == "__main__":
    main()

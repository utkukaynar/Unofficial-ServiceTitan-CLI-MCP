"""Docs must only mention commands and tools that exist.

The docs drifted once already (``bookings-create``, ``purchase-orders-approve``,
``st jpm …`` — none of which worked), so every ``st <group> <command>`` and
``st_…`` tool name in README.md and docs/*.md is checked against the live CLI
and MCP server. ``docs/api-coverage.md`` is generated from them and skipped.
"""

from __future__ import annotations

import asyncio
import re
from functools import cache
from pathlib import Path

import pytest
import typer

ROOT = Path(__file__).resolve().parent.parent
DOC_FILES = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
DOC_FILES = [f for f in DOC_FILES if f.name != "api-coverage.md"]

# Names the docs cite on purpose as what a tool is *not* called.
COUNTER_EXAMPLES = {"st_memberships_memberships_update"}

_CLI_REF = re.compile(r"(?<![\w-])st (?:--json )?([a-z][a-z-]*) ([a-z][a-z0-9-]*)")
_TOOL_REF = re.compile(r"\bst_[a-z0-9_]+\b")


@cache
def cli_commands() -> dict[str, frozenset[str]]:
    from st_cli.main import app

    root = typer.main.get_command(app)
    return {
        name: frozenset(getattr(group, "commands", {}).keys())
        for name, group in root.commands.items()  # type: ignore[attr-defined]
    }


@cache
def mcp_tools() -> frozenset[str]:
    import st_cli.mcp_server as server

    return frozenset(t.name for t in asyncio.run(server.mcp.list_tools()))


@pytest.mark.parametrize("doc", DOC_FILES, ids=lambda p: p.name)
def test_cli_commands_in_docs_exist(doc: Path):
    groups = cli_commands()
    bad = []
    for lineno, line in enumerate(doc.read_text().splitlines(), 1):
        for group, command in _CLI_REF.findall(line):
            if group not in groups:
                bad.append(f"{doc.name}:{lineno}: unknown group `st {group}`")
            elif command not in groups[group]:
                bad.append(f"{doc.name}:{lineno}: unknown command `st {group} {command}`")
    assert not bad, "\n".join(bad)


@pytest.mark.parametrize("doc", DOC_FILES, ids=lambda p: p.name)
def test_mcp_tools_in_docs_exist(doc: Path):
    tools = mcp_tools()
    bad = [
        f"{doc.name}:{lineno}: unknown tool `{name}`"
        for lineno, line in enumerate(doc.read_text().splitlines(), 1)
        for name in _TOOL_REF.findall(line)
        # `st_crm_*`-style globs end in "_"; st_cli is the package
        if not name.endswith("_")
        and not name.startswith("st_cli")
        and name not in tools
        and name not in COUNTER_EXAMPLES
    ]
    assert not bad, "\n".join(bad)

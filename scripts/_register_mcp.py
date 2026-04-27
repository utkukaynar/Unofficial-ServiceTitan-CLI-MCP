"""Idempotently register an MCP server entry in a Claude Code / Desktop config.

Usage:
    python _register_mcp.py <config-path> <server-name> <command> [arg ...]

If the config file doesn't exist it's created (parent dirs included). If it
exists, ``mcpServers.<server-name>`` is added or replaced; everything else in
the file is preserved.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 4:
        print(
            "Usage: _register_mcp.py <config-path> <server-name> <command> [arg ...]",
            file=sys.stderr,
        )
        return 2

    config_path = Path(sys.argv[1]).expanduser()
    server_name = sys.argv[2]
    command = sys.argv[3]
    extra_args = sys.argv[4:]

    if config_path.exists():
        try:
            config = json.loads(config_path.read_text() or "{}")
        except json.JSONDecodeError as exc:
            print(
                f"error: existing config at {config_path} is not valid JSON: {exc}",
                file=sys.stderr,
            )
            return 1
    else:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config = {}

    if not isinstance(config, dict):
        print(f"error: config at {config_path} is not a JSON object", file=sys.stderr)
        return 1

    servers = config.setdefault("mcpServers", {})
    if not isinstance(servers, dict):
        print(f"error: 'mcpServers' in {config_path} is not an object", file=sys.stderr)
        return 1

    entry: dict[str, object] = {"command": command}
    if extra_args:
        entry["args"] = extra_args
    servers[server_name] = entry

    config_path.write_text(json.dumps(config, indent=2) + "\n")
    print(f"  registered '{server_name}' in {config_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

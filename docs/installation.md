# Installation

Requires **Python 3.11+**.

## One-shot installer (recommended)

The installer picks the best available isolated installer (`uv tool` → `pipx` →
`pip --user`), puts `st` and `st-mcp` on PATH, and registers `st-mcp` with Claude
Code and/or Claude Desktop.

### macOS / Linux

```bash
git clone https://github.com/utkukaynar/Unofficial-ServiceTitan-CLI-MCP.git
cd Unofficial_ST_CLI
./scripts/install.sh                # interactive
# or non-interactive:
./scripts/install.sh --code         # register with Claude Code only
./scripts/install.sh --desktop      # register with Claude Desktop only
./scripts/install.sh --both         # both
./scripts/install.sh --skip         # install only, don't touch any config
```

### Windows (PowerShell)

```powershell
git clone https://github.com/utkukaynar/Unofficial-ServiceTitan-CLI-MCP.git
Set-Location Unofficial_ST_CLI
.\scripts\install.ps1                       # interactive
# or non-interactive:
.\scripts\install.ps1 -Target Code
.\scripts\install.ps1 -Target Desktop
.\scripts\install.ps1 -Target Both
.\scripts\install.ps1 -Target Skip
```

The MCP registration is idempotent — re-running the installer just refreshes the
`command` path. Other servers in your config are preserved.

## Manual install

```bash
# Editable install with dev dependencies (uv)
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"

# Verify
st --help
st-mcp --help
```

Then add `st-mcp` to your MCP client manually — see
[MCP server → Hooking it up](mcp-server.md#hooking-it-up-to-claude-code).

## Next steps

- [Configure](configuration.md) your credentials in a `.env` file.
- Run your [first commands](usage.md#quick-start).

---

← [Docs index](README.md) · [Configuration →](configuration.md)

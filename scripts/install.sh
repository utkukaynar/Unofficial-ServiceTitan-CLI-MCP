#!/usr/bin/env bash
# Install st-cli + st-mcp on macOS/Linux and (optionally) register the MCP
# server with Claude Code and/or Claude Desktop.
#
# Usage:
#   ./scripts/install.sh                # interactive
#   ./scripts/install.sh --code         # register with Claude Code
#   ./scripts/install.sh --desktop      # register with Claude Desktop
#   ./scripts/install.sh --both         # register with both
#   ./scripts/install.sh --skip         # install only, no MCP registration
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

mode="${1:-interactive}"

# --- 1. Python check ---------------------------------------------------------
if ! command -v python3 >/dev/null 2>&1; then
  echo "error: python3 not found. Install Python 3.11+ first." >&2
  exit 1
fi

py_version="$(python3 -c 'import sys; print("{}.{}".format(*sys.version_info[:2]))')"
if [[ "$(python3 -c 'import sys; print(sys.version_info >= (3, 11))')" != "True" ]]; then
  echo "error: Python 3.11+ required (found $py_version)." >&2
  exit 1
fi
echo "✓ Python $py_version"

# --- 2. Install --------------------------------------------------------------
# Prefer isolated tool installs (uv tool / pipx) so st-mcp lands on PATH for
# any GUI client. Fall back to a user-site pip install.
if command -v uv >/dev/null 2>&1; then
  echo "→ Installing with uv..."
  uv tool install --reinstall --editable "$REPO_ROOT"
  installer="uv"
elif command -v pipx >/dev/null 2>&1; then
  echo "→ Installing with pipx..."
  pipx install --force --editable "$REPO_ROOT"
  installer="pipx"
else
  echo "→ Installing with pip --user (consider 'brew install uv' or 'pipx' for isolation)..."
  if ! python3 -m pip install --user -e "$REPO_ROOT" 2>/dev/null; then
    python3 -m pip install --user --break-system-packages -e "$REPO_ROOT"
  fi
  installer="pip"
fi

# --- 3. Locate st-mcp on PATH -----------------------------------------------
hash -r 2>/dev/null || true
if ! command -v st-mcp >/dev/null 2>&1; then
  echo "warning: st-mcp not on PATH after install (installer: $installer)."
  case "$installer" in
    uv)   echo "  Try: export PATH=\"\$HOME/.local/bin:\$PATH\"" ;;
    pipx) echo "  Try: pipx ensurepath, then restart your shell." ;;
    pip)  echo "  Add Python's user-bin dir to PATH (python3 -m site --user-base)/bin." ;;
  esac
  st_mcp_path="st-mcp"
else
  st_mcp_path="$(command -v st-mcp)"
  echo "✓ st-mcp at $st_mcp_path"
fi

# --- 4. Register with MCP clients -------------------------------------------
register() {
  python3 "$REPO_ROOT/scripts/_register_mcp.py" "$1" servicetitan "$st_mcp_path"
}

claude_code_cfg="$HOME/.claude/settings.json"
case "$(uname -s)" in
  Darwin) claude_desktop_cfg="$HOME/Library/Application Support/Claude/claude_desktop_config.json" ;;
  *)      claude_desktop_cfg="$HOME/.config/Claude/claude_desktop_config.json" ;;
esac

case "$mode" in
  --code)    register "$claude_code_cfg" ;;
  --desktop) register "$claude_desktop_cfg" ;;
  --both)    register "$claude_code_cfg"; register "$claude_desktop_cfg" ;;
  --skip)    echo "→ Skipping MCP registration." ;;
  interactive)
    echo
    echo "Where would you like to register st-mcp?"
    echo "  1) Claude Code      ($claude_code_cfg)"
    echo "  2) Claude Desktop   ($claude_desktop_cfg)"
    echo "  3) Both"
    echo "  4) Skip"
    read -rp "Choice [1-4]: " choice
    case "$choice" in
      1) register "$claude_code_cfg" ;;
      2) register "$claude_desktop_cfg" ;;
      3) register "$claude_code_cfg"; register "$claude_desktop_cfg" ;;
      4) echo "→ Skipping MCP registration." ;;
      *) echo "error: invalid choice." >&2; exit 1 ;;
    esac
    ;;
  *)
    echo "error: unknown flag '$mode'. Use --code, --desktop, --both, --skip, or no flag." >&2
    exit 1
    ;;
esac

# --- 5. .env reminder --------------------------------------------------------
if [[ ! -f "$REPO_ROOT/.env" ]]; then
  echo
  echo "→ No .env file found at $REPO_ROOT/.env."
  echo "  Create one with: ST_CLIENT_ID, ST_CLIENT_SECRET, ST_APP_KEY, ST_TENANT_ID, ST_ENVIRONMENT."
  echo "  See README.md → Configure."
fi

echo
echo "✓ Done. Restart your MCP client to pick up the new server."

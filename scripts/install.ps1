<#
.SYNOPSIS
    Install st-cli + st-mcp on Windows and (optionally) register the MCP server
    with Claude Code and/or Claude Desktop.

.EXAMPLE
    PS> .\scripts\install.ps1
    PS> .\scripts\install.ps1 -Target Code
    PS> .\scripts\install.ps1 -Target Desktop
    PS> .\scripts\install.ps1 -Target Both
    PS> .\scripts\install.ps1 -Target Skip
#>

[CmdletBinding()]
param(
    [ValidateSet("Interactive", "Code", "Desktop", "Both", "Skip")]
    [string]$Target = "Interactive"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path "$PSScriptRoot\..").Path
Set-Location $RepoRoot

# --- 1. Python check ---------------------------------------------------------
$pythonCmd = $null
foreach ($candidate in @("python", "python3", "py")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        $pythonCmd = $candidate
        break
    }
}
if (-not $pythonCmd) {
    Write-Error "Python 3.11+ not found. Install from python.org first."
    exit 1
}

$pyVersion = & $pythonCmd -c "import sys; print('{}.{}'.format(*sys.version_info[:2]))"
$pyOk      = & $pythonCmd -c "import sys; print(sys.version_info >= (3, 11))"
if ($pyOk.Trim() -ne "True") {
    Write-Error "Python 3.11+ required (found $pyVersion)."
    exit 1
}
Write-Host "✓ Python $pyVersion"

# --- 2. Install --------------------------------------------------------------
$installer = $null
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "→ Installing with uv..."
    uv tool install --reinstall --editable $RepoRoot
    $installer = "uv"
}
elseif (Get-Command pipx -ErrorAction SilentlyContinue) {
    Write-Host "→ Installing with pipx..."
    pipx install --force --editable $RepoRoot
    $installer = "pipx"
}
else {
    Write-Host "→ Installing with pip --user (consider 'pipx' or 'uv' for isolation)..."
    & $pythonCmd -m pip install --user -e $RepoRoot
    $installer = "pip"
}

# --- 3. Locate st-mcp --------------------------------------------------------
$stMcp = Get-Command st-mcp -ErrorAction SilentlyContinue
if (-not $stMcp) {
    Write-Warning "st-mcp not on PATH after install (installer: $installer)."
    switch ($installer) {
        "uv"   { Write-Host '  Try: $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"' }
        "pipx" { Write-Host '  Try: pipx ensurepath, then restart your shell.' }
        "pip"  { Write-Host '  Add Python''s Scripts dir to PATH (python -m site --user-base)\Scripts.' }
    }
    $stMcpPath = "st-mcp"
} else {
    $stMcpPath = $stMcp.Source
    Write-Host "✓ st-mcp at $stMcpPath"
}

# --- 4. Register with MCP clients -------------------------------------------
$claudeCodeCfg    = Join-Path $env:USERPROFILE ".claude\settings.json"
$claudeDesktopCfg = Join-Path $env:APPDATA "Claude\claude_desktop_config.json"

function Register-Mcp([string]$ConfigPath) {
    & $pythonCmd "$RepoRoot\scripts\_register_mcp.py" $ConfigPath "servicetitan" $stMcpPath
}

$choice = $null
switch ($Target) {
    "Code"    { Register-Mcp $claudeCodeCfg }
    "Desktop" { Register-Mcp $claudeDesktopCfg }
    "Both"    { Register-Mcp $claudeCodeCfg; Register-Mcp $claudeDesktopCfg }
    "Skip"    { Write-Host "→ Skipping MCP registration." }
    "Interactive" {
        Write-Host ""
        Write-Host "Where would you like to register st-mcp?"
        Write-Host "  1) Claude Code      ($claudeCodeCfg)"
        Write-Host "  2) Claude Desktop   ($claudeDesktopCfg)"
        Write-Host "  3) Both"
        Write-Host "  4) Skip"
        $choice = Read-Host "Choice [1-4]"
        switch ($choice) {
            "1" { Register-Mcp $claudeCodeCfg }
            "2" { Register-Mcp $claudeDesktopCfg }
            "3" { Register-Mcp $claudeCodeCfg; Register-Mcp $claudeDesktopCfg }
            "4" { Write-Host "→ Skipping MCP registration." }
            default { Write-Error "Invalid choice."; exit 1 }
        }
    }
}

# --- 5. .env reminder --------------------------------------------------------
$envFile = Join-Path $RepoRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Host ""
    Write-Host "→ No .env file found at $envFile."
    Write-Host "  Create one with: ST_CLIENT_ID, ST_CLIENT_SECRET, ST_APP_KEY, ST_TENANT_ID, ST_ENVIRONMENT."
    Write-Host "  See README.md → Configure."
}

Write-Host ""
Write-Host "✓ Done. Restart your MCP client to pick up the new server."

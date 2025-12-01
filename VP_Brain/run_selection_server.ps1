# Runs the VisionPilot selection server with correct import path
# Usage: Right-click > Run with PowerShell (or execute from PowerShell)

Param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$NoReload
)

# Move to script directory
Push-Location $PSScriptRoot

# Activate venv if present
$venvActivate = Join-Path $PSScriptRoot "venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    . $venvActivate
}

# Ensure Python can import the package from project root
$env:PYTHONPATH = $PSScriptRoot

# Build uvicorn args
$reloadArg = $null
if (-not $NoReload.IsPresent) { $reloadArg = "--reload" }

uvicorn "vp_brain.mcp.selection_server:app" --host $Host --port $Port $reloadArg

Pop-Location

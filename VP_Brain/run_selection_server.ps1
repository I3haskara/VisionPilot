# Runs the VisionPilot selection server with correct import path
# Usage: Right-click > Run with PowerShell (or execute from PowerShell)

Param(
    [string]$ListenHost = "127.0.0.1",
    [int]$ListenPort = 8000,
    [switch]$NoReload
)

# Move to script directory
Push-Location $PSScriptRoot

# Activate venv if present
$venvActivateLocal = Join-Path $PSScriptRoot "venv\Scripts\Activate.ps1"
if (Test-Path $venvActivateLocal) {
    . $venvActivateLocal
} else {
    $venvActivateParent = Join-Path (Join-Path $PSScriptRoot "..") "venv\Scripts\Activate.ps1"
    if (Test-Path $venvActivateParent) {
        . $venvActivateParent
    }
}

# Ensure Python can import the package from project root
$env:PYTHONPATH = $PSScriptRoot

# Load environment variables from .env if present
$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith('#')) { return }
        $parts = $line -split '=', 2
        if ($parts.Count -eq 2) {
            $key = $parts[0].Trim()
            $val = $parts[1].Trim()
            # Remove inline comments after value
            $val = ($val -split '\s+#', 2)[0].Trim()
            [System.Environment]::SetEnvironmentVariable($key, $val, [System.EnvironmentVariableTarget]::Process)
        }
    }
}

# Build uvicorn args
$reloadArg = $null
if (-not $NoReload.IsPresent) { $reloadArg = "--reload" }

# Resolve python executable (prefer active venv)
$pythonExe = $null
if ($env:VIRTUAL_ENV) {
    $pythonExe = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
}
if (-not $pythonExe -or -not (Test-Path $pythonExe)) {
    $pythonExe = Join-Path (Join-Path $PSScriptRoot "..") "venv\Scripts\python.exe"
}

& $pythonExe -m uvicorn "vp_brain.mcp.selection_server:app" --app-dir $PSScriptRoot --host $ListenHost --port $ListenPort $reloadArg

Pop-Location

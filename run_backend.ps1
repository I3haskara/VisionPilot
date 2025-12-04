# run_backend.ps1  — local VisionPilot backend

Push-Location "I:\VisionPilot"

# Activate venv
& "I:\VisionPilot\venv\Scripts\Activate.ps1"

# Set module path
$env:PYTHONPATH = "I:\VisionPilot\VP_Brain"

# Kill any old python using the port (optional but practical)
try {
    $pids = (netstat -ano | findstr :8010 | ForEach-Object { ($_ -split '\s+')[-1] }) | Select-Object -Unique
    foreach ($pid in $pids) {
        if ($pid -match '^\d+$') { taskkill /PID $pid /F | Out-Null }
    }
} catch { }

# Start server on fixed port
python -m uvicorn vp_brain.mcp.selection_server:app --host 127.0.0.1 --port 8010 --reload

Pop-Location
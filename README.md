# VisionPilot

## Overview

VisionPilot brings together a Python “brain” (VP_Brain) and a Unity client (VP_Unity) to power interactive, voice/vision-driven AR experiences. This repository contains both parts and supporting scripts.

Repo layout:
- `VP_Brain/` — Python services, including the Selection FastAPI server and MCP utilities
- `VP_Unity/` — Unity project (optional, not needed to run the selection server)

## VP_Brain: Selection Server

The Selection Server is a small FastAPI app that stores the latest user “selection” and exposes two endpoints:
- `GET /health` → `{ "status": "ok" }`
- `GET /selection` → returns current selection JSON
- `POST /selection` → updates the selection

### Quick Start (Windows PowerShell)

Minimal dependencies (FastAPI + Uvicorn + Requests for testing):

```powershell
cd I:\VisionPilot\VP_Brain
python -m pip install --upgrade pip
python -m pip install fastapi uvicorn requests
$env:PYTHONPATH = "."
python -m uvicorn vp_brain.mcp.selection_server:app --reload
```

Alternatively, run the module directly (uses an internal __main__ runner):

```powershell
cd I:\VisionPilot\VP_Brain
$env:PYTHONPATH = "."
python -m vp_brain.mcp.selection_server
```

Helper script (auto-sets `PYTHONPATH`, uses Uvicorn):

```powershell
cd I:\VisionPilot\VP_Brain
./run_selection_server.ps1
```

Note: The old root `selection_server.py` is deprecated. Use the package path `vp_brain.mcp.selection_server`.

### Test It

Health check:

```powershell
python -c "import requests; print(requests.get('http://127.0.0.1:8000/health').json())"
```

Post a selection (example with segment metadata):

```powershell
python -c "import requests; url='http://127.0.0.1:8000/selection'; r=requests.post(url, json={'x':0.5,'y':0.5,'source':'xr','segment_id':'page_1'}); print(r.json())"
```

Get the latest selection:

```powershell
python -c "import requests; print(requests.get('http://127.0.0.1:8000/selection').json())"
```

### Endpoint Contract

Request body for `POST /selection`:

```json
{
	"x": 0.0,   // 0.0–1.0
	"y": 0.0,   // 0.0–1.0
	"source": "demo|xr|...",  
	"segment_id": "cover|page_1|page_2|page_3|chapter_2|..."
}
```

Response (both GET and POST):

```json
{
	"x": 0.5,
	"y": 0.5,
	"source": "xr",
	"segment_id": "page_1",
	"ts": "2025-12-01T11:22:33.782953"
}
```

## VP_Unity

Open the Unity project in `VP_Unity/` with a matching Unity version (see `ProjectSettings/ProjectVersion.txt`). This is optional for running the Python Selection Server.

## Notes
- Windows PowerShell is the primary shell assumed in examples.
- If you need to expose the server to other devices, start Uvicorn with `--host 0.0.0.0`.

## Contributing
PRs welcome. Please follow existing code style and keep changes minimal and focused.

## License
TBD
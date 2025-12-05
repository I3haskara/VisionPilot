# Porting Guide (New Device Setup)

This guide shows how to clone, set up, and run VisionPilot on a fresh machine. It focuses on the Python Selection Server in `VP_Brain` and includes optional notes for the Unity/MCP websocket helpers.

## Requirements

- Python 3.10 or newer (3.10.x recommended)
- Git
- A shell:
  - Windows: Windows PowerShell 5.1 (used in examples)
  - macOS/Linux: Bash or zsh
- Optional: VS Code for editing/debugging
- Network ports:
  - `8000` (Selection Server HTTP)
  - `8080`/`8090` (optional MCP websocket tools to Unity)

## Clone the repository

```powershell
git clone https://github.com/I3haskara/VisionPilot.git
cd VisionPilot
```

## Create a virtual environment and install deps

Windows PowerShell:

```powershell
python -m venv venv
./venv/Scripts/Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r VP_Brain/requirements.txt
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r VP_Brain/requirements.txt
```

## Run the Selection Server

The server lives at `vp_brain.mcp.selection_server:app`.

Option A — Uvicorn (recommended during development):

- Windows PowerShell

```powershell
cd VP_Brain
$env:PYTHONPATH = "."
python -m uvicorn vp_brain.mcp.selection_server:app --host 127.0.0.1 --port 8000 --reload
```

- macOS/Linux

```bash
cd VP_Brain
export PYTHONPATH=.
python -m uvicorn vp_brain.mcp.selection_server:app --host 127.0.0.1 --port 8000 --reload
```

Option B — Module runner (uses uvicorn internally):

```powershell
cd VP_Brain
python -m vp_brain.mcp.selection_server
```

Option C — Helper script (Windows PowerShell):

- `run_backend.ps1` (recommended): kills any process on `8010`, activates `venv`, sets `PYTHONPATH`, and runs uvicorn on `127.0.0.1:8010`.

```powershell
cd VP_Brain
../run_backend.ps1
```

- Legacy: `run_selection_server.ps1` if present.

Notes:
- If you need to reach the server from other devices on your LAN, use `--host 0.0.0.0` and allow the port through your firewall.
- If you see import errors, ensure your CWD is `VP_Brain` or that `PYTHONPATH` includes the `VP_Brain` directory.

## Verify the API

Health check:

```powershell
python -c "import requests; print(requests.get('http://127.0.0.1:8010/health').json())"
```

Post a selection:

```powershell
python -c "import requests; url='http://127.0.0.1:8010/selection'; r=requests.post(url, json={'x':0.5,'y':0.5,'source':'demo','segment_id':'page_1'}); print(r.json())"
```

Read the latest selection:

```powershell
python -c "import requests; print(requests.get('http://127.0.0.1:8010/selection').json())"
```

## Optional: MCP websocket utilities

The MCP helper scripts under `VP_Brain/vp_brain/mcp/` use websockets to talk to Unity (typical URLs: `ws://localhost:8090`):

- Quick example (Python REPL):

```python
import asyncio
from vp_brain.mcp.send_selection import send_selection

asyncio.run(send_selection(0.5, 0.3))
```

Ensure Unity is listening on the matching websocket port and accepts the message schema you expect.

## Troubleshooting

- ModuleNotFoundError (vp_brain/mcp):
  - Run commands from the `VP_Brain` directory, or set `PYTHONPATH` to `.` (Windows: `$env:PYTHONPATH = "."`; macOS/Linux: `export PYTHONPATH=.`).
- Port conflicts:
  - Default dev port is `8010`. If `8010` is in use, pick another (e.g., `8020`) or stop the conflicting service. `run_backend.ps1` auto-clears `8010`.
- Uvicorn not found:
  - `pip install uvicorn` (or re-run `pip install -r VP_Brain/requirements.txt`).
- PowerShell script blocked:
  - You may need to adjust execution policy (e.g., `Set-ExecutionPolicy -Scope Process RemoteSigned`) or run the script in a signed/allowed context.
- Firewall/AV blocks:
  - Allow Python and the chosen port (e.g., 8000) through your firewall.

## Dependency management

- App dependencies are listed in `VP_Brain/requirements.txt`:

```
fastapi
uvicorn
pydantic
requests
websockets
```

- To lock exact versions for reproducibility (optional):

```powershell
pip freeze > VP_Brain/requirements.lock.txt
```

## Git hygiene and large files

- Do not commit local virtual environments; `.gitignore` excludes `venv/` already.
- If you need to track large assets (models/media), use Git LFS and add only the required paths.

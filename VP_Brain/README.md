## Quick Start

```bash
cd I:\VisionPilot\VP_Brain
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Run Selection Server

Recommended (auto-reload):

```powershell
cd I:\VisionPilot\VP_Brain
venv\Scripts\activate
$env:PYTHONPATH = "."
uvicorn vp_brain.mcp.selection_server:app --reload
```

Or run the module directly:

```powershell
cd I:\VisionPilot\VP_Brain
venv\Scripts\activate
python -m vp_brain.mcp.selection_server
```

Windows helper script:

```powershell
cd I:\VisionPilot\VP_Brain
./run_selection_server.ps1
```

Note: The old root `selection_server.py` is deprecated. Use the package path `vp_brain.mcp.selection_server`.

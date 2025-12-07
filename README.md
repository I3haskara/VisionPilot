# VisionPilot

## Overview

VisionPilot brings together a Python “brain” (VP_Brain) and a Unity client (VP_Unity) to power interactive, voice/vision-driven AR experiences. This repository contains both parts and supporting scripts.

Repo layout:
- `VP_Brain/` — Python services, including the Selection FastAPI server and MCP utilities
- `VP_Unity/` — Unity project (optional, not needed to run the selection server)

For first-time setup on a new machine, see `PORTING.md`.

## VP_Brain: Selection Server

The Selection Server is a small FastAPI app that stores the latest user “selection” and includes voice features (STT via OpenAI Whisper; TTS via ElevenLabs). It exposes endpoints:
- `GET /health` → `{ "status": "ok" }`
- `GET /selection` → returns current selection JSON
- `POST /selection` → updates the selection
- `POST /voice/command` → Mic upload (WAV/MP3) → Whisper STT → Chat → JSON reply
- `POST /tts` → ElevenLabs TTS, returns public URL to generated MP3
- `GET /tts/test` → Quick ElevenLabs voice test using env-configured voice ID

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

### Environment Setup (keep secrets local)

Create `VP_Brain/.env` with your keys. Do not commit this file.

```env
# OpenAI (STT Whisper + Chat)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
# Optional if your billing is under an org
OPENAI_ORG_ID=org_xxxxxxxxxxxxxxxx

# ElevenLabs (TTS)
ELEVENLABS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
ELEVENLABS_VOICE_ID=flHkNRp1BlvT73UL6gyz

# Public base URL for serving static TTS files
PUBLIC_BASE_URL=http://127.0.0.1:8000
```

To start from the repo root:

```powershell
F:\SenseAIProject\VisionPilot\venv\Scripts\Activate.ps1
$env:PYTHONPATH = "F:\SenseAIProject\VisionPilot\VP_Brain"
uvicorn vp_brain.mcp.selection_server:app --host 127.0.0.1 --port 8000 --reload
```

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

TTS quick test (PowerShell):

```powershell
$body = @{ text = "Hello from VisionPilot"; buddy_id = "test_buddy" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/tts" -ContentType "application/json" -Body $body
```

Mic command test (multipart upload):

```powershell
Invoke-RestMethod -Method Post `
	-Uri "http://127.0.0.1:8000/voice/command" `
	-ContentType "multipart/form-data" `
	-Form @{ audio = Get-Item "F:\SenseAIProject\VisionPilot\VP_Brain\debug_audio\sample.wav" }
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
- Keep secrets out of git. `.env` is ignored and only used locally.

## Contributing
PRs welcome. Please follow existing code style and keep changes minimal and focused.

## License
TBD
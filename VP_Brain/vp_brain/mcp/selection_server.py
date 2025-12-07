import base64
import os
import uuid
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import httpx
import requests
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .routes_voice import router as voice_router
from vp_brain.stt_gemini import transcribe_audio_wav

# Load .env and log a brief sanity check (without secrets)
load_dotenv()
print("[env] Loaded .env; keys present ->",
    "HYPER3D_API_KEY=", bool(os.getenv("HYPER3D_API_KEY")),
    "GOOGLE_API_KEY=", bool(os.getenv("GOOGLE_API_KEY")),
    "GEMINI_API_KEY=", bool(os.getenv("GEMINI_API_KEY")),
    "ELEVENLABS_API_KEY=", bool(os.getenv("ELEVENLABS_API_KEY")))

app = FastAPI(title="VisionPilot Selection Server")
app.include_router(voice_router, prefix="/ai")

# --- TTS (ElevenLabs) ---
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
TTS_OUTPUT_DIR = os.getenv("TTS_OUTPUT_DIR", "static_tts")
os.makedirs(TTS_OUTPUT_DIR, exist_ok=True)

tts_router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    voice_id: str | None = None
    buddy_id: str | None = None


@tts_router.post("/tts")
async def tts_generate(req: TTSRequest):
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY not set")

    # Fallback to env voice id if not provided
    env_voice_id = os.getenv("ELEVENLABS_VOICE_ID")
    voice_id = req.voice_id or env_voice_id
    if not voice_id:
        raise HTTPException(status_code=400, detail="voice_id missing and ELEVENLABS_VOICE_ID not set")

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": req.text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.8,
        },
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(tts_url, headers=headers, json=payload)
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"ElevenLabs error: {resp.text}")
        audio_bytes = resp.content

    file_id = str(uuid.uuid4())
    file_name = f"{file_id}.mp3"
    file_path = os.path.join(TTS_OUTPUT_DIR, file_name)

    with open(file_path, "wb") as f:
        f.write(audio_bytes)

    public_base = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")
    audio_url = f"{public_base}/static_tts/{file_name}"

    return {"audio_url": audio_url}


@tts_router.get("/tts/test")
async def tts_test():
    """
    Generate a short test clip using the env-configured ELEVENLABS_VOICE_ID.
    Returns a public URL to the generated audio.
    """
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY not set")

    env_voice_id = os.getenv("ELEVENLABS_VOICE_ID")
    if not env_voice_id:
        raise HTTPException(status_code=400, detail="ELEVENLABS_VOICE_ID not set in .env")

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{env_voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": "Hello from VisionPilot. This is a quick TTS test.",
        "model_id": "eleven_turbo_v2",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(tts_url, headers=headers, json=payload)
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail=f"ElevenLabs error: {resp.text}")
        audio_bytes = resp.content

    file_id = str(uuid.uuid4())
    file_name = f"{file_id}.mp3"
    file_path = os.path.join(TTS_OUTPUT_DIR, file_name)
    with open(file_path, "wb") as f:
        f.write(audio_bytes)

    public_base = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")
    audio_url = f"{public_base}/static_tts/{file_name}"
    return {"audio_url": audio_url}


app.include_router(tts_router)
app.mount("/static_tts", StaticFiles(directory=TTS_OUTPUT_DIR), name="static_tts")


# --- Voice command STT endpoint (hard override; no more stub) ---
@app.post("/voice/command")
async def voice_command(audio: UploadFile = File(...)):
    """
    Accepts a WAV file from Unity and returns:
      - user_text: transcription (Gemini STT)
      - ai_text: echo reply we can show in UI
    """
    data = await audio.read()

    try:
        text = transcribe_audio_wav(data) or ""
    except Exception as e:
        print("Gemini STT error:", e)
        text = "(STT error or empty audio)"

    ai_text = f"I heard: {text}"

    return {
        "user_text": text,
        "ai_text": ai_text,
        "action": "spawn",
        "effects": {
            "highlight": True,
            "hologram": True,
        },
        "model_url": None,
        "voice_b64": None,
    }


class SegmentRequest(BaseModel):
    segment_group_id: str
    label: str | None = None


class AIResponse(BaseModel):
    segment_group_id: str
    intent: str
    action: str
    message: str
    emotion: str = "neutral"
    effects: Dict[str, bool] = Field(default_factory=dict)
    model_url: Optional[str] = None


SEGMENTS = {
    "cover": {
        "description": "Front cover of the magic book",
    },
    "page_1": {
        "description": "First AR page / intro scene",
    },
    "page_2": {
        "description": "Second AR page / volcano scene",
    },
    "page_3": {
        "description": "Third AR page / whatever",
    },
    "chapter_2": {
        "description": "Chapter 2 spread",
    },
}


class Selection(BaseModel):
    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)
    source: str = "demo"
    segment_id: Optional[str] = None


class SelectionOut(BaseModel):
    x: float
    y: float
    source: str
    segment_id: Optional[str]
    ts: datetime


# Initial dummy value
latest_selection = SelectionOut(
    x=0.5,
    y=0.5,
    source="init",
    segment_id=None,
    ts=datetime.utcnow(),
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/selection", response_model=SelectionOut)
def get_selection():
    return latest_selection


@app.post("/selection", response_model=SelectionOut)
def set_selection(sel: Selection):
    global latest_selection

    latest_selection = SelectionOut(
        x=sel.x,
        y=sel.y,
        source=sel.source,
        segment_id=sel.segment_id,
        ts=datetime.utcnow(),
    )
    return latest_selection


@app.post("/ai/segment", response_model=AIResponse)
async def handle_segment(req: SegmentRequest) -> AIResponse:
    sgid = req.segment_group_id

    # Special demo object
    if sgid == "plant_01":
        return AIResponse(
            segment_group_id=sgid,
            intent="educational_fact",
            action="speak_highlight_and_spawn_hologram",
            message="This is Peace Lily. It likes indirect light and moist soil.",
            emotion="friendly",
            effects={"highlight": True, "hologram": True},
            model_url="https://your-cdn-or-hyper3d-url/plant_01.glb",
        )

    # TEMP: simple hardcoded logic for demo
    if sgid.startswith("plant"):
        return AIResponse(
            segment_group_id=sgid,
            intent="educational_fact",
            action="speak_and_highlight",
            message=f"This is {req.label or 'a plant'}. It likes indirect light and moist soil.",
            emotion="friendly",
            effects={"highlight": True, "hologram": False},
        )

    if sgid.startswith("book"):
        return AIResponse(
            segment_group_id=sgid,
            intent="assistant_tip",
            action="speak",
            message="You were reading this last time. Do you want a quick summary?",
            emotion="neutral",
            effects={"highlight": False, "hologram": False},
        )

    # default fallback
    return AIResponse(
        segment_group_id=sgid,
        intent="smalltalk",
        action="speak",
        message="I see something interesting there. I'll learn more about it next time.",
        emotion="casual",
        effects={"highlight": False, "hologram": False},
    )


# -------------------------------------------------------------------
# Hyper3D integration
# -------------------------------------------------------------------
HYPER3D_API_KEY = os.getenv("HYPER3D_API_KEY")
if not HYPER3D_API_KEY:
    raise RuntimeError("HYPER3D_API_KEY missing in .env")

HYPER3D_BASE_URL = "https://api.hyper3d.com/api/v2"
HYPER3D_TIER = os.getenv("HYPER3D_TIER", "Gen-2")
HYPER3D_MESH_MODE = os.getenv("HYPER3D_MESH_MODE", "Raw")
HYPER3D_MATERIAL = os.getenv("HYPER3D_MATERIAL", "PBR")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "hyper3d"
INPUT_DIR = DATA_DIR / "inputs"
INPUT_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "hyper3d_buddies.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS hyper3d_buddies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image_path TEXT NOT NULL,
            hyper_task_uuid TEXT NOT NULL,
            subscription_key TEXT NOT NULL,
            status TEXT NOT NULL,
            model_url TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()


init_db()


class Hyper3DGenerateRequest(BaseModel):
    image_b64: str
    name: str


class Hyper3DGenerateResponse(BaseModel):
    buddy_id: int
    status: str
    hyper_task_uuid: str
    subscription_key: str


class Hyper3DStatusResponse(BaseModel):
    buddy_id: int
    status: str
    model_url: Optional[str] = None


def hyper3d_submit_task(image_path: Path) -> dict:
    url = f"{HYPER3D_BASE_URL}/rodin"

    with open(image_path, "rb") as f:
        image_data = f.read()

    files = {
        "images": (image_path.name, image_data, "image/jpeg"),
        "tier": (None, HYPER3D_TIER),
        "mesh_mode": (None, HYPER3D_MESH_MODE),
        "material": (None, HYPER3D_MATERIAL),
    }

    headers = {"Authorization": f"Bearer {HYPER3D_API_KEY}"}

    resp = requests.post(url, files=files, headers=headers, timeout=120)
    if not resp.ok:
        raise HTTPException(status_code=502, detail=f"Hyper3D submit failed: {resp.text}")
    return resp.json()


def hyper3d_check_status(subscription_key: str) -> dict:
    url = f"{HYPER3D_BASE_URL}/status"
    headers = {
        "Authorization": f"Bearer {HYPER3D_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"subscription_key": subscription_key}
    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    if not resp.ok:
        raise HTTPException(status_code=502, detail=f"Hyper3D status failed: {resp.text}")
    return resp.json()


def hyper3d_download_results(task_uuid: str) -> dict:
    url = f"{HYPER3D_BASE_URL}/download"
    headers = {
        "Authorization": f"Bearer {HYPER3D_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"task_uuid": task_uuid}
    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    if not resp.ok:
        raise HTTPException(status_code=502, detail=f"Hyper3D download failed: {resp.text}")
    return resp.json()


def save_base64_image(image_b64: str) -> Path:
    # Handle "data:image/png;base64,..." prefixes
    if "," in image_b64:
        image_b64 = image_b64.split(",", 1)[1]

    raw = base64.b64decode(image_b64)
    fname = f"{uuid.uuid4().hex}.jpg"
    out_path = INPUT_DIR / fname
    with open(out_path, "wb") as f:
        f.write(raw)
    return out_path


@app.post("/hyper3d/generate", response_model=Hyper3DGenerateResponse)
def hyper3d_generate(payload: Hyper3DGenerateRequest):
    # 1) Save incoming image
    image_path = save_base64_image(payload.image_b64)

    # 2) Submit to Hyper3D
    task = hyper3d_submit_task(image_path)
    task_uuid = task.get("uuid")
    jobs = task.get("jobs") or {}
    subscription_key = jobs.get("subscription_key")

    if not task_uuid or not subscription_key:
        raise HTTPException(status_code=502, detail=f"Unexpected Hyper3D response: {task}")

    now = datetime.utcnow().isoformat()

    # 3) Insert into DB
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO hyper3d_buddies
            (name, image_path, hyper_task_uuid, subscription_key, status, model_url, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload.name,
            str(image_path),
            task_uuid,
            subscription_key,
            "submitted",
            None,
            now,
            now,
        ),
    )
    buddy_id = cur.lastrowid
    conn.commit()
    conn.close()

    return Hyper3DGenerateResponse(
        buddy_id=buddy_id,
        status="submitted",
        hyper_task_uuid=task_uuid,
        subscription_key=subscription_key,
    )


@app.get("/hyper3d/status/{buddy_id}", response_model=Hyper3DStatusResponse)
def hyper3d_status(buddy_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM hyper3d_buddies WHERE id = ?",
        (buddy_id,),
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Buddy not found")

    status = row["status"]
    model_url = row["model_url"]
    hyper_task_uuid = row["hyper_task_uuid"]
    subscription_key = row["subscription_key"]

    # If already done/failed and model_url recorded, just return
    if status in ("done", "failed"):
        conn.close()
        return Hyper3DStatusResponse(buddy_id=buddy_id, status=status, model_url=model_url)

    # Otherwise call Hyper3D /status
    status_resp = hyper3d_check_status(subscription_key)
    jobs = status_resp.get("jobs", [])

    # If Hyper3D structure changes, bail safely
    if not isinstance(jobs, list) or len(jobs) == 0:
        conn.close()
        raise HTTPException(status_code=502, detail=f"Unexpected Hyper3D status response: {status_resp}")

    job_statuses = {j.get("uuid"): j.get("status") for j in jobs}
    all_done = all(s in ("Done", "Failed") for s in job_statuses.values())
    any_failed = any(s == "Failed" for s in job_statuses.values())

    now = datetime.utcnow().isoformat()

    if all_done:
        if any_failed:
            status = "failed"
            model_url = None
        else:
            download_resp = hyper3d_download_results(hyper_task_uuid)
            items = download_resp.get("list", [])
            chosen = None
            for item in items:
                name = item.get("name", "")
                if name.lower().endswith(".glb"):
                    chosen = item
                    break
            if chosen is None and items:
                chosen = items[0]
            model_url = chosen.get("url") if chosen else None
            status = "done"

        cur.execute(
            """
            UPDATE hyper3d_buddies
            SET status = ?, model_url = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, model_url, now, buddy_id),
        )
        conn.commit()

    else:
        status = "running"
        cur.execute(
            """
            UPDATE hyper3d_buddies
            SET status = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, now, buddy_id),
        )
        conn.commit()

    conn.close()
    return Hyper3DStatusResponse(buddy_id=buddy_id, status=status, model_url=model_url)


if __name__ == "__main__":
    # Allow running directly or via `python -m vp_brain.mcp.selection_server`
    import sys
    import pathlib
    try:
        import uvicorn  # type: ignore
    except Exception as exc:
        raise SystemExit(
            "Uvicorn is required to run the server. Install with 'pip install uvicorn'"
        ) from exc

    # Ensure project root is on sys.path when running directly
    project_root = pathlib.Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    uvicorn.run(
        "vp_brain.mcp.selection_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )

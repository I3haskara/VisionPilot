import base64
import os
import uuid
import sqlite3
import os
import tempfile
from uuid import uuid4
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from openai import OpenAI

# ============================================================
#  BASIC APP SETUP
# ============================================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # lock this down later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static dir to serve generated audio files
STATIC_DIR = Path("static/audio")
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Serve /static/*  =>  ./static/*
app.mount("/static", StaticFiles(directory="static"), name="static")

# ============================================================
#  OPENAI CLIENT + CONFIG
# ============================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in environment")

client = OpenAI(api_key=OPENAI_API_KEY)

BUDDY_SYSTEM_PROMPT = os.getenv(
    "BUDDY_SYSTEM_PROMPT",
    (
        "You are Buddy, a supportive, slightly witty AR/VR companion. "
        "Speak in short, natural sentences. Respond like you are inside "
        "a mixed-reality world helping the user explore and play. "
        "Avoid long monologues; keep it tight and helpful."
    ),
)

# Models (centralized here so you can tweak later)
STT_MODEL = "gpt-4o-mini-transcribe"  # audio -> text
CHAT_MODEL = "gpt-4o-mini"            # conversation
TTS_MODEL = "gpt-4o-mini-tts"         # text -> audio


# ============================================================
#  HEALTH CHECK
# ============================================================

@app.get("/ping")
async def ping():
    return {
        "status": "ok",
        "service": "visionpilot-backend",
        "voice_pipeline": "openai-only",
    }


# ============================================================
#  VOICE COMMAND ENDPOINT (STT + CHAT + TTS)
# ============================================================

@app.post("/voice/command")
async def voice_command(file: UploadFile = File(...)):
    """
    1) Receive user audio from Unity (multipart file)
    2) Transcribe with OpenAI STT
    3) Generate Buddy reply with OpenAI chat
    4) Generate speech with OpenAI TTS
    5) Return transcript, reply_text, and audio_url (mp3)
    """

    # ----------------------------
    # 1. Save uploaded audio temp
    # ----------------------------
    try:
        suffix = Path(file.filename).suffix or ".wav"
    except Exception:
        suffix = ".wav"

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            raw_data = await file.read()
            tmp.write(raw_data)
            tmp_path = Path(tmp.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded audio: {e}")

    # ----------------------------
    # 2. STT: Speech -> Text
    # ----------------------------
    try:
        with tmp_path.open("rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=STT_MODEL,
                file=audio_file,
                language="en",
            )
        user_text = (transcription.text or "").strip()
    except Exception as e:
        # Clean up tmp file even on failure
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass
        raise HTTPException(status_code=502, detail=f"STT failed: {e}")

    # Clean temp file after successful STT
    try:
        tmp_path.unlink(missing_ok=True)
    except Exception:
        pass

    if not user_text:
        raise HTTPException(status_code=400, detail="Empty transcription from audio")

    # ----------------------------
    # 3. Chat: generate Buddy reply
    # ----------------------------
    try:
        completion = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": BUDDY_SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            temperature=0.8,
        )
        reply_text = (completion.choices[0].message.content or "").strip()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Chat completion failed: {e}")

    if not reply_text:
        raise HTTPException(status_code=500, detail="Empty reply from chat model")

    # ----------------------------
    # 4. TTS: reply_text -> mp3
    # ----------------------------
    audio_id = f"{uuid4().hex}.mp3"
    audio_path = STATIC_DIR / audio_id

    try:
        # Stream TTS directly to file for lower memory usage
        with client.audio.speech.with_streaming_response.create(
            model=TTS_MODEL,
            voice="alloy",  # other voices available: "verse", "nova", etc.
            input=reply_text,
        ) as response:
            response.stream_to_file(audio_path)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TTS failed: {e}")

    # ----------------------------
    # 5. Response to Unity
    # ----------------------------
    # Unity can hit: http://127.0.0.1:8000/static/audio/<audio_id>
    audio_url = f"/static/audio/{audio_id}"

    return {
        "success": True,
        "provider": "openai",
        "transcript": user_text,
        "reply_text": reply_text,
        "audio_url": audio_url,
    }


# ============================================================
#  (OPTIONAL) TEXT-ONLY CHAT ENDPOINT
#  Useful if you want non-voice messages from Unity later.
# ============================================================

@app.post("/chat")
async def chat(message: str):
    try:
        completion = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": BUDDY_SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            temperature=0.8,
        )
        reply_text = (completion.choices[0].message.content or "").strip()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Chat failed: {e}")

    return {
        "success": True,
        "reply_text": reply_text,
    }


import io
import os
import pathlib
from dotenv import load_dotenv

# Load .env explicitly from the project root (VP_Brain)
_project_root = pathlib.Path(__file__).resolve().parents[1]
_env_path = _project_root / ".env"
load_dotenv(dotenv_path=_env_path)

import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY (or GEMINI_API_KEY) is not set in .env at " + str(_env_path))

genai.configure(api_key=GOOGLE_API_KEY)

# Use Gemini’s audio-text model; adjust name if Google changes it
MODEL_NAME = "gemini-1.5-flash"  # supports audio+text multimodal


def transcribe_audio_wav(data: bytes) -> str:
    """
    Takes raw WAV bytes and returns transcript text.
    Keep it simple for hackathon.
    """
    audio_file = {
        "mime_type": "audio/wav",
        "data": data,
    }

    model = genai.GenerativeModel(MODEL_NAME)

    # Simple prompt: "transcribe this audio"
    resp = model.generate_content(
        [
            "You are a speech-to-text system. Output only the transcription.",
            audio_file,
        ]
    )

    text = resp.text or ""
    return text.strip()

import os
from dotenv import load_dotenv
from typing import Optional

import google.generativeai as genai

# Load variables from .env if present
load_dotenv()

# Support either env var name
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY or GOOGLE_API_KEY not set in environment")

genai.configure(api_key=API_KEY)


def transcribe_audio_gemini_wav(audio_bytes: bytes) -> Optional[str]:
    """
    Takes raw WAV bytes and returns transcribed text using Gemini STT.
    Returns None if transcription fails.
    """
    try:
        # Wrap bytes as a pseudo file for the client
        audio_file = {
            "mime_type": "audio/wav",
            "data": audio_bytes,
        }

        # Use a lightweight audio-capable model; adjust model name if needed
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Ask Gemini to transcribe / summarize as plain text
        response = model.generate_content(
            [
                "You are a speech recognizer. Transcribe this audio accurately as plain text only.",
                audio_file,
            ]
        )

        # Gemini responses usually have a single text piece
        text = response.text.strip()
        return text or None

    except Exception as e:
        # Log and fall back gracefully
        print(f"[Gemini STT] Error: {e}")
        return None

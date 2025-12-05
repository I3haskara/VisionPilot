from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

router = APIRouter()


class VoiceAIResponse(BaseModel):
    user_text: str
    ai_text: str
    action: str
    effects: dict
    model_url: str | None = None
    voice_b64: str | None = None


def transcribe_audio_to_text(audio_bytes: bytes) -> str:
    # TODO: plug in real STT (Whisper/OpenAI/etc.)
    return "<transcribed text stub>"


async def run_ai_for_text(user_text: str) -> dict:
    # TODO: reuse logic similar to /ai/segment handler
    return {
        "ai_text": f"You said: {user_text}",
        "action": "speak",
        "effects": {"highlight": False},
        "model_url": None,
        "voice_b64": None,
    }


@router.post("/voice_command", response_model=VoiceAIResponse)
async def voice_command(audio: UploadFile = File(...)):
    # 1) Read audio bytes
    audio_bytes = await audio.read()

    # 2) Run STT
    user_text = transcribe_audio_to_text(audio_bytes)

    # 3) Call AI logic
    ai_result = await run_ai_for_text(user_text)

    return VoiceAIResponse(
        user_text=user_text,
        ai_text=ai_result["ai_text"],
        action=ai_result["action"],
        effects=ai_result["effects"],
        model_url=ai_result.get("model_url"),
        voice_b64=ai_result.get("voice_b64"),
    )
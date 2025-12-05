from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

router = APIRouter(tags=["voice"])


class Effects(BaseModel):
    highlight: bool = False
    hologram: bool = False


class VoiceAIResponse(BaseModel):
    user_text: str
    ai_text: str
    action: str
    effects: Effects
    model_url: str | None = None
    voice_b64: str | None = None


@router.post("/voice_command", response_model=VoiceAIResponse)
async def voice_command(audio: UploadFile = File(...)) -> VoiceAIResponse:
    audio_bytes = await audio.read()
    print(f"[voice_command] Received audio bytes: {len(audio_bytes)}")

    # Stubbed STT + AI logic
    user_text = "Test voice command (fake STT)"
    ai_text = f"I heard: {user_text}. This is a stub response."

    return VoiceAIResponse(
        user_text=user_text,
        ai_text=ai_text,
        action="spawn",
        effects=Effects(highlight=True, hologram=False),
        model_url=None,
        voice_b64=None,
    )

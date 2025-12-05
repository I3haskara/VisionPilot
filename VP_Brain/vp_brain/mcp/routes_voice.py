from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

from gemini_stt import transcribe_audio_gemini_wav

router = APIRouter(
    tags=["voice"],
    prefix="",
    responses={200: {"description": "Voice command processed"}},
)


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


@router.post(
    "/voice_command",
    response_model=VoiceAIResponse,
    summary="Voice Command",
    description="Upload an audio file (WAV recommended) to transcribe with Gemini STT and receive an AI response.",
    response_description="AI response including user transcription and effects",
)
async def voice_command(audio: UploadFile = File(...)) -> VoiceAIResponse:
    audio_bytes = await audio.read()
    print(f"[voice_command] Received audio bytes: {len(audio_bytes)}")

    # 1) REAL Gemini STT
    user_text = transcribe_audio_gemini_wav(audio_bytes)
    if not user_text:
        user_text = "(could not transcribe audio)"
        ai_text = "Sorry, I couldn’t understand that. Please try again."
        return VoiceAIResponse(
            user_text=user_text,
            ai_text=ai_text,
            action="none",
            effects=Effects(highlight=False, hologram=False),
            model_url=None,
            voice_b64=None,
        )

    print(f"[voice_command] Transcribed text: {user_text!r}")

    # 2) TEMP: simple response – **NO STUB TEXT**
    ai_text = "GEMINI LIVE 777 – if you see this, Render is using THIS file."

    return VoiceAIResponse(
        user_text=user_text,
        ai_text=ai_text,
        action="spawn",
        effects=Effects(highlight=True, hologram=False),
        model_url=None,
        voice_b64=None,
    )

import os
import simpleaudio as sa
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

def speak(text: str, voice_id: str = None):
    """
    Convert text to speech using ElevenLabs and play the audio.
    """
    vid = voice_id or VOICE_ID

    if not vid:
        print("ERROR: No voice ID set for ElevenLabs.")
        return

    # Send text to TTS model
    audio_chunks = client.text_to_speech.convert(
        voice_id=vid,
        text=text,
        model_id="eleven_multilingual_v2"
    )

    # Save and play
    output_path = "vp_output.wav"
    with open(output_path, "wb") as f:
        for chunk in audio_chunks:
            f.write(chunk)

    wave_obj = sa.WaveObject.from_wave_file(output_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()

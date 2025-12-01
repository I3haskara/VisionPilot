from vp_brain.mcp.command_sender import CommandSender
from vp_brain.audio.tts_elevenlabs import speak
import asyncio

async def visionpilot_loop():
    sender = CommandSender()
    await sender.init()

    # camera + hand tracking setup...
    # inside your loop:
    coords = (0.5, 0.3)  # Example normalized coordinates, replace with actual tracking logic
    if coords:
        nx, ny = coords
        # Send to FastAPI selection server
        import requests
        try:
            resp = requests.post(
                "http://127.0.0.1:8000/selection",
                json={"x": nx, "y": ny},
                timeout=0.2,
            )
            print("[Selection Server Response]", resp.json())
        except Exception as e:
            print("[Selection Server Error]", e)
        # Send to Unity MCP
        response = await sender.send_select(nx, ny)
        print("[UNITY RESPONSE]", response)
        speak("Object selected.")

if __name__ == "__main__":
    asyncio.run(visionpilot_loop())

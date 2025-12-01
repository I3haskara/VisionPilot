import asyncio
import json
import websockets

WS_URL = "ws://localhost:8090"  # same port shown in MCP Unity window

async def send_selection(nx: float, ny: float, msg_id: int = 1):
    payload = {
        "jsonrpc": "2.0",
        "id": msg_id,
        "method": "tools/call",
        "params": {
            "name": "update_component",
            "arguments": {
                # Must match your GameObject name in the scene
                "gameObject": "MCP_Controller",
                # Must match the component class name
                "component": "MCPController",
                "fields": {
                    "normalizedX": nx,
                    "normalizedY": ny
                }
            }
        }
    }

    async with websockets.connect(WS_URL) as ws:
        await ws.send(json.dumps(payload))
        # Optional: read response
        resp = await ws.recv()
        print("MCP response:", resp)

# Example usage
# asyncio.run(send_selection(0.5, 0.3))

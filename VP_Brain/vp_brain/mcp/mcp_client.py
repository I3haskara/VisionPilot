import asyncio
import json
import websockets

class MCPClient:
    def __init__(self, uri="ws://localhost:8080"):
        self.uri = uri
        self.websocket = None
        self.request_id = 0

    async def connect(self):
        print(f"[MCP] Connecting to {self.uri} ...")
        self.websocket = await websockets.connect(self.uri)
        print("[MCP] Connected.")

    async def send(self, method: str, params: dict):
        if not self.websocket:
            raise RuntimeError("WebSocket not connected.")

        self.request_id += 1

        payload = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }

        await self.websocket.send(json.dumps(payload))
        return await self.websocket.recv()

    async def close(self):
        if self.websocket:
            await self.websocket.close()
            print("[MCP] Connection closed.")

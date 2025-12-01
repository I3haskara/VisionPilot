import asyncio
from .mcp_client import MCPClient

# vp_brain/mcp/command_sender.py
UNITY_WS_URL = "ws://localhost:8090"


class CommandSender:
    def __init__(self, uri=UNITY_WS_URL):
        self.client = MCPClient(uri)

    async def init(self):
        await self.client.connect()

    async def send_select(self, x, y):
        return await self.client.send(
            method="tools/call",
            params={
                "tool_name": "SelectObject",
                "arguments": {"x": x, "y": y}
            }
        )

    async def send_action(self, action_name: str, target_id: str):
        return await self.client.send(
            method="tools/call",
            params={
                "tool_name": action_name,
                "arguments": {"id": target_id}
            }
        )

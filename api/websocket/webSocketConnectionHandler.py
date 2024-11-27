import asyncio
import json

from starlette.websockets import WebSocket, WebSocketDisconnect

from services.player import Player


class WebSocketConnectionHandler:
    def __init__(self, player: Player):
        self.player = player

    async def handle(self, websocket: WebSocket):
        """Handle WebSocket connection and communication."""
        await websocket.accept()
        await websocket.accept()
        try:
            if self.player:
                await self.player.play(websocket)
        finally:
            await websocket.close()
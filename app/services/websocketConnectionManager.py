from typing import List, Any

from starlette.websockets import WebSocket


class WebsocketConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast_text(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def broadcast_json(self, message: Any):
        for connection in self.active_connections:
            await connection.send_json(message)

    async def broadcast_bytes(self, message: bytes):
        for connection in self.active_connections:
            await connection.send_bytes(message)

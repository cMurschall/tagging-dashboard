import logging
from typing import List, Any

from starlette.websockets import WebSocket

logger = logging.getLogger('uvicorn.error')


class WebsocketConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected: {websocket}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected: {websocket}")

    async def _safe_send(self, connection: WebSocket, send_method, message):
        try:
            await send_method(message)
        except Exception as e:
            logger.warning(f"Failed to send to connection {connection}: {e}")
            self.disconnect(connection)

    async def broadcast_text(self, message: str):
        for connection in list(self.active_connections):  # copy to avoid issues during iteration
            await self._safe_send(connection, connection.send_text, message)

    async def broadcast_bytes(self, message: bytes):
        for connection in list(self.active_connections):
            await self._safe_send(connection, connection.send_bytes, message)

    async def broadcast_json(self, message: dict, sender: WebSocket = None):
        for connection in list(self.active_connections):
            if connection == sender:
                logger.debug(f"Skipping sender connection: {connection}")
                continue
            await self._safe_send(connection, connection.send_json, message)

import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import asyncio

from app.dependencies import get_connection_manager
from app.services.websocketConnectionManager import WebsocketConnectionManager


class WebSockets:
    def __init__(self):
        self.router = APIRouter()
        self.logger = logging.getLogger("uvicorn.error")
        self._define_routes()

    def _define_routes(self):

        @self.router.websocket("/heartbeat")
        async def heartbeat_ws(websocket: WebSocket,
                               connection_manager: WebsocketConnectionManager = Depends(get_connection_manager)):

            await connection_manager.connect(websocket)
            try:
                while True:
                    await websocket.send_text("ping")
                    await asyncio.sleep(20)
            except WebSocketDisconnect:
                connection_manager.disconnect(websocket)

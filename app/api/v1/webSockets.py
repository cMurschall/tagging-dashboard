import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import asyncio

from app.dependencies import get_connection_manager_data, get_connection_manager_simulation_time
from app.services.websocketConnectionManager import WebsocketConnectionManager


class WebSockets:
    def __init__(self):
        self.router = APIRouter()
        self.logger = logging.getLogger("uvicorn.error")
        self._define_routes()

    def _define_routes(self):

        @self.router.websocket("/data")
        async def data_ws(websocket: WebSocket,
                          connection_manager: WebsocketConnectionManager = Depends(get_connection_manager_data)):

            await connection_manager.connect(websocket)
            try:
                while True:
                    await websocket.send_text("ping")
                    await asyncio.sleep(20)
            except WebSocketDisconnect:
                connection_manager.disconnect(websocket)

        @self.router.websocket("/simulationTime")
        async def simulation_time_ws(websocket: WebSocket, connection_manager: WebsocketConnectionManager = Depends(
            get_connection_manager_simulation_time)):

            await connection_manager.connect(websocket)
            try:
                while True:
                    data = await websocket.receive_json()
                    # Process data only if it's a simulation time update
                    if "timestamp" in data:
                        # Broadcast to other connected clients
                        await connection_manager.broadcast_json({
                            "timestamp": data["timestamp"]
                        }, sender=websocket)
            except WebSocketDisconnect:
                connection_manager.disconnect(websocket)

import asyncio
import json

from starlette.websockets import WebSocket, WebSocketDisconnect

from controllers.CsvPlayback import CSVPlayback

class WebSocketConnectionHandler:
    def __init__(self, playback: CSVPlayback):
        self.playback = playback

    async def handle(self, websocket: WebSocket):
        """Handle WebSocket connection and communication."""
        await websocket.accept()
        try:
            while True:
                message = await websocket.receive_text()
                if message == "play":
                    if self.playback.playback_task is None or self.playback.playback_task.done():
                        self.playback.playback_task = asyncio.create_task(
                            self.playback.play(websocket.send_json)
                        )
                elif message == "pause":
                    self.playback.pause()
                elif message.startswith("jump_to_timestamp"):
                    _, timestamp = message.split(":")
                    self.playback.jump_to_timestamp(float(timestamp))
                    if self.playback.is_playing and (
                        self.playback.playback_task is None or self.playback.playback_task.done()
                    ):
                        self.playback.playback_task = asyncio.create_task(
                            self.playback.play(websocket.send_json)
                        )
        except WebSocketDisconnect:
            self.playback.pause()
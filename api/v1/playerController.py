from http.client import HTTPException

from fastapi import APIRouter

from controllers.CsvLoader import CSVLoader
from controllers.CsvPlayback import CSVPlayback
from models.measurementModel import MeasurementModel

router = APIRouter()


class PlayerController:
    def __init__(self):
        self.router = APIRouter()
        self.playback = None
        self._define_routes()

    def _define_routes(self):
        @self.router.post("/load")
        async def load_file(file_name: str):
            """Load a new CSV file for playback."""
            loader = CSVLoader(file_name)
            self.playback = CSVPlayback(loader.load_all())
            return {"message": f"CSV file '{file_name}' loaded successfully"}

        @self.router.post("/play")
        async def play_stream():
            if not self.playback:
                raise HTTPException(status_code=400, detail="No file loaded for playback")
            if not self.playback.is_playing:
                self.playback.is_playing = True
                return {"message": "Playback started"}
            return {"message": "Playback is already running"}

        @self.router.post("/pause")
        async def pause_stream():
            if not self.playback:
                raise HTTPException(status_code=400, detail="No file loaded for playback")
            if self.playback.is_playing:
                self.playback.pause()
                return {"message": "Playback paused"}
            return {"message": "Playback is already paused"}

        @self.router.post("/toTimeStamp")
        async def jump_to_time(timestamp: float):
            if not self.playback:
                raise HTTPException(status_code=400, detail="No file loaded for playback")
            self.playback.jump_to_timestamp(timestamp)
            return {"message": f"Jumped to timestamp {timestamp}"}


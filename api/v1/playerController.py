from http.client import HTTPException

from fastapi import APIRouter

from models.measurementModel import MeasurementModel
from services.dataSources.csvDataSource import CSVDataSource
from services.dataSources.simulatedNetworkDataSource import SimulatedNetworkStreamDataSource
from services.player import Player

router = APIRouter()


class PlayerController:
    def __init__(self):
        self.router = APIRouter()
        self.playback = None
        self._define_routes()

    def _define_routes(self):

        @self.router.post("/load_csv")
        async def load_csv(file_path: str):
            global player
            data_source = CSVDataSource(file_path)
            player = Player(data_source)
            return {"message": f"CSV data source initialized from {file_path}"}

        @self.router.post("/load_stream")
        async def load_stream():
            global player
            data_source = SimulatedNetworkStreamDataSource()
            player = Player(data_source)
            return {"message": "Network stream data source initialized"}

        @self.router.post("/play")
        async def play():
            if player:
                player.play()
                return {"message": "Playback started"}
            return {"error": "No data source loaded"}

        @self.router.post("/pause")
        async def pause():
            if player:
                player.pause()
                return {"message": "Playback paused"}
            return {"error": "No data source loaded"}

        @self.router.post("/jump_to_timestamp")
        async def jump_to_timestamp(timestamp: float):
            if player:
                await player.jump_to_timestamp(timestamp)
                return {"message": f"Jumped to timestamp {timestamp}"}
            return {"error": "No data source loaded"}


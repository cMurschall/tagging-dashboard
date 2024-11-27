from http.client import HTTPException
from pathlib import Path

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...main import get_player
from ...services.dataSources.csvDataSource import CSVDataSource
from ...services.dataSources.simulatedNetworkDataSource import SimulatedNetworkStreamDataSource
from ...services.player import Player

router = APIRouter()


class LoadCsvPayload(BaseModel):
    file_name: str

class JumpToTimestampPayload(BaseModel):
    timestamp: float

class PlayerController:
    def __init__(self):
        self.router = APIRouter()
        self.playback = None
        self._define_routes()

        self.csv_file_folder = "D:/Praxisprojekt Herms"

    def _define_routes(self):

        @self.router.post("/load_csv")
        async def load_csv(payload: LoadCsvPayload,  player: Player = Depends(get_player)):
            file_name = payload.file_name
            file_path = Path(f"{self.csv_file_folder}/{file_name}")
            if file_path.is_file() is False:
                raise HTTPException(status_code=404, detail="File not found")

            data_source = CSVDataSource(file_path.name)
            player.set_data_source(data_source)
            return {"message": f"CSV data source initialized from {file_path}"}

        @self.router.post("/load_stream")
        async def load_stream(player: Player = Depends(get_player)):
            data_source = SimulatedNetworkStreamDataSource()
            player.set_data_source(data_source)
            return {"message": "Network stream data source initialized"}

        @self.router.post("/play")
        async def play(player: Player = Depends(get_player)):
            player.play()
            return {"message": "Playback started"}

        @self.router.post("/pause")
        async def pause(player: Player = Depends(get_player)):
            player.pause()
            return {"message": "Playback paused"}

        @self.router.post("/jump_to_timestamp")
        async def jump_to_timestamp(payload: JumpToTimestampPayload, player: Player = Depends(get_player)):
            await player.jump_to_timestamp(payload.timestamp)
            return {"message": f"Jumped to timestamp {payload.timestamp}"}


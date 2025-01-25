import subprocess
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, FileResponse

from pydantic import BaseModel

from ...dependencies import get_player, get_settings
from ...services.dataSources.csvDataSource import CSVDataSource
from ...services.dataSources.simulatedNetworkDataSource import SimulatedNetworkStreamDataSource
from ...services.player import Player
from ...settings import Settings

router = APIRouter()


class LoadCsvPayload(BaseModel):
    file_name: str


class JumpToTimestampPayload(BaseModel):
    timestamp: float


class ThumbnailsResponse(BaseModel):
    thumbnails: list[str]


class PlayerController:
    def __init__(self):
        self.router = APIRouter()
        self.playback = None
        self._define_routes()

    def _define_routes(self):

        @self.router.get("/video/{filename}")
        def get_video_stream(filename: str, settings: Settings = Depends(get_settings)) -> StreamingResponse:

            file_path = Path(settings.VIDEO_PATH) / filename
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Video not found")

            def video_streamer():
                with open(file_path, "rb") as file:
                    while chunk := file.read(1024 * 1024):  # Stream in chunks of 1 MB
                        yield chunk

            return StreamingResponse(video_streamer(), media_type="video/mp4")

        @self.router.get("/thumbnail/{filename}")
        def get_thumbnail(filename: str, settings: Settings = Depends(get_settings)) -> FileResponse:
            file_path = Path(settings.SPRITE_FOLDER) / filename
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Thumbnail not found")
            return FileResponse(file_path, media_type="image/png")

        # @self.router.post("/load_csv")
        # async def load_csv(payload: LoadCsvPayload, player: Player = Depends(get_player), settings: Settings = Depends(get_settings)):
        #     file_name = payload.file_name
        #
        #     csv_file_folder = settings.CSV_PATH;
        #     file_path = Path(f"{csv_file_folder}/{file_name}")
        #     if file_path.is_file() is False:
        #         raise HTTPException(status_code=404, detail="File not found")
        #
        #     data_source = CSVDataSource(file_path.name)
        #     player.set_data_source(data_source)
        #     return {"message": f"CSV data source initialized from {file_path}"}
        #
        # @self.router.post("/load_stream")
        # async def load_stream(player: Player = Depends(get_player)):
        #     data_source = SimulatedNetworkStreamDataSource()
        #     player.set_data_source(data_source)
        #     return {"message": "Network stream data source initialized"}
        #
        # @self.router.post("/play")
        # async def play(player: Player = Depends(get_player)):
        #     player.play()
        #     return {"message": "Playback started"}
        #
        # @self.router.post("/pause")
        # async def pause(player: Player = Depends(get_player)):
        #     player.pause()
        #     return {"message": "Playback paused"}
        #
        # @self.router.post("/jump_to_timestamp")
        # async def jump_to_timestamp(payload: JumpToTimestampPayload, player: Player = Depends(get_player)):
        #     await player.jump_to_timestamp(payload.timestamp)
        #     return {"message": f"Jumped to timestamp {payload.timestamp}"}

import subprocess
from http.client import HTTPException
from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, FileResponse

from pydantic import BaseModel

from ...dependencies import get_player
from ...services.dataSources.csvDataSource import CSVDataSource
from ...services.dataSources.simulatedNetworkDataSource import SimulatedNetworkStreamDataSource
from ...services.player import Player

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

        self.csv_file_folder = "D:/Praxisprojekt Herms"
        self.video_file_folder = "D:/Praxisprojekt Herms"

        self.thumbnail_folder = "./thumbnails"

    def _define_routes(self):

        @self.router.get("/video/{filename}")
        def get_video_stream(filename: str) -> StreamingResponse:

            file_path = Path(self.video_file_folder) / filename
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Video not found")

            def video_streamer():
                with open(file_path, "rb") as file:
                    while chunk := file.read(1024 * 1024):  # Stream in chunks of 1 MB
                        yield chunk

            return StreamingResponse(video_streamer(), media_type="video/mp4")

        @self.router.get("/thumbnail/{filename}")
        def generate_thumbnails(filename: str) -> ThumbnailsResponse:
            video_path = Path(self.video_file_folder) / filename
            if not video_path.exists():
                raise HTTPException(status_code=404, detail="Video not found")

            # Create thumbnail directory for this video
            video_thumbnail_dir = Path(self.thumbnail_folder) / filename
            video_thumbnail_dir.mkdir(exist_ok=True)

            # Generate thumbnails using FFmpeg
            thumbnail_pattern = str(video_thumbnail_dir / "thumb_%03d.jpg")
            command = [
                "ffmpeg",
                "-i", str(video_path),
                "-vf", "fps=1",  # Generate 1 thumbnail per second
                thumbnail_pattern,
                "-hide_banner",
                "-loglevel", "error"
            ]
            subprocess.run(command, check=True)

            # Return list of generated thumbnails
            thumbnails = sorted(video_thumbnail_dir.glob("thumb_*.jpg"))
            if not thumbnails:
                raise HTTPException(status_code=500, detail="Thumbnails could not be generated")

            return {"thumbnails": [f"/thumbnails/{filename}/{thumb.name}" for thumb in thumbnails]}

        @self.router.get("/thumbnails/{filename}/{thumb}")
        def get_thumbnail(filename: str, thumb: str) -> FileResponse:
            thumbnail_path = Path(self.thumbnail_folder) / filename / thumb
            if not thumbnail_path.exists():
                raise HTTPException(status_code=404, detail="Thumbnail not found")
            return FileResponse(thumbnail_path, media_type="image/jpeg")

        @self.router.post("/load_csv")
        async def load_csv(payload: LoadCsvPayload, player: Player = Depends(get_player)):
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

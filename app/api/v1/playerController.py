import logging
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Union, Any, Generator

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse, FileResponse, Response

from pydantic import BaseModel

from ...dependencies import get_player, get_settings, get_testdata_manager
from ...services.dataSources.csvDataSource import CSVDataSource
from ...services.dataSources.simulatedNetworkDataSource import SimulatedNetworkStreamDataSource
from ...services.player import Player
from ...services.testDriveDataService import TestDriveDataService
from ...settings import Settings

router = APIRouter()


class LoadCsvPayload(BaseModel):
    file_name: str


class JumpToTimestampPayload(BaseModel):
    timestamp: float


class ThumbnailsResponse(BaseModel):
    thumbnails: list[str]


class ColumnInfo(BaseModel):
    name: str
    type: str


class ColumnsResponse(BaseModel):
    columns: List[ColumnInfo]


class JsonResponseModel(BaseModel):
    data: List[Dict[str, Any]]


class FeatherResponseModel(BaseModel):
    detail: str


class PlayerController:
    def __init__(self):
        self.router = APIRouter()
        self.playback = None
        self.logger = logging.getLogger('uvicorn.error')

        self._define_routes()

    def _define_routes(self):

        @self.router.get("/video/{filename}")
        async def get_video_stream(filename: str, request: Request,
                                   settings: Settings = Depends(get_settings)) -> StreamingResponse:

            file_path = Path(settings.VIDEO_PATH) / filename
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Video not found")

            range_header = request.headers.get("range")
            if range_header:
                start, end = range_header.replace("bytes=", "").split("-")
                start = int(start)
                end = int(end) if end else start + (50 * 1024 * 1024)
                with open(file_path, "rb") as file:
                    file.seek(start)
                    data = file.read(end - start)
                    filesize = str(file_path.stat().st_size)
                    headers = {
                        'Content-Range': f'bytes {str(start)}-{str(end)}/{filesize}',
                        'Accept-Ranges': 'bytes',
                        'Content-Length': str(len(data)),
                    }
                    return Response(data, status_code=206, headers=headers, media_type="video/mp4")
            return FileResponse(file_path)

        @self.router.get("/thumbnail/{filename}")
        def get_thumbnail(filename: str, settings: Settings = Depends(get_settings)) -> FileResponse:
            self.logger.info(f"Thumbnail file requested: {filename}")
            file_path = Path(settings.SPRITE_FOLDER) / filename
            self.logger.info(f"Thumbnail requested: {file_path}")
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Thumbnail not found")
            return FileResponse(file_path, media_type="image/png")

        @self.router.get("/columns")
        async def get_data(service: TestDriveDataService = Depends(get_testdata_manager)) -> ColumnsResponse:
            columns_info = [
                {"name": col, "type": str(dtype)} for col, dtype in service.get_csv_data_columns()
            ]

            return {"columns": columns_info}

        @self.router.get("/data/json", summary="Get data as JSON",
                         description="Retrieve the selected data as a JSON response.")
        async def get_data_as_json(
                columns: str = Query(None, description="Comma-separated list of columns to include"),
                service: TestDriveDataService = Depends(get_testdata_manager)) -> JsonResponseModel:
            # Parse the columns
            column_list = columns.split(",") if columns else []
            data = service.get_csv_data(column_list)
            return {"data": data.to_dict(orient="records")}

        @self.router.get("/data/feather", summary="Get data as Feather",
                         description="Retrieve the selected data as a Feather file download.")
        async def get_data_as_feather(
                columns: str = Query(None, description="Comma-separated list of columns to include"),
                service: TestDriveDataService = Depends(get_testdata_manager)) -> FeatherResponseModel:
            # Parse the columns
            column_list = columns.split(",") if columns else []
            data = service.get_csv_data(column_list)

            # Save to a Feather file
            feather_file = "data.feather"
            data.reset_index().to_feather(feather_file)  # Feather requires no index issues

            # Return the Feather file as a response
            return FileResponse(
                feather_file,
                media_type="application/octet-stream",
                filename="data.feather"
            )

import logging
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Union, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, FileResponse

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
        def get_video_stream(filename: str, settings: Settings = Depends(get_settings)) -> StreamingResponse:

            file_path = Path(settings.VIDEO_PATH) / filename
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Video not found")

            def video_streamer():
                with open(file_path, "rb") as file:
                    while chunk := file.read(1024 * 1024):  # Stream in chunks of 1 MB
                        yield chunk

            return StreamingResponse(video_streamer(), media_type="video/mp4")

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

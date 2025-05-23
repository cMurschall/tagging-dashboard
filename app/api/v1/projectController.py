import logging
import os
import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from app.dependencies import get_testdata_manager, get_settings
from app.models.testDriveDataInfo import TestDriveDataInfo
from app.models.testDriveMetaData import TestDriveMetaData
from app.models.testDriveProjectInfo import TestDriveProjectInfo
from app.models.testDriveTagInfo import TestDriveTagInfo
from app.models.testDriveVideoInfo import TestDriveVideoInfo
from app.services.testDriveDataService import TestDriveDataService
from app.settings import Settings


class CreateProjectPayload(BaseModel):
    csv_file_name: str = Field("", title="CSV file name", description="The name of the CSV file")
    video_file_name: str = Field("", title="Video file name", description="The name of the video file")
    driver_name: str = Field("", title="Driver name", description="The name of the driver")
    vehicle_name: str = Field("", title="Vehicle name", description="The name of the vehicle")
    route_name: str = Field("", title="Route name", description="The name of the route")
    notes: str = Field("", title="Notes", description="Notes for the test drive project")


class TimeRangeTagModel(BaseModel):
    start_timestamp: float = Field(0.0, title="Start Timestamp", description="The start timestamp of the tag")
    end_timestamp: float = Field(0.0, title="End Timestamp", description="The end timestamp of the tag")
    notes: str = Field("", title="Notes", description="Notes for the tag")


class CSVFileResponse(BaseModel):
    files: List[str]


class VideoFileResponse(BaseModel):
    files: List[str]


class AllTestDrivesResponse(BaseModel):
    testdrives: List[TestDriveProjectInfo]


class TestDriveResponse(BaseModel):
    testdrive: TestDriveProjectInfo


class OptionalTestDriveResponse(BaseModel):
    testdrive: Optional[TestDriveProjectInfo]


class UploadResponse(BaseModel):
    filename: str = Field("", title="Filename", description="The name of the file")


class ProjectController:
    def __init__(self):
        self.router = APIRouter()
        self.playback = None
        self.logger = logging.getLogger("uvicorn.error")
        self._define_routes()

    def _define_routes(self):
        @self.router.get("/files/csv", response_model=CSVFileResponse)
        async def get_csv_files(settings: Settings = Depends(get_settings)):
            folder_path = settings.CSV_PATH
            if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
                raise HTTPException(status_code=500, detail="CSV folder not found")

            csv_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
            return {"files": csv_files}

        @self.router.get("/files/video", response_model=VideoFileResponse)
        async def get_video_files(settings: Settings = Depends(get_settings)):
            folder_path = settings.VIDEO_PATH
            if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
                raise HTTPException(status_code=500, detail="Video folder not found")

            video_files = [f for f in os.listdir(folder_path) if f.endswith(".mp4") or f.endswith(".m4v")]
            return {"files": video_files}

        @self.router.get("/all", response_model=AllTestDrivesResponse)
        async def get_all_testdrives(service: TestDriveDataService = Depends(get_testdata_manager)):
            return {"testdrives": service.get_testdrives()}

        @self.router.post("/create", response_model=TestDriveResponse)
        async def create_testdrive(payload: CreateProjectPayload,
                                   service: TestDriveDataService = Depends(get_testdata_manager),
                                   settings: Settings = Depends(get_settings)):

            video_folders = [settings.VIDEO_UPLOAD_DIR.resolve(), Path(settings.VIDEO_PATH)]
            csv_folders = [settings.CSV_UPLOAD_DIR.resolve(), Path(settings.CSV_PATH)]

            # Find existing video path
            video_path = next(
                (folder / payload.video_file_name for folder in video_folders if
                 (folder / payload.video_file_name).exists()),
                None
            )

            # Find existing CSV path
            csv_path = next(
                (folder / payload.csv_file_name for folder in csv_folders if (folder / payload.csv_file_name).exists()),
                None
            )

            # video_path = os.path.join(settings.VIDEO_PATH, payload.video_file_name)
            # csv_path = os.path.join(settings.CSV_PATH, payload.csv_file_name)

            if video_path is None:
                raise HTTPException(status_code=404, detail=f"Video file '{payload.video_file_name}' not found.")

            if csv_path is None:
                raise HTTPException(status_code=404, detail=f"CSV file '{payload.csv_file_name}' not found.")

            # create tag file name: same name as csv file but with _tags suffix and .csv extension
            #  e.g. testdrive.csv -> testdrive_tags.json
            tag_file_name = payload.csv_file_name.replace(".csv", "_tags.csv")
            tag_path = os.path.join(settings.TAG_PATH, tag_file_name)

            testdrive = TestDriveProjectInfo(
                is_live=False,
                test_drive_data_info=TestDriveDataInfo(csv_file_name=payload.csv_file_name,
                                                       csv_file_full_path=os.path.normpath(csv_path)),
                test_drive_video_info=TestDriveVideoInfo(video_file_name=payload.video_file_name,
                                                         video_file_full_path=os.path.normpath(video_path)),
                test_drive_meta_info=TestDriveMetaData(driver_name=payload.driver_name,
                                                       vehicle_name=payload.vehicle_name,
                                                       route_name=payload.route_name,
                                                       notes=payload.notes),
                test_drive_tag_info=TestDriveTagInfo(tag_file_name=tag_file_name,
                                                     tag_file_full_path=tag_path)
            )
            created_testdrive = service.create_testdrive(testdrive)
            return {"testdrive": created_testdrive}

        @self.router.patch("/update", response_model=TestDriveResponse)
        async def update_testdrive(testdrive: TestDriveProjectInfo,
                                   service: TestDriveDataService = Depends(get_testdata_manager)):
            created_testdrive = service.update_testdrive(testdrive)
            return {"testdrive": created_testdrive}

        @self.router.delete("/delete", response_model=TestDriveResponse)
        async def delete_testdrive(testdrive_id: int,
                                   service: TestDriveDataService = Depends(get_testdata_manager)):
            created_testdrive = service.delete_testdrive(testdrive_id)
            return {"testdrive": created_testdrive}

        @self.router.get("/active", response_model=OptionalTestDriveResponse)
        async def get_active_testdrive(service: TestDriveDataService = Depends(get_testdata_manager)):
            active_testdrive = service.get_active_testdrive()
            return {"testdrive": active_testdrive}

        @self.router.post("/activate/{testdrive_id}", response_model=TestDriveResponse)
        async def activate_testdrive(testdrive_id: int,
                                     background_tasks: BackgroundTasks,
                                     service: TestDriveDataService = Depends(get_testdata_manager),
                                     settings: Settings = Depends(get_settings)):
            activated_testdrive = service.activate_testdrive(testdrive_id)
            if activated_testdrive is None:
                raise HTTPException(status_code=404, detail=f"Testdrive with id {testdrive_id} not found")

            if activated_testdrive.is_live:
                service.create_new_live_data(activated_testdrive, settings)

            background_tasks.add_task(service.load_csv_data, activated_testdrive)
            return {"testdrive": activated_testdrive}

        @self.router.post("/deactivate", response_model=TestDriveResponse)
        async def deactivate_testdrive(service: TestDriveDataService = Depends(get_testdata_manager)):
            deactivated_testdrive = service.deactivate_testdrive()
            if deactivated_testdrive is None:
                raise HTTPException(status_code=404, detail="No active testdrive found")
            return {"testdrive": deactivated_testdrive}

        @self.router.post("/upload/csv")
        async def upload_csv_file(csv_file: UploadFile = File(),
                                  settings: Settings = Depends(get_settings)) -> UploadResponse:
            csv_path = settings.CSV_UPLOAD_DIR / csv_file.filename

            with csv_path.open("wb") as f:
                shutil.copyfileobj(csv_file.file, f)

            return {"filename": csv_file.filename}

        @self.router.post("/upload/video")
        async def upload_video_file(video_file: UploadFile = File(),
                                    settings: Settings = Depends(get_settings)) -> UploadResponse:
            csv_path = settings.VIDEO_UPLOAD_DIR / video_file.filename

            with csv_path.open("wb") as f:
                shutil.copyfileobj(video_file.file, f)

            return {"filename": video_file.filename}

import logging
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from app.dependencies import get_testdata_manager, get_settings
from app.models.testDriveDataInfo import TestDriveDataInfo
from app.models.testDriveMetaData import TestDriveMetaData
from app.models.testDriveProjectInfo import TestDriveProjectInfo
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


class SingleTimeTagModel(BaseModel):
    timestamp: float = Field(0.0, title="Timestamp", description="The timestamp of the tag")
    notes: str = Field("", title="Notes", description="Notes for the tag")


class TimeRangeTagModel(BaseModel):
    start_timestamp: float
    end_timestamp: float
    notes: str


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
        async def get_all_testdrives(service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            return {"testdrives": service.get_testdrives()}

        @self.router.post("/create", response_model=TestDriveResponse)
        async def create_testdrive(payload: CreateProjectPayload,
                                   service: TestDriveDataService = Depends(lambda: get_testdata_manager()),
                                   settings: Settings = Depends(get_settings)):

            video_path = os.path.join(settings.VIDEO_PATH, payload.video_file_name)
            csv_path = os.path.join(settings.CSV_PATH, payload.csv_file_name)

            testdrive = TestDriveProjectInfo(
                test_drive_data_info=TestDriveDataInfo(csv_file_name=payload.csv_file_name,
                                                       csv_file_full_path=os.path.normpath(csv_path)),
                test_drive_video_info=TestDriveVideoInfo(video_file_name=payload.video_file_name,
                                                         video_file_full_path=os.path.normpath(video_path)),
                test_drive_meta_info=TestDriveMetaData(driver_name=payload.driver_name,
                                                       vehicle_name=payload.vehicle_name,
                                                       route_name=payload.route_name,
                                                       notes=payload.notes)
            )
            created_testdrive = service.create_testdrive(testdrive)
            return {"testdrive": created_testdrive}

        @self.router.patch("/update", response_model=TestDriveResponse)
        async def update_testdrive(testdrive: TestDriveProjectInfo,
                                   service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            created_testdrive = service.update_testdrive(testdrive)
            return {"testdrive": created_testdrive}

        @self.router.delete("/delete", response_model=TestDriveResponse)
        async def delete_testdrive(testdrive_id: int,
                                   service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            created_testdrive = service.delete_testdrive(testdrive_id)
            return {"testdrive": created_testdrive}

        @self.router.get("/active", response_model=OptionalTestDriveResponse)
        async def get_active_testdrive(service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            active_testdrive = service.get_active_testdrive()
            return {"testdrive": active_testdrive}

        @self.router.post("/activate/{testdrive_id}", response_model=TestDriveResponse)
        async def activate_testdrive(testdrive_id: int,
                                     background_tasks: BackgroundTasks,
                                     service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            activated_testdrive = service.activate_testdrive(testdrive_id)
            if activated_testdrive is None:
                raise HTTPException(status_code=404, detail=f"Testdrive with id {testdrive_id} not found")

            background_tasks.add_task(service.load_csv_data(activated_testdrive.test_drive_data_info))
            return {"testdrive": activated_testdrive}

        @self.router.post("/deactivate", response_model=TestDriveResponse)
        async def deactivate_testdrive(service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            deactivated_testdrive = service.deactivate_testdrive()
            if deactivated_testdrive is None:
                raise HTTPException(status_code=404, detail="No active testdrive found")
            return {"testdrive": deactivated_testdrive}

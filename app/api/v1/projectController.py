import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sympy.abc import lamda

from app.dependencies import get_testdata_manager, get_settings
from app.models.tags import SingleTimeTag, TimeRangeTag
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


class AddTimeTagResponse(BaseModel):
    message: str


class DeleteTimeTagResponse(BaseModel):
    message: str


class ProjectController:
    def __init__(self):
        self.router = APIRouter()
        self.playback = None
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

        @self.router.delete("/{testdrive_id}/tag/{tag_index}", response_model=DeleteTimeTagResponse)
        async def delete_tag(testdrive_id: int, tag_index: int,
                             service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            service.delete_tag(testdrive_id, tag_index)
            return {"message": "Tag deleted"}

        @self.router.get("/active", response_model=TestDriveResponse)
        async def get_active_testdrive(service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            active_testdrive = service.get_active_testdrive()
            if active_testdrive is None:
                raise HTTPException(status_code=404, detail="Active testdrive not found")
            return {"testdrive": active_testdrive}

        @self.router.post("/activate/{testdrive_id}", response_model=TestDriveResponse)
        async def activate_testdrive(testdrive_id: int,
                                     service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            activated_testdrive = service.activate_testdrive(testdrive_id)
            if activated_testdrive is None:
                raise HTTPException(status_code=404, detail=f"Testdrive with id {testdrive_id} not found")
            return {"testdrive": activated_testdrive}

        @self.router.post("/deactivate", response_model=TestDriveResponse)
        async def deactivate_testdrive(service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            deactivated_testdrive = service.deactivate_testdrive()
            if deactivated_testdrive is None:
                raise HTTPException(status_code=404, detail="No active testdrive found")
            return {"testdrive": deactivated_testdrive}

        # @self.router.post("/{testdrive_id}/tag/single", response_model=AddTimeTagResponse) @ self.router.put(
        #     "/{testdrive_id}/tag/single", response_model=AddTimeTagResponse)
        # async def add_single_time_tag(testdrive_id: int, tag: SingleTimeTagModel,
        #                               service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
        #     new_tag = SingleTimeTag(timestamp=tag.timestamp, notes=tag.notes)
        #     service.add_tag(testdrive_id, new_tag)
        #     return {"message": "Single time tag added"}
        #
        # @self.router.put("/{testdrive_id}/tag/range", response_model=AddTimeTagResponse)
        # async def add_time_range_tag(testdrive_id: int, tag: TimeRangeTagModel,
        #                              service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
        #     new_tag = TimeRangeTag(start_timestamp=tag.start_timestamp, end_timestamp=tag.end_timestamp,
        #                            notes=tag.notes)
        #     service.add_tag(testdrive_id, new_tag)
        #     return {"message": "Time range tag added"}

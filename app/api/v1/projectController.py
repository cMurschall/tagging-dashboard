from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.dependencies import get_testdata_manager
from app.models.tags import SingleTimeTag, TimeRangeTag
from app.models.testDriveData import TestDriveData
from app.services.testDriveDataService import TestDriveDataService


class SingleTimeTagModel(BaseModel):
    timestamp: float
    notes: str


class TimeRangeTagModel(BaseModel):
    start_timestamp: float
    end_timestamp: float
    notes: str


class CSVFileResponse(BaseModel):
    files: List[str]


class VideoFileResponse(BaseModel):
    files: List[str]


class AllTestDrivesResponse(BaseModel):
    testdrives: List[TestDriveData]


class TestDriveResponse(BaseModel):
    testdrive: TestDriveData


class AddTimeTagResponse(BaseModel):
    message: str


class DeleteTimeTagResponse(BaseModel):
    message: str


class ProjectController:
    def __init__(self):
        self.router = APIRouter()
        self.playback = None
        self._define_routes()

        self.csv_file_folder = "D:/Praxisprojekt Herms"

    def _define_routes(self):
        @self.router.get("/files/csv", response_model=CSVFileResponse)
        async def get_csv_files(service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            csv_files = service.list_csv_files(self.csv_file_folder)
            return {"files": csv_files}

        @self.router.get("/files/video", response_model=VideoFileResponse)
        async def get_video_files(service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            video_files = service.list_video_files(self.csv_file_folder)
            return {"files": video_files}

        @self.router.get("/all", response_model=AllTestDrivesResponse)
        async def get_all_testdrives(service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            return {"testdrives": service.get_testdrives()}

        @self.router.post("/", response_model=TestDriveResponse)
        async def create_testdrive(testdrive: TestDriveData,
                                   service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            created_testdrive = service.create_testdrive(testdrive)
            return {"testdrive": created_testdrive}

        @self.router.patch("/", response_model=TestDriveResponse)
        async def update_testdrive(testdrive: TestDriveData,
                                   service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            created_testdrive = service.update_testdrive(testdrive)
            return {"testdrive": created_testdrive}

        @self.router.delete("/", response_model=TestDriveResponse)
        async def delete_testdrive(testdrive_id: int,
                                   service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            created_testdrive = service.delete_testdrive(testdrive_id)
            return {"testdrive": created_testdrive}

        # @self.router.post("/live")
        # async def create_testdrive_from_live_data(service: TestDriveDataService = Depends(lambda: data_service)):
        #     testdrive_id = await service.create_testdrive_from_live_data(live_data_stream())
        #     return {"testdrive_id": testdrive_id}

        @self.router.put("/{testdrive_id}/tag/single", response_model=AddTimeTagResponse)
        async def add_single_time_tag(testdrive_id: int, tag: SingleTimeTagModel,
                                      service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            new_tag = SingleTimeTag(timestamp=tag.timestamp, notes=tag.notes)
            service.add_tag(testdrive_id, new_tag)
            return {"message": "Single time tag added"}

        @self.router.put("/{testdrive_id}/tag/range", response_model=AddTimeTagResponse)
        async def add_time_range_tag(testdrive_id: int, tag: TimeRangeTagModel,
                                     service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            new_tag = TimeRangeTag(start_timestamp=tag.start_timestamp, end_timestamp=tag.end_timestamp,
                                   notes=tag.notes)
            service.add_tag(testdrive_id, new_tag)
            return {"message": "Time range tag added"}

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

        @self.router.put("/activate/{testdrive_id}", response_model=TestDriveResponse)
        async def activate_testdrive(testdrive_id: int,
                                     service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            activated_testdrive = service.activate_testdrive(testdrive_id)
            if activated_testdrive is None:
                raise HTTPException(status_code=404, detail=f"Testdrive with id {testdrive_id} not found")
            return {"testdrive": activated_testdrive}

        @self.router.put("/deactivate", response_model=TestDriveResponse)
        async def deactivate_testdrive(service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            deactivated_testdrive = service.deactivate_testdrive()
            if deactivated_testdrive is None:
                raise HTTPException(status_code=404, detail="No active testdrive found")
            return {"testdrive": deactivated_testdrive}

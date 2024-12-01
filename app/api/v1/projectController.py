from fastapi import APIRouter, Depends
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


class ProjectController:
    def __init__(self):
        self.router = APIRouter()
        self.playback = None
        self._define_routes()

        self.csv_file_folder = "D:/Praxisprojekt Herms"

    def _define_routes(self):
        @self.router.get("/{testdrive_id}")
        async def get_testdrive(testdrive_id: int,
                                service: TestDriveDataService = Depends(lambda: get_testdata_manager)):
            return service.get_testdrive(testdrive_id)

        @self.router.post("/")
        async def create_testdrive(testdrive: TestDriveData,
                                   service: TestDriveDataService = Depends(lambda: get_testdata_manager)):
            testdrive_id = service.create_testdrive(testdrive)
            return {"testdrive_id": testdrive_id}

        @self.router.post("/live")
        async def create_testdrive_from_live_data(service: TestDriveDataService = Depends(lambda: data_service)):
            testdrive_id = await service.create_testdrive_from_live_data(live_data_stream())
            return {"testdrive_id": testdrive_id}

        @self.router.put("/{testdrive_id}/tag/single")
        async def add_single_time_tag(testdrive_id: int, tag: SingleTimeTagModel,
                                      service: TestDriveDataService = Depends(lambda: get_testdata_manager)):
            new_tag = SingleTimeTag(timestamp=tag.timestamp, notes=tag.notes)
            service.add_tag(testdrive_id, new_tag)
            return {"message": "Single time tag added"}

        @self.router.put("/{testdrive_id}/tag/range")
        async def add_time_range_tag(testdrive_id: int, tag: TimeRangeTagModel,
                                     service: TestDriveDataService = Depends(lambda: get_testdata_manager)):
            new_tag = TimeRangeTag(start_timestamp=tag.start_timestamp, end_timestamp=tag.end_timestamp,
                                   notes=tag.notes)
            service.add_tag(testdrive_id, new_tag)
            return {"message": "Time range tag added"}

        @self.router.delete("/{testdrive_id}/tag/{tag_index}")
        async def delete_tag(testdrive_id: int, tag_index: int,
                             service: TestDriveDataService = Depends(lambda: get_testdata_manager)):
            service.delete_tag(testdrive_id, tag_index)
            return {"message": "Tag deleted"}

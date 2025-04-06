import logging
from http.client import HTTPException

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.dependencies import get_testdata_manager, get_tagdata_manager
from app.models.tag import Tag
from app.services.testDriveDataService import TestDriveDataService
from app.services.testDriveTagService import TestDriveTagService


class CreateTagPayload(BaseModel):
    timestamp_start_s: float = Field(0.0, title="Start Timestamp", description="The start timestamp of the tag")
    timestamp_end_s: float = Field(0.0, title="End Timestamp", description="The end timestamp of the tag")
    category: str = Field("", title="Category", description="The category of the tag")
    notes: str = Field("", title="Notes", description="Notes for the tag")


class UpdateTagPayload(BaseModel):
    timestamp_start_s: float = Field(0.0, title="Start Timestamp", description="The start timestamp of the tag")
    timestamp_end_s: float = Field(0.0, title="End Timestamp", description="The end timestamp of the tag")
    category: str = Field("", title="Category", description="The category of the tag")
    notes: str = Field("", title="Notes", description="Notes for the tag")


class AllTagListResponse(BaseModel):
    tags: list[Tag]


class TagResponse(BaseModel):
    tag: Tag


class TagController:
    def __init__(self):
        self.router = APIRouter()
        self.logger = logging.getLogger("uvicorn.error")
        self._define_routes()

    def _define_routes(self):
        @self.router.get("/all", response_model=AllTagListResponse)
        async def get_all_tags(
                test_drive_service: TestDriveDataService = Depends(lambda: get_testdata_manager()),
                tag_service: TestDriveTagService = Depends(lambda: get_tagdata_manager())):
            active_testdrive = test_drive_service.get_active_testdrive()
            if not active_testdrive:
                return {"tags": []}

            tags = tag_service.get_all_tags(active_testdrive.test_drive_tag_info)
            return {"tags": tags}

        @self.router.post("/create", response_model=TagResponse)
        async def add_tag(
                payload: CreateTagPayload,
                test_drive_service: TestDriveDataService = Depends(lambda: get_testdata_manager()),
                tag_service: TestDriveTagService = Depends(lambda: get_tagdata_manager())):
            active_testdrive = test_drive_service.get_active_testdrive()
            if not active_testdrive:
                raise HTTPException(status_code=404, detail="No active test drive found")

            tag = Tag(**payload.model_dump())

            created_tag = tag_service.add_tag(active_testdrive.test_drive_tag_info, tag)
            return {"tag": created_tag}

        @self.router.get("/get_by_id/{id}", response_model=TagResponse)
        async def get_tag_by_guid(
                id: int,
                test_drive_service: TestDriveDataService = Depends(lambda: get_testdata_manager()),
                tag_service: TestDriveTagService = Depends(lambda: get_tagdata_manager())):
            active_testdrive = test_drive_service.get_active_testdrive()
            if not active_testdrive:
                raise HTTPException(status_code=404, detail="No active test drive found")

            tag = tag_service.get_by_id(active_testdrive, id)
            return {"tag": tag}

        @self.router.delete("/delete/{id}", response_model=TagResponse)
        async def delete_tag(
                id: int,
                test_drive_service: TestDriveDataService = Depends(lambda: get_testdata_manager()),
                tag_service: TestDriveTagService = Depends(lambda: get_tagdata_manager())):
            active_testdrive = test_drive_service.get_active_testdrive()
            if not active_testdrive:
                raise HTTPException(status_code=404, detail="No active test drive found")

            tag = tag_service.delete_tag(active_testdrive.test_drive_tag_info, id)
            return {"tag": tag}

        @self.router.put("/update/{id}", response_model=TagResponse)
        async def update_tag(
                id: int,
                payload: UpdateTagPayload,
                test_drive_service: TestDriveDataService = Depends(lambda: get_testdata_manager()),
                tag_service: TestDriveTagService = Depends(lambda: get_tagdata_manager())):
            active_testdrive = test_drive_service.get_active_testdrive()
            if not active_testdrive:
                raise HTTPException(status_code=404, detail="No active test drive found")

            tag = Tag(**payload.model_dump())
            updated_tag = tag_service.update_tag(active_testdrive.test_drive_tag_info, id, tag)
            return {"tag": updated_tag}

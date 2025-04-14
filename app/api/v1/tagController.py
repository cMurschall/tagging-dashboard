import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.dependencies import get_testdata_manager, get_tagdata_manager
from app.models.tag import Tag
from app.models.testDriveTagInfo import TagCategory
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


class DeleteResponse(BaseModel):
    success: bool


class AllCategoriesResponse(BaseModel):
    categories: list[TagCategory]


class CreateNewTagCategoryPayload(BaseModel):
    name: str = Field("", title="Category Name", description="The name of the category")


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
                id: str,
                test_drive_service: TestDriveDataService = Depends(lambda: get_testdata_manager()),
                tag_service: TestDriveTagService = Depends(lambda: get_tagdata_manager())):
            active_testdrive = test_drive_service.get_active_testdrive()
            if not active_testdrive:
                raise HTTPException(status_code=404, detail="No active test drive found")

            tag = tag_service.get_by_id(active_testdrive, id)
            return {"tag": tag}

        @self.router.delete("/delete/{id}", response_model=DeleteResponse)
        async def delete_tag(
                id: str,
                test_drive_service: TestDriveDataService = Depends(lambda: get_testdata_manager()),
                tag_service: TestDriveTagService = Depends(lambda: get_tagdata_manager())):
            active_testdrive = test_drive_service.get_active_testdrive()
            if not active_testdrive:
                raise HTTPException(status_code=404, detail="No active test drive found")

            success = tag_service.delete_tag(active_testdrive.test_drive_tag_info, id)
            return {"success": success}

        @self.router.put("/update/{id}", response_model=TagResponse)
        async def update_tag(
                id: str,
                payload: UpdateTagPayload,
                test_drive_service: TestDriveDataService = Depends(lambda: get_testdata_manager()),
                tag_service: TestDriveTagService = Depends(lambda: get_tagdata_manager())):
            active_testdrive = test_drive_service.get_active_testdrive()
            if not active_testdrive:
                raise HTTPException(status_code=404, detail="No active test drive found")

            tag = Tag(**payload.model_dump())
            updated_tag = tag_service.update_tag(active_testdrive.test_drive_tag_info, id, tag)
            return {"tag": updated_tag}

        @self.router.get("/category/all", response_model=AllCategoriesResponse)
        async def get_all_tag_categories(
                test_drive_service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            active_testdrive = test_drive_service.get_active_testdrive()
            if not active_testdrive:
                return {"categories": []}
            return {"categories": active_testdrive.test_drive_tag_info.tag_categories}

        @self.router.post("/category", response_model=AllCategoriesResponse)
        async def add_tag_category(
                payload: CreateNewTagCategoryPayload,
                test_drive_service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            if not payload.name:
                raise HTTPException(status_code=400, detail="Category name is required")

            active_testdrive = test_drive_service.get_active_testdrive()
            if not active_testdrive:
                raise HTTPException(status_code=404, detail="No active test drive found")

            not_reserved_id = 1
            for category in active_testdrive.test_drive_tag_info.tag_categories:
                # check if category already exists
                if category.name == payload.name:
                    raise HTTPException(status_code=400, detail="Category name already exists")
                not_reserved_id += 1

            new_category = TagCategory(id=not_reserved_id, name=payload.name)
            active_testdrive.test_drive_tag_info.tag_categories.append(new_category)

            updated_testdrive = test_drive_service.update_testdrive(active_testdrive)
            return {"categories": updated_testdrive.test_drive_tag_info.tag_categories}

        @self.router.delete("/category/{category_id}", response_model=AllCategoriesResponse)
        async def delete_tag_category(
                category_id: int,
                test_drive_service: TestDriveDataService = Depends(lambda: get_testdata_manager())):
            active_testdrive = test_drive_service.get_active_testdrive()
            if not active_testdrive:
                raise HTTPException(status_code=404, detail="No active test drive found")

            # Find the category by ID
            category_index = next(
                (index for index, cat in enumerate(active_testdrive.test_drive_tag_info.tag_categories) if
                 cat.id == category_id), None)
            if not category_index:
                raise HTTPException(status_code=404, detail=f"Category with ID '{category_id}' not found")
            # Remove the category from the list
            active_testdrive.test_drive_tag_info.tag_categories.pop(category_index)
            updated_testdrive = test_drive_service.update_testdrive(active_testdrive)
            return {"categories": updated_testdrive.test_drive_tag_info.tag_categories}

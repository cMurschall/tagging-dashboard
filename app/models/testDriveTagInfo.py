from typing import List

from pydantic import BaseModel, Field


class TagCategory(BaseModel):
    id: int = Field(-1, title="Tag category ID", description="The unique identifier of the tag category")
    name: str = Field("", title="Tag category", description="The name of the tag category")


class TestDriveTagInfo(BaseModel):
    tag_file_name: str = Field("", title="Tag file name", description="The name of the tag file")
    tag_file_full_path: str = Field("", title="Tag file full path", description="The full path of the tag file")
    tag_categories: List[TagCategory] = Field(default_factory=list, title="Tag categories",
                                              description="List of tag categories")

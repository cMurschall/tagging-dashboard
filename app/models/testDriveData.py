from dataclasses import dataclass, field
from typing import List

from pydantic import BaseModel, Field

from app.models.tags import Tag
from app.models.testDriveMetaData import TestDriveMetaData


class TestDriveData(BaseModel):
    id: int
    raw_data_path: str = ""  # Path to the csv log file
    video_path: str = ""  # Path to the video file
    video_sprite_path: str = ""  # Path to the video
    tags: List[Tag] = Field(default_factory=[])  # Replace `Tag` with `str` or a specific type
    meta_data: TestDriveMetaData = Field(default_factory=TestDriveMetaData)

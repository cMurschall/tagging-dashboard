from dataclasses import dataclass, field
from typing import List

from pydantic import BaseModel, Field

from app.models.tags import Tag
from app.models.testDriveMetaData import TestDriveMetaData


# @dataclass
# class TestDriveData:
#     id: int
#     raw_data_path: str = ""  # Path to the csv log file
#     video_path: str = ""  # Path to the video file
#     tags: List[Tag] = field(default_factory=list)
#     meta_data: TestDriveMetaData = field(default_factory=TestDriveMetaData)


class TestDriveData(BaseModel):
    id: int
    raw_data_path: str = ""  # Path to the csv log file
    video_path: str = ""  # Path to the video file
    tags: List[Tag] = Field(default_factory=[])  # Replace `Tag` with `str` or a specific type
    meta_data: TestDriveMetaData = Field(default_factory=TestDriveMetaData)

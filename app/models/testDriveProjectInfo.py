from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from ..models.testDriveDataInfo import TestDriveDataInfo
from ..models.testDriveVideoInfo import TestDriveVideoInfo
from ..models.tags import Tag
from ..models.testDriveMetaData import TestDriveMetaData


class TestDriveProjectInfo(BaseModel):
    id: int = Field(-1, title="Test Drive ID", description="The unique identifier of the test drive")
    creation_date: Optional[datetime] = Field(default_factory=datetime.now, title="Creation date",
                                              description="The date and time the test drive project was created")

    test_drive_data_info: TestDriveDataInfo = Field(default_factory=TestDriveDataInfo)
    test_drive_video_info: TestDriveVideoInfo = Field(default_factory=TestDriveVideoInfo)
    tags: List[Tag] = Field(default_factory=list)  # Correct way to handle mutable defaults
    test_drive_meta_info: TestDriveMetaData = Field(default_factory=TestDriveMetaData)

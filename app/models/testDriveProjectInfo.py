from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .testDriveTagInfo import TestDriveTagInfo
from ..models.testDriveDataInfo import TestDriveDataInfo
from ..models.testDriveVideoInfo import TestDriveVideoInfo
from ..models.testDriveMetaData import TestDriveMetaData


class TestDriveProjectInfo(BaseModel):
    id: int = Field(-1, title="Test Drive ID", description="The unique identifier of the test drive")

    creation_date: Optional[datetime] = Field(default_factory=datetime.now, title="Creation date",
                                              description="The date and time the test drive project was created")

    test_drive_data_info: TestDriveDataInfo = Field(default_factory=TestDriveDataInfo, title="Test Drive Data Info",
                                                    description="Information about the test drive data")

    test_drive_video_info: TestDriveVideoInfo = Field(default_factory=TestDriveVideoInfo, title="Test Drive Video Info",
                                                      description="Information about the test drive video")

    test_drive_meta_info: TestDriveMetaData = Field(default_factory=TestDriveMetaData, title="Test Drive Meta Info",
                                                    description="Information about the test drive metadata")

    test_drive_tag_info: TestDriveTagInfo = Field(default_factory=TestDriveTagInfo, title="Test Drive Tag Info",
                                                  description="Information about the test drive tags")

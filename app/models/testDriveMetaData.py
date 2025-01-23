from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


#
# @dataclass
# class TestDriveMetaData:
#     driver_name: str
#     vehicle_id: str
#     route_name: str
#     notes: str = ""
#     test_date: Optional[datetime] = datetime.now()

class TestDriveMetaData(BaseModel):
    driver_name: str
    vehicle_id: str
    route_name: str
    notes: Optional[str] = ""
    test_date: Optional[datetime] = Field(default_factory=datetime.now)  # Default to current time

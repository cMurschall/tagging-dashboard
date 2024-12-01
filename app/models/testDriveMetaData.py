from dataclasses import dataclass
from datetime import datetime


@dataclass
class TestDriveMetaData:
    driver_name: str
    vehicle_id: str
    test_date: datetime
    route_name: str
    notes: str = ""


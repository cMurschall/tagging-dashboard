from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TestDriveMetaData(BaseModel):
    driver_name: str = Field("", title="Driver name", description="The name of the driver")
    vehicle_name: str = Field("", title="Vehicle ID", description="The name or type of the vehicle")
    route_name: str = Field("", title="Route name", description="The name of the route")

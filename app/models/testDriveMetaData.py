from pydantic import BaseModel, Field


class TestDriveMetaData(BaseModel):
    driver_name: str = Field("", title="Driver name", description="The name of the driver")
    vehicle_name: str = Field("", title="Vehicle ID", description="The name or type of the vehicle")
    route_name: str = Field("", title="Route name", description="The name of the route")
    notes: str = Field("", title="Notes", description="Notes for the test drive project")

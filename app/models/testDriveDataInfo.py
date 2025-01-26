from pydantic import BaseModel, Field


class TestDriveDataInfo(BaseModel):
    csv_file_name: str = Field("", title="CSV path", description="The name of the CSV file")
    csv_file_full_path: str = Field("", title="CSV full path", description="The full path of the CSV file")
    driven_distance_m: float = Field(0.0, title="Driven distance",
                                     description="The distance driven in meters")
    driven_time_s: float = Field(0.0, title="Driven time",
                                 description="The time driven in seconds")
    average_speed_m_s: float = Field(0.0, title="Average speed",
                                     description="The average speed in meters per second")
    max_speed_m_s: float = Field(0.0, title="Max speed", description="The maximum speed in meters per second")

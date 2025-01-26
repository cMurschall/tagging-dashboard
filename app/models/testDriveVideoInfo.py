from pydantic import BaseModel, Field
from app.models.videoSpriteInfo import VideoSpriteInfo


class TestDriveVideoInfo(BaseModel):
    video_file_name: str = Field("", title="Video file name", description="The name of the video file")
    video_file_full_path: str = Field("", title="Video file full path", description="The full path of the video file")
    # video_sprite_info: Field(default_factory=VideoSpriteInfo)
    simulation_start_time_s: float = Field(0.0, title="Simulation start time",
                                           description="Start time of the simulation in seconds")
    simulation_stop_time_s: float = Field(0.0, title="Simulation stop time",
                                          description="Stop time of the simulation in seconds")

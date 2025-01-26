from pydantic import BaseModel, Field
from app.models.videoThumbnailsInfo import VideoThumbnailsInfo


class TestDriveVideoInfo(BaseModel):
    video_file_name: str = Field("", title="Video file name", description="The name of the video file")
    video_file_full_path: str = Field("", title="Video file full path", description="The full path of the video file")
    video_sprite_info: VideoThumbnailsInfo = Field(default_factory=VideoThumbnailsInfo, title="Video sprite info",
                                                   description="The video sprite info")

    video_duration_s: float = Field(0.0, title="Video duration", description="The duration of the video in seconds")
    video_width: int = Field(0, title="Video width", description="The width of the video in pixels")
    video_height: int = Field(0, title="Video height", description="The height of the video in pixels")

    video_frame_rate: float = Field(0.0, title="Video frame rate", description="The frame rate of the video")

    video_simulation_time_start_s: float = Field(0.0, title="Video simulation start time",
                                                 description="The start time of the video simulation in seconds")
    video_simulation_time_end_s: float = Field(0.0, title="Video simulation end time",
                                               description="The end time of the video simulation in seconds")

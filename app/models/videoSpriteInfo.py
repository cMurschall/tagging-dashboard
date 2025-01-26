from pydantic import BaseModel, Field


class VideoSpriteInfo(BaseModel):
    video_path: str = Field("", title="Video path", description="The path of the video")
    output_path: str = Field("", title="Output path", description="The path of the output sprite")
    interval: int = Field(4, title="Interval", description="The interval between frames")
    thumbnail_width: int = Field(120, title="Thumbnail width", description="The width of each thumbnail")
    thumbnail_height: int = Field(90, title="Thumbnail height", description="The height of each thumbnail")

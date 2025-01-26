from pydantic import BaseModel, Field


class VideoThumbnailsInfo(BaseModel):
    sprite_file_name: str = Field("", title="Thumbnails file name", description="The name of the thumbnails file")
    sprite_file_full_path: str = Field("", title="Thumbnails file full path",
                                       description="The full path of the thumbnails file")
    sprite_interval: int = Field(0, title="Interval", description="The interval between frames")
    thumbnail_width: int = Field(0, title="Thumbnail width", description="The width of each thumbnail")
    thumbnail_height: int = Field(0, title="Thumbnail height", description="The height of each thumbnail")

    sprite_rows: int = Field(0, title="Rows", description="The number of rows in the grid")
    sprite_columns: int = Field(0, title="Columns", description="The number of columns in the grid")

    sprites_total: int = Field(0, title="Total thumbnails", description="The total number of thumbnails")

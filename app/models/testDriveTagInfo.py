from pydantic import BaseModel, Field


class TestDriveTagInfo(BaseModel):
    tag_file_name: str = Field("", title="Tag file name", description="The name of the tag file")
    tag_file_full_path: str = Field("", title="Tag file full path", description="The full path of the tag file")

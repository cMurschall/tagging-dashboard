from pydantic import BaseModel, Field


class Tag(BaseModel):
    id: str = Field("", title="Id", description="The unique identifier of the tag")

    timestamp_start_s: float = Field(0.0, title="Start Timestamp", description="The start timestamp of the tag")
    timestamp_end_s: float = Field(0.0, title="End Timestamp", description="The end timestamp of the tag")

    category: str = Field("", title="Category", description="The category of the tag")
    notes: str = Field("", title="Notes", description="Notes for the tag")

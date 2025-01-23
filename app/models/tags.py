from dataclasses import dataclass
from enum import Enum, auto


class TagType(Enum):
    SINGLE_TIME = "single_time"
    TIME_RANGE = "time_range"


@dataclass
class Tag:
    id: int
    notes: str
    category: TagType


@dataclass
class SingleTimeTag(Tag):
    timestamp: float = 0  # Time in seconds from the start of the test drive
    category: TagType = TagType.SINGLE_TIME


@dataclass
class TimeRangeTag(Tag):
    start_timestamp: float = 0  # Start time in seconds from the start of the test drive
    end_timestamp: float = 0  # End time in seconds from the start of the test drive
    category: TagType = TagType.TIME_RANGE

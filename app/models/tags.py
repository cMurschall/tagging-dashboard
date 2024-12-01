from dataclasses import dataclass
from enum import Enum, auto


class TagType(Enum):
    SINGLE_TIME = auto()
    TIME_RANGE = auto()


@dataclass
class Tag:
    id: int
    notes: str
    category: TagType


@dataclass
class SingleTimeTag(Tag):
    timestamp: float  # Time in seconds from the start of the test drive
    category: TagType = TagType.SINGLE_TIME


@dataclass
class TimeRangeTag(Tag):
    start_timestamp: float  # Start time in seconds from the start of the test drive
    end_timestamp: float  # End time in seconds from the start of the test drive
    category: TagType = TagType.TIME_RANGE

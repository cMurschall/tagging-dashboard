from abc import ABC, abstractmethod
from typing import Optional

from ...models.loggingRow import LoggingRow


class DataSource(ABC):
    """ Abstract base class for data sources. """

    @abstractmethod
    def load_data(self):
        """Load data into the source."""
        pass

    @abstractmethod
    async def get_next_data(self) -> Optional[LoggingRow]:
        """Asynchronously fetch the next piece of data based on the timestamp."""
        pass

    @abstractmethod
    async def jump_to_timestamp(self, timestamp: float):
        """Jump to the specified timestamp in the data."""
        pass

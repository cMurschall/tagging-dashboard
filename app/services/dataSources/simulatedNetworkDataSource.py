import asyncio
from random import random
from typing import Optional

from ...models.loggingRow import LoggingRow, create_random_instance
from ...services.dataSources.dataSource import DataSource


# Network Stream Data Source Implementation
class SimulatedNetworkStreamDataSource(DataSource):
    def __init__(self):
        self.data_queue: asyncio.Queue[LoggingRow] = asyncio.Queue()

    async def simulate_stream(self):
        """Simulates data arrival in a network stream."""
        while True:
            await asyncio.sleep(random.uniform(0.5, 2.0))  # Simulate random delays
            new_data = create_random_instance(LoggingRow)
            await self.data_queue.put(new_data)

    async def load_data(self):
        """Start the stream simulation."""
        asyncio.create_task(self.simulate_stream())

    async def get_next_data(self) -> Optional[LoggingRow]:
        return await self.data_queue.get()

    async def jump_to_timestamp(self, timestamp: float):
        """Jump to the closest timestamp."""

        # This is a network stream, so we can't jump to a specific timestamp.
        pass

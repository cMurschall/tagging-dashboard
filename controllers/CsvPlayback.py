import asyncio
from typing import List, Generator



from models.measurementModel import MeasurementModel

class CSVPlayback:
    def __init__(self, data_source: Generator[List[MeasurementModel], None, None]):
        self.data_source = data_source
        self.csv_data = []
        self.current_index = 0
        self.is_playing = False
        self.playback_task = None
        self.end_of_data = False

    def _load_next_chunk(self):
        """Load the next chunk of data if available."""
        try:
            self.csv_data.extend(next(self.data_source))
        except StopIteration:
            self.end_of_data = True

    async def play(self, send_func):
        """Play the recording, sending data through the provided function."""
        self.is_playing = True
        while self.is_playing:
            if self.current_index >= len(self.csv_data):
                if self.end_of_data:
                    break
                self._load_next_chunk()

            if self.current_index < len(self.csv_data):
                current_row = self.csv_data[self.current_index]
                await send_func(current_row.dict())

                next_timestamp = (
                    self.csv_data[self.current_index + 1].timestamp
                    if self.current_index + 1 < len(self.csv_data)
                    else None
                )
                if next_timestamp:
                    sleep_time = max(0, next_timestamp - current_row.timestamp)
                    await asyncio.sleep(sleep_time)

                self.current_index += 1

    def pause(self):
        self.is_playing = False

    def jump_to_timestamp(self, timestamp: float):
        """Jump to the nearest timestamp."""
        while not self.end_of_data:
            self._load_next_chunk()
            index = next(
                (i for i, row in enumerate(self.csv_data) if row.timestamp >= timestamp),
                None,
            )
            if index is not None:
                self.current_index = index
                return
        # If no suitable row is found, go to the last available data
        self.current_index = len(self.csv_data) - 1
# CSV Data Source Implementation
import asyncio
import csv
from typing import List, Optional, AsyncIterator

from ...models.measurementModel import MeasurementModel
from ...services.dataSources.dataSource import DataSource


class CSVDataSource(DataSource):

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data: List[MeasurementModel] = []
        self.iterator: Optional[AsyncIterator[MeasurementModel]] = None
        self.previous_timestamp = 0.0

    async def load_data(self):
        try:
            # Open the CSV file for reading (https://docs.pydantic.dev/latest/examples/files/#json-lines-files)
            with open(self.file_path, 'r') as file:
                csv_reader = csv.DictReader(file)

                # Skip the first row explicitly (contains zero values)
                next(csv_reader, None)

                parsed_data =[]
                # Parse the CSV file
                for row in csv_reader:
                    try:
                        model = MeasurementModel.model_validate(row)
                        parsed_data.append(model)
                    except ValueError as e:
                        print(f"Error: Failed to parse the CSV file '{self.file_path}'. {e}")


                # Store the sorted data and initialize the iterator
                self.data = parsed_data
                self.iterator = iter(self.data)
                self.previous_timestamp = 0.0

        except FileNotFoundError:
            print(f"Error: The file '{self.file_path}' does not exist.")
            raise
        except ValueError as e:
            print(f"Error: Failed to parse the CSV file '{self.file_path}'. {e}")
            raise

    async def get_next_data(self) -> Optional[MeasurementModel]:
        try:
            data = next(self.iterator)
            delay = max(0, data.timestamp - self.previous_timestamp)
            await asyncio.sleep(delay)
            self.previous_timestamp = data.timestamp
            return data
        except StopIteration:
            return None

    async def jump_to_timestamp(self, timestamp: float):
        """Jump to the closest timestamp."""
        closest_index = next((i for i, d in enumerate(self.data) if d.timestamp >= timestamp), len(self.data) - 1)
        self.iterator = iter(self.data[closest_index:])
        self.previous_timestamp = timestamp
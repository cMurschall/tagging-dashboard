import csv
from typing import List, Generator

from pydantic import parse_obj_as

from models.measurementModel import MeasurementModel


class CSVLoader:
    def __init__(self, file_path: str, chunk_size: int = 1000):
        self.file_path = file_path
        self.chunk_size = chunk_size

    def load_all(self) -> List[MeasurementModel]:
        """Load the entire CSV file into memory."""
        with open(self.file_path, mode="r") as file:
            reader = csv.DictReader(file)
            return parse_obj_as(List[MeasurementModel], reader)

    def load_in_chunks(self) -> Generator[List[MeasurementModel], None, None]:
        """Load the CSV file in chunks."""
        with open(self.file_path, mode="r") as file:
            reader = csv.DictReader(file)
            buffer = []
            for row in reader:
                buffer.append(row)
                if len(buffer) >= self.chunk_size:
                    yield parse_obj_as(List[MeasurementModel], buffer)
                    buffer = []
            if buffer:
                yield parse_obj_as(List[MeasurementModel], buffer)
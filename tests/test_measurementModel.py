import csv
from typing import List

import pytest

from app.models.loggingRow import LoggingRow


def test_convert_single_from_csv():
    # Open the CSV file for reading (https://docs.pydantic.dev/latest/examples/files/#json-lines-files)
    with open("test_recording.csv", 'r') as file:
        csv_reader = csv.DictReader(file)

        # Skip the first row explicitly
        next(csv_reader, None)

        row = next(csv_reader)
        measurement = LoggingRow.from_dict(row)
        assert measurement is not None, "Measurement is None"
        assert isinstance(measurement, LoggingRow), "Measurement is not of type LoggingRow"

        assert measurement.brakes == 0, "Breaks is not 0"
        assert measurement.brakes_vol == 1, "Breaks_vol is not 1"


def test_create_random_instance():
    # Create a random instance of LoggingRow
    instance = LoggingRow.create_random_instance()

    # Verify that the instance is of type LoggingRow
    assert isinstance(instance, LoggingRow), "Instance is not of type LoggingRow"

    # Verify that all fields in the instance have valid types
    for field_name, field_type in LoggingRow.__annotations__.items():
        field_value = getattr(instance, field_name)

        if field_type is int:
            assert isinstance(field_value, int), f"Field {field_name} is not an int"
        elif field_type is float:
            assert isinstance(field_value, float), f"Field {field_name} is not a float"
        elif field_type is List[float]:
            assert isinstance(field_value, list), f"Field {field_name} is not a list"
            assert all(isinstance(item, float) for item in field_value), f"Field {field_name} contains non-float items"
        else:
            pytest.fail(f"Unsupported field type {field_type} for field {field_name}")

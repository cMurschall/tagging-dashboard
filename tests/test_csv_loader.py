from unittest.mock import mock_open, patch

import pytest

from controllers.CsvLoader import CSVLoader
from models.measurementModel import MeasurementModel


@pytest.fixture
def mock_csv_content():
    return """timestamp,throttle,brakes
1.0,0.5,1
2.0,0.7,0
3.0,0.6,1
"""


@patch("builtins.open", new_callable=mock_open, read_data="")
def test_load_all(mock_file, mock_csv_content):
    """Test loading the entire CSV."""
    mock_file.return_value.read.return_value = mock_csv_content
    loader = CSVLoader("test.csv")
    result = loader.load_all()

    # Validate results
    assert len(result) == 3
    assert isinstance(result[0], MeasurementModel)
    assert result[0].timestamp == 1.0


@patch("builtins.open", new_callable=mock_open, read_data="")
def test_load_in_chunks(mock_file, mock_csv_content):
    """Test loading the CSV in chunks."""
    mock_file.return_value.read.return_value = mock_csv_content
    loader = CSVLoader("test.csv", chunk_size=2)
    chunks = list(loader.load_in_chunks())

    # Validate chunks
    assert len(chunks) == 2  # Two chunks: [row1, row2], [row3]
    assert len(chunks[0]) == 2
    assert len(chunks[1]) == 1
    assert isinstance(chunks[0][0], MeasurementModel)
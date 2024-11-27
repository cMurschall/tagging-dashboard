from unittest.mock import patch

import pytest

from app.services.dataSources.csvDataSource import CSVDataSource


@pytest.mark.asyncio
async def test_load_data():
    datasource = CSVDataSource("test_recording.csv")
    await datasource.load_data()

    assert datasource.previous_timestamp == 0.0
    assert datasource.iterator is not None


@pytest.mark.asyncio
async def test_get_next_data():
    datasource = CSVDataSource("test_recording.csv")
    await datasource.load_data()

    assert len(datasource.data) == 99  # 99 rows in the test_recording.csv file

    # assert timestamp is sorted
    for i in range(1, len(datasource.data)):
        assert datasource.data[i].timestamp >= datasource.data[i - 1].timestamp

    with patch("asyncio.sleep", return_value=None) as mock_sleep:
        # First call to get_next_data
        data = await datasource.get_next_data()
        assert data is not None
        mock_sleep.assert_called_once_with(0)  # No delay on the first call

        # Second call
        data = await datasource.get_next_data()
        assert data is not None
        mock_sleep.assert_called_with(1.8277)  # Delay based on the timestamp difference

        # Third call
        data = await datasource.get_next_data()
        assert data is not None
        mock_sleep.assert_called_with(0.011949999999999905)  # Delay based on the timestamp difference


@pytest.mark.asyncio
async def test_jump_to_timestamp():
    datasource = CSVDataSource("test_recording.csv")
    await datasource.load_data()

    await datasource.jump_to_timestamp(2.5)
    data = await datasource.get_next_data()

    # Should skip to the second index, as timestamp 2.5 is closest to 2.50409
    assert datasource.previous_timestamp == 2.50409

import unittest
from unittest.mock import AsyncMock

from controllers.CsvPlayback import CSVPlayback
from models.measurementModel import MeasurementModel



class TestCSVPlayback(unittest.TestCase):
    def setUp(self):
        self.mock_data = [
            MeasurementModel(timestamp=1.0, throttle=0.5, brakes=1),
            MeasurementModel(timestamp=2.0, throttle=0.7, brakes=0),
            MeasurementModel(timestamp=3.0, throttle=0.6, brakes=1),
        ]
        self.mock_data_source = (chunk for chunk in [self.mock_data])  # Simulate a generator

    def test_jump_to_timestamp(self):
        playback = CSVPlayback(self.mock_data_source)
        playback.csv_data = self.mock_data  # Mock loaded data
        playback.jump_to_timestamp(2.5)
        self.assertEqual(playback.current_index, 2)  # Should jump to the nearest index

    async def test_play(self):
        playback = CSVPlayback(self.mock_data_source)
        playback.csv_data = self.mock_data  # Mock loaded data
        send_func = AsyncMock()

        await playback.play(send_func)
        self.assertEqual(send_func.call_count, 3)  # Three rows sent
        send_func.assert_any_call(self.mock_data[0].dict())
        send_func.assert_any_call(self.mock_data[1].dict())
        send_func.assert_any_call(self.mock_data[2].dict())

    def test_pause(self):
        playback = CSVPlayback(self.mock_data_source)
        playback.pause()
        self.assertFalse(playback.is_playing)


if __name__ == "__main__":
    unittest.main()

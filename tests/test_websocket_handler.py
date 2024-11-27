from unittest.mock import AsyncMock, MagicMock

import pytest

from api.websocket.webSocketConnectionHandler import WebSocketConnectionHandler
from controllers.CsvPlayback import CSVPlayback
from models.measurementModel import MeasurementModel, create_random_instance



@pytest.fixture
def setup_handler():
    mock_data = [
        MeasurementModel(timestamp=1.0, throttle=0.5, brakes=1),
        MeasurementModel(timestamp=2.0, throttle=0.7, brakes=0),
    ]
    mock_data_source = (chunk for chunk in [mock_data])
    playback = CSVPlayback(mock_data_source)
    handler = WebSocketConnectionHandler(playback)
    return handler


@pytest.mark.asyncio
async def test_handle_play(setup_handler):
    handler = setup_handler
    websocket = AsyncMock()
    websocket.receive_text = AsyncMock(return_value="play")
    websocket.send_json = AsyncMock()

    handler.playback.csv_data = list(handler.playback.data_source)  # Mock loaded data
    await handler.handle(websocket)
    websocket.send_json.assert_called()  # Ensure data was sent


@pytest.mark.asyncio
async def test_handle_pause(setup_handler):
    handler = setup_handler
    websocket = AsyncMock()
    websocket.receive_text = AsyncMock(side_effect=["pause", "play", "pause"])
    websocket.send_json = AsyncMock()

    await handler.handle(websocket)
    assert not handler.playback.is_playing  # Should pause playback
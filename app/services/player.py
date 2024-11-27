# Player class
import asyncio

from .dataSources.emptyDataSource import EmptyDataSource
from .websocketConnectionManager import ConnectionManager
from ..services.dataSources.dataSource import DataSource


class Player:
    def __init__(self, websocket_manager: ConnectionManager):
        self.websocket_manager = websocket_manager
        self._is_playing = False
        self._data_source = EmptyDataSource()
        self._lock = asyncio.Lock()  # Protects shared state
        self._stop_event = asyncio.Event()  # Signals playback to stop

    async def set_data_source(self, data_source: DataSource):
        # Stop playback gracefully
        async with self._lock:
            if self._is_playing:
                self._stop_event.set()  # Signal to stop playback

        await self._wait_for_playback_to_stop()

        async with self._lock:
            # Assign the new data source after playback stops
            self._data_source = data_source
            self._stop_event.clear()  # Reset the stop event for future use

    async def play(self):
        async with self._lock:
            if self._is_playing:
                return  # Playback is already running
            self._is_playing = True
            current_data_source = self._data_source

        try:
            await current_data_source.load_data()

            while not self._stop_event.is_set():
                data = await current_data_source.get_next_data()
                if data is None:
                    break  # End of data
                await self.websocket_manager.broadcast_text(data.json())
        finally:
            async with self._lock:
                self._is_playing = False
                self._stop_event.clear()  # Ensure the stop event is reset

    async def pause(self):
        async with self._lock:
            self._stop_event.set()

    async def jump_to_timestamp(self, timestamp: float):
        async with self._lock:
            current_data_source = self._data_source
        await current_data_source.jump_to_timestamp(timestamp)

    async def _wait_for_playback_to_stop(self):
        """Waits for the playback loop to finish if it is running."""
        while True:
            async with self._lock:
                if not self._is_playing:
                    break
            await asyncio.sleep(0.01)  # Avoid busy waiting

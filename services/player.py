# Player class
from services.dataSources.dataSource import DataSource


class Player:
    def __init__(self, data_source: DataSource):
        self.data_source = data_source
        self.is_playing = False

    async def play(self, websocket):
        self.is_playing = True
        await self.data_source.load_data()

        while self.is_playing:
            data = await self.data_source.get_next_data()
            if data is None:
                break  # End of data
            await websocket.send_text(data.json())

    def pause(self):
        self.is_playing = False

    async def jump_to_timestamp(self, timestamp: float):
        await self.data_source.jump_to_timestamp(timestamp)

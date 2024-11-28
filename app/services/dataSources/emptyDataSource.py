from typing import Optional

from app.models.loggingRow import LoggingRow
from app.services.dataSources.dataSource import DataSource


class EmptyDataSource(DataSource):

    async def load_data(self):
        pass

    async def get_next_data(self) -> Optional[LoggingRow]:
        return None

    async def jump_to_timestamp(self, timestamp: float):
        pass

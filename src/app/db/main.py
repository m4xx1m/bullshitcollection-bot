from contextlib import asynccontextmanager
 
from app.config import DatabaseConfig
from . import utils
from .dao import DAO


class Database:
    def __init__(self, config: DatabaseConfig):
        self._config = config
        self._engine = utils.create_engine(config)
        self._sessionmaker = utils.create_sessionmaker(self._engine)
        
    @asynccontextmanager
    async def dao(self):
        async with self._sessionmaker() as session:
            async with DAO(session) as dao:
                yield dao

    async def close(self):
        await self._engine.dispose()

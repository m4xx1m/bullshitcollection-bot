import cachetools

from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._cache = cachetools.TTLCache(maxsize=256, ttl=60)

    async def commit(self):
        await self._session.commit()

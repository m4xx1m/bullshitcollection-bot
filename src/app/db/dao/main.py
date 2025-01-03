import logging

from sqlalchemy.ext.asyncio import AsyncSession

from .users import UsersDAO
from .saves import SavesDAO


logger = logging.getLogger("app")


class DAO:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._users = UsersDAO(self._session)
        self._saves = SavesDAO(self._session)
        
    @property
    def users(self) -> UsersDAO:
        return self._users
    
    @property
    def saves(self) -> SavesDAO:
        return self._saves

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self._session.commit()
        except Exception as err:
            logger.error("failed commit db", exc_info=err) 

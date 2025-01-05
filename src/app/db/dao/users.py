from sqlalchemy import exists, select, delete
from sqlalchemy.dialects.postgresql import Insert

from app.db import dto, models
from .base import BaseDAO


class UsersDAO(BaseDAO):
    async def get(self, user_id: int) -> dto.User | None:
        if user := self._cache.get(user_id):
            return user 
        
        if instance := await self._get(user_id):
            user = instance.to_dto()
            self._cache[user_id] = user
            return user 

    async def get_all(self) -> list[dto.User]:
        return [user.to_dto() for user in await self._get_all()]

    async def get_moders(self) -> list[dto.User]:
        query = select(models.User).where(models.User.is_moder == True)
        results = (await self._session.execute(query)).unique().scalars().fetchall()
        return [row.to_dto() for row in results]

    async def upsert(self, user: dto.User) -> dto.User:
        query = Insert(models.User)\
            .values(
                user_id=user.user_id, 
                first_name=user.first_name, 
                last_name=user.last_name, 
                username=user.username, 
                is_moder=user.is_moder,
            )\
            .on_conflict_do_update(
                index_elements=["user_id"],
                set_={
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "is_moder": user.is_moder,
                }
            )\
            .returning(models.User)
        
        instance = await self._session.scalar(query)
        user = instance.to_dto()
        self._cache[user.user_id] = user
        return user
    
    async def delete(self, user_id: int) -> int:
        """returning count of deleted rows"""
        query = delete(models.User).where(models.User.user_id == user_id)
        return (await self._session.execute(query)).rowcount

    async def exists(self, user_id: int) -> bool:
        query = select(exists().where(models.User.user_id == user_id))
        return await self._session.scalar(query)

    async def _get(self, user_id: int) -> models.User | None:
        return await self._session.get(models.User, user_id)

    async def _get_all(self) -> list[models.User]:
        return (await self._session.scalars(select(models.User))).unique().fetchall()  # type: ignore

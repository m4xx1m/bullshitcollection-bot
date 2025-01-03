from sqlalchemy import exists, select, bindparam, func, delete, desc, insert 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import Insert 

from .base import BaseDAO
from app.db import dto, models


class SavesDAO(BaseDAO):
    async def get(self, file_id: str) -> dto.Save | None:
        if save := self._cache.get(file_id):
            return save 

        instance = await self._get(file_id)
        if instance:
            save = instance.to_dto()
            self._cache[file_id] = save
            return save 
    
    async def search(
        self, 
        query_string: str, 
        reverse: bool = False,
        limit: int | None = None
    ) -> list[dto.Save]:
        query = select(models.Save).where(models.Save.caption.ilike(f"%{query_string}%"))
        if limit is not None:
            query = query.limit(limit)
        if reverse:
            query = query.order_by(desc(models.Save.id))
        results = (await self._session.scalars(query)).fetchall()
        return [result.to_dto() for result in results]

    async def get_all(
        self, 
        limit: int | None = None,
        reverse: bool = False,
    ) -> list[dto.Save]:
        return [save.to_dto() for save in await self._get_all(limit, reverse)]

    async def upsert(self, save: dto.Save) -> dto.Save:
        query = Insert(models.Save)\
            .values(
                file_id=save.file_id, 
                caption=save.caption, 
                media_type=save.media_type
            )\
            .on_conflict_do_update(
                index_elements=["file_id"],
                set_={
                    "caption": save.caption,
                    "media_type": save.media_type
                }
            )\
            .returning(models.Save)

        instance = await self._session.scalar(query)
        save = instance.to_dto()
        self._cache[save.file_id] = save
        return save
    
    async def delete(self, file_id: str):
        """returning count of deleted rows"""
        query = delete(models.Save).where(models.Save.file_id == file_id)
        return (await self._session.execute(query)).rowcount

    async def _get(self, file_id: str) -> models.Save | None:
        return await self._session.get(models.Save, file_id)

    async def _get_all(
        self, 
        limit: int | None = None,
        reverse: bool = False,
    ) -> list[models.Save]:
        query = select(models.Save)
        if limit is not None:
            query = query.limit(limit)
        if reverse:
            query = query.order_by(models.Save.id.desc())
        return (await self._session.scalars(query)).unique().fetchall()  # type: ignore

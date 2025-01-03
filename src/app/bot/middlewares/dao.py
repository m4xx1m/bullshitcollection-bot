from typing import Callable, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.db import Database 


class DAOMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        database: Database = data["database"]

        async with database.dao() as dao:
            data["dao"] = dao
            result = await handler(event, data)

        return result

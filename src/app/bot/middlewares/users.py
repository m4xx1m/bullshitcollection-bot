import logging 
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message, CallbackQuery, InlineQuery, ErrorEvent

from app.db import DAO, dto
from app.bot.utils import set_commands


logger = logging.getLogger("app.moddlewares")


class UsersMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery | InlineQuery,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, ErrorEvent):
            if update := (
                event.update.message
                or event.update.callback_query
                or event.update.inline_query
                or event.update.my_chat_member
            ):
                from_user = update.from_user
            else:
                data["user"] = None
                return await handler(event, data)
        else:
            from_user = event.from_user
         
        bot: Bot = data["bot"]
        dao: DAO = data["dao"]
        superusers: list[int] = data["superusers"]
        user = await dao.users.get(from_user.id)

        if (
            user and any([
                user.first_name != from_user.first_name,
                user.last_name != from_user.last_name,
                user.username != from_user.username
            ])
        ) or (
            user is None and from_user.id in superusers
        ):
            user = await dao.users.upsert(dto.User(
                user_id=from_user.id,
                first_name=from_user.first_name,
                last_name=from_user.last_name,
                username=from_user.username,
                is_moder=from_user.id in superusers if user is None else user.is_moder,
            ))
            await set_commands(bot, [user])
            logger.info(
                "upserting user", 
                extra=user.model_dump()
            )

        data["user"] = user
        return await handler(event, data)


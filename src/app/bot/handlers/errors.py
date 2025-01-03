import logging

from aiogram.enums import ChatType
from aiogram.types import ErrorEvent


logger = logging.getLogger("app")


async def common_handler(err: ErrorEvent):
    if update := (
            err.update.message
            or err.update.callback_query
            or err.update.inline_query
            or err.update.my_chat_member
    ):
        user_id = update.from_user.id
    else:
        user_id = None

    logger.exception(
        "raised exception while polling", 
        exc_info=err.exception, 
        extra={"user_id": user_id}
    )
    if message := err.update.message:
        if message.chat.type == ChatType.PRIVATE:
            await message.answer("raised unknown error")

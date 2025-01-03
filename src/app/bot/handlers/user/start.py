import logging 

from aiogram import Bot
from aiogram.types import Message, ReactionTypeEmoji
from aiogram.filters import CommandObject

from app.db import dto, DAO
from app.bot.utils import set_commands


logger = logging.getLogger("app.handlers")


async def start(
    message: Message,
    command: CommandObject,
    invites: dict[str, dict[str, int]],
    dao: DAO,
    bot: Bot,
    user: dto.User | None,
):
    invite_token = command.args

    if invite_token in invites["moder"]:
        invited_by = invites["moder"].pop(invite_token)

        if user is None:
            user = await dao.users.upsert(_make_user_from_message(message, is_moder=True))
        else:
            user.is_moder = True
            user = await dao.users.upsert(user)

        await message.react([ReactionTypeEmoji(emoji="👌")])
        await set_commands(bot, [user])
        logger.info(
            "new moder", 
            extra={
                "invite_token": invite_token, 
                "user_id": message.from_user.id, 
                "invited_by": invited_by
            }
        )
        
    elif user is None and invite_token in invites["user"]:
        invited_by = invites["user"].pop(invite_token)
        user = await dao.users.upsert(_make_user_from_message(message))
        await message.react([ReactionTypeEmoji(emoji="👌")])
        await set_commands(bot, [user]) 
        logger.info(
            "new user", 
            extra={
                "invite_token": invite_token, 
                "user_id": message.from_user.id, 
                "invited_by": invited_by
            }
        )

    elif not user is None:
        await message.react([ReactionTypeEmoji(emoji="🤝")])


def _make_user_from_message(message: Message, is_moder: bool = False) -> dto.User:
    from_user = message.from_user
    return dto.User(
        user_id=from_user.id,
        first_name=from_user.first_name,
        last_name=from_user.last_name,
        username=from_user.username,
        is_moder=is_moder,
    )

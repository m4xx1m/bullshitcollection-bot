import secrets
import logging 

from aiogram import Bot 
from aiogram.filters import CommandObject
from aiogram.types import Message, ReactionTypeEmoji
from aiogram.utils.deep_linking import create_start_link

from app.db import DAO, dto
from app.bot.utils import unset_commands


logger = logging.getLogger("app.handlers")


async def add_user(
    message: Message,
    invites: dict[str, dict[str, int]],
    bot: Bot,
    command: CommandObject,
    dao: DAO
):
    try:
        user_id = int(str(command.args))
    except ValueError:
        pass
    else:
        await dao.users.upsert(dto.User(
            user_id=user_id,
            first_name=f"{user_id}",
            last_name=f"added by {message.from_user.id}"
        ))
        await message.react([ReactionTypeEmoji(emoji="👌")]) 
        logger.info(
            "new user from /add_user", 
            extra={"user_id": user_id, "added_by": message.from_user.id}
        )
        return 

    invite_token = secrets.token_hex(8)

    invites["user"][invite_token] = message.from_user.id
    
    start_link = await create_start_link(bot, invite_token)
    await message.answer(f"<code>{start_link}</code>")
    logger.info(
        "new add_user link", 
        extra={"user_id": message.from_user.id, "invite_token": invite_token}
    )


async def get_users(
    message: Message,
    dao: DAO,
):
    users = [user for user in await dao.users.get_all() if not user.is_moder]

    if len(users) == 0:
        text = "There is no users"
    else:
        text = "<b>Users list</b>\n\n"

    for user in users:
        text += f"<a href=\"tg://user?id={user.user_id}\">{user.full_name}</a> - "
        text += f"<code>{user.user_id}</code>\n"

    await message.answer(text)


async def del_user(
    message: Message,
    dao: DAO,
    bot: Bot,
    command: CommandObject,
    superusers: list[int],
):
    try:
        user_id = int(command.args)
    except ValueError:
        await message.reply("wrong user id")
        return 

    user_ = await dao.users.get(user_id)
    if user_ is None:
        await message.reply("couldn't find user")
        return 

    if user_.user_id in superusers:
        await message.reply("you can't demote superusers")
        return 

    if user_.is_moder and not message.from_user.id in superusers:
        await message.reply("you can't demote other moders")
        return 
    
    if await dao.users.delete(user_.user_id) == 0:
        # idk in which case it possible xd
        await message.reply("no users deleted")
        return 

    await message.react([ReactionTypeEmoji(emoji="👌")]) 
    await unset_commands(bot, user_id)
    logger.info(
        "deleted user", 
        extra={"user_id": message.from_user.id, "deleted_user_id": user_id}
    )

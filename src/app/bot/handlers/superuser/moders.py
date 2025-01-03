import secrets
import logging 

from aiogram import Bot 
from aiogram.filters import CommandObject
from aiogram.types import Message, ReactionTypeEmoji
from aiogram.utils.deep_linking import create_start_link

from app.db import DAO, dto
from app.bot.utils import set_commands


logger = logging.getLogger("app.handlers")


async def add_moder(
    message: Message,
    invites: dict[str, dict[str, int]],
    bot: Bot,
    command: CommandObject,
    dao: DAO,
):
    try:
        user_id = int(str(command.args))
    except ValueError:
        pass
    else:
        await dao.users.upsert(dto.User(
            user_id=user_id,
            first_name=f"{user_id}",
            last_name=f"added by {message.from_user.id}",
            is_moder=True,
        ))
        await message.react([ReactionTypeEmoji(emoji="👌")]) 
        logger.info(
            "new moder from /add_moder", 
            extra={"user_id": user_id, "added_by": message.from_user.id},
        )
        return 

    invite_token = secrets.token_hex(8)
    invites["moder"][invite_token] = message.from_user.id
    
    start_link = await create_start_link(bot, invite_token)
    logger.info(
        "new add_moder link", 
        extra={"user_id": message.from_user.id, "invite_token": invite_token}
    )
    await message.answer(f"<code>{start_link}</code>")


async def get_moders(
    message: Message,
    dao: DAO,
):
    moders = await dao.users.get_moders()
   
    text = "<b>Moders list</b>\n\n"

    for moder in moders:
        text += f"<a href=\"tg://user?id={moder.user_id}\">{moder.full_name}</a> - "
        text += f"<code>{moder.user_id}</code>\n"
    
    await message.answer(text)


async def del_moder(
    message: Message,
    dao: DAO,
    bot: Bot,
    command: CommandObject,
    superusers: list[int],
):
    try:
        moder_id = int(command.args)
    except ValueError:
        await message.reply("wrong user id")
        return 

    moder = await dao.users.get(moder_id)
    if not moder:
        await message.reply("user not found")
        return 

    if moder.user_id in superusers:
        await message.reply("you can't demote superusers")
        return

    moder.is_moder = False
    moder = await dao.users.upsert(moder)
    await message.react([ReactionTypeEmoji(emoji="👌")]) 
    await set_commands(bot, [moder])
    logger.info(
        "deleted moder", 
        extra={"user_id": message.from_user.id, "deleted_user_id": moder.user_id}
    )

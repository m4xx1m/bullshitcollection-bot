import logging

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import BotCommand, BotCommandScopeChat

from app.db import dto
from app.config import BotConfig


logger = logging.getLogger("app.utils")


def create_bot(config: BotConfig) -> Bot:
    session = None
    if api_path := config.api_path:
        session = AiohttpSession(api=TelegramAPIServer.from_base(api_path))
 
    return Bot(
        token=config.token,
        default=DefaultBotProperties(parse_mode="html"),
        session=session,
    )


def create_dispatcher() -> Dispatcher:
    return Dispatcher()


async def set_commands(
    bot: Bot, 
    users: list[dto.User], 
    superusers: list[int] | None = None
):
    user_commands = [
        # BotCommand(command="start", description="start")
    ]

    moder_commands = [
        BotCommand(command="upsert", description="add or edit saved item"),
        BotCommand(command="search", description="search saved item (limit 5)"),
        BotCommand(command="delete", description="delete saved item by id"),
        BotCommand(command="add_user", description="add user"),
        BotCommand(command="get_users", description="get list of users"),
        BotCommand(command="del_user", description="detete user by id"),
    ]

    superuser_commands = [
        BotCommand(command="add_moder", description="add moderator"),
        BotCommand(command="get_moders", description="get list of moderators"),
        BotCommand(command="del_moder", description="detele moderator by id"),
    ]

    for user in users:
        user_id = user.user_id
        commands = user_commands.copy()

        if user.is_moder:
            commands += moder_commands

        if not superusers is None and user_id in superusers:
            commands += superuser_commands
        
        if not commands:
            continue 
 
        try:
            logger.info("setting commands", extra={"user_id": user_id})
            await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=user_id))
        except TelegramBadRequest as err:
            logger.warning("failed set commands", extra={"user_id": user_id, "error": err.message})


async def unset_commands(bot: Bot, chat_id: int):
    try:
        await bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=chat_id))
        logger.info("unsetting commands", extra={"chat_id": chat_id})
    except TelegramBadRequest as err:
        logger.warning(
            "failed unset commands", 
            extra={"chat_id": chat_id, "error": err.message}
        )

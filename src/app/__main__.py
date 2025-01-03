import asyncio
import logging

from cachetools import TTLCache

from app.log import setup_logging
from app.config import load_config
from app.db import Database
from app.bot import create_bot, create_dispatcher, setup_bot, set_commands

logger = logging.getLogger("app")


async def main():
    config = load_config()
    setup_logging(config.log_level)
    logger.info("initialization")
    bot = create_bot(config.bot)
    dispatcher = create_dispatcher()
    database = Database(config.database)

    dispatcher.workflow_data.update({
        "database": database,
        "superusers": config.bot.superusers,
        "bullshit_channel_id": config.bullshit_channel_id,
        "invites": {
            "moder": TTLCache(maxsize=256, ttl=600),
            "user": TTLCache(maxsize=256, ttl=600),
        },
    })

    try:
        setup_bot(dispatcher)

        logger.info("settings commands")
        async with database.dao() as dao:
            users = await dao.users.get_all()
        logger.info("loaded users from database", extra={"count": len(users)})
        await set_commands(bot, users, config.bot.superusers)

        if config.bot.skip_updates:
            logger.info("skipping updates")
            await bot.delete_webhook(drop_pending_updates=True)

        logger.info("starting polling")
        await dispatcher.start_polling(bot)
    finally:
        logger.info("closing bot session")
        await bot.session.close()
        logger.info("closing dispatcher storage")
        await dispatcher.storage.close()
        logger.info("closing database connections")
        await database.close()


if __name__ == '__main__':
    asyncio.run(main())

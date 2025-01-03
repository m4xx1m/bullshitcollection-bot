import json
import logging 

from aiogram import Bot
from aiogram.types import Message, ReactionTypeEmoji

from app.db import DAO, dto


logger = logging.getLogger("app.handlers")


async def load_dump(
    message: Message, 
    bot: Bot,
    dao: DAO,
):
    reply = message.reply_to_message

    if not reply or not reply.document:
        await message.reply("You need reply to json file with dump")
        return 
    
    file = await bot.download_file((await bot.get_file(reply.document.file_id)).file_path)
    
    try:
        dump = json.load(file)
    except json.JSONDecodeError:
        await message.reply("Wrong json file")
        return 
    
    for save in dump:
        try:
            save = dto.Save(
                file_id=save["file_id"],
                caption=save["caption"],
                media_type=dto.MediaType(save["type"]),
            )
            logger.info("upserting save (from dump)", extra=save.model_dump())
            await dao.saves.upsert(save)
        except:
            await dao.rollback()
            raise 

    await message.react([ReactionTypeEmoji(emoji="👌")]) 

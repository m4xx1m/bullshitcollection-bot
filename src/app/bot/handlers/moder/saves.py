import re
import logging 

from aiogram.filters import CommandObject
from aiogram.types import Message, ReactionTypeEmoji, PhotoSize

from app.db import DAO, dto


HTML_TAG_RE = r"<[^>]*>"

logger = logging.getLogger("app.handlers")


async def upsert(
    message: Message,
    command: CommandObject,
    dao: DAO,
    bullshit_channel_id: int
):
    caption = ""
    external_reply = message.external_reply

    if (
        external_reply is None
        or external_reply.chat is None
        or external_reply.chat.id != bullshit_channel_id
    ):
        await message.reply("you need reply to message from {bullshit_channel_id}")
        return 

    if command.args:
        caption += str(command.args) + " "

    elif quote := message.quote:
        caption += str(quote.text) + " "
    
    if animation := external_reply.animation:
        file_id = animation.file_id
        media_type = dto.MediaType.ANIMATION

    elif audio := external_reply.audio:
        file_id = audio.file_id
        media_type = dto.MediaType.AUDIO

        if title := audio.title:
            caption += str(title) + " "
       
        if performer := audio.performer:
            caption += str(performer) + " "
    
        if not caption and (file_name := audio.file_name):
            caption += str(file_name) + " "

    elif file := external_reply.document:
        file_id = file.file_id
        media_type = dto.MediaType.FILE
        
        if not caption and (file_name := file.file_name):
            caption += str(file_name) + " "

    elif photo := external_reply.photo:
        file_id = _select_photo(photo).file_id
        media_type = dto.MediaType.PHOTO

    elif sticker := external_reply.sticker:
        file_id = sticker.file_id
        media_type = dto.MediaType.STICKER
        
        if not caption and (emoji := sticker.emoji):
            caption += str(emoji) + " "

    elif video := external_reply.video:
        file_id = video.file_id
        media_type = dto.MediaType.VIDEO

    elif voice := external_reply.voice:
        file_id = voice.file_id
        media_type = dto.MediaType.VOICE

    elif video_note := external_reply.video_note:
        file_id = video_note.file_id
        media_type = dto.MediaType.VIDEO_NOTE

    else:
        await message.reply("can't parse media from reply")
        return 

    caption = caption.strip()

    if not caption:
        await message.reply("can't parse caption from reply/media/command")
        return 
    
    save = dto.Save(
        file_id=file_id,
        caption=caption,
        media_type=media_type,
    )
    await dao.saves.upsert(save)

    logger.info("upserting save", extra={"user_id": message.from_user.id, **save.model_dump()})
    await message.react([ReactionTypeEmoji(emoji="👌")])


async def search(
    message: Message,
    command: CommandObject,
    dao: DAO
):
    text = ""
    query = command.args
    if not query:
        await message.reply("you must provide search query")
        return 

    results = await dao.saves.search(query, limit=5, reverse=True)
    if not results:
        await message.reply("no item found")
        return 

    for result in results:
        item_text = f"Caption: <code>{result.caption}</code>\n"
        item_text += f"Type: <code>{result.media_type.value}</code>\n"
        item_text += f"FileID: <code>{result.file_id}</code>"
        if len(_remove_html_tags(text + item_text)) > 4096:
            continue 
        text += item_text + "\n\n"
    
    await message.answer(text)


async def delete(
    message: Message,
    command: CommandObject,
    dao: DAO,
):
    file_id = command.args
    if not file_id:
        await message.answer("you must provide file_id (you can find it in /search <query>")
        return 

    if not await dao.saves.delete(file_id):
        await message.reply("no item deleted")
    else:
        logger.info("save deleted", extra={"user_id": message.from_user.id, "file_id": file_id})
        await message.react([ReactionTypeEmoji(emoji="👌")])


def _remove_html_tags(text: str) -> str:
    for tag in re.findall(HTML_TAG_RE, text):
        text = text.replace(tag, "")
    return text 

def _select_photo(photos: list[PhotoSize]) -> PhotoSize:
    return sorted(photos, reverse=True, key=lambda photo: photo.width * photo.height)[0]

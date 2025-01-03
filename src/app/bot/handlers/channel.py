import logging 

from aiogram.types import Message, PhotoSize

from app.db import DAO, dto


logger = logging.getLogger("app.handlers")


async def edited_post(
    message: Message,
    dao: DAO,
):
    if animation := message.animation:
        file_id = animation.file_id
        media_type = dto.MediaType.ANIMATION

    elif audio := message.audio:
        file_id = audio.file_id
        media_type = dto.MediaType.AUDIO

    elif file := message.document:
        file_id = file.file_id
        media_type = dto.MediaType.FILE
    
    elif photo := message.photo:
        file_id = _select_photo(photo).file_id
        media_type = dto.MediaType.PHOTO

    elif sticker := message.sticker:
        file_id = sticker.file_id
        media_type = dto.MediaType.STICKER
    
    elif video := message.video:
        file_id = video.file_id
        media_type = dto.MediaType.VIDEO

    elif voice := message.voice:
        file_id = voice.file_id
        media_type = dto.MediaType.VOICE

    elif video_note := message.video_note:
        file_id = video_note.file_id
        media_type = dto.MediaType.VIDEO_NOTE

    else:
        logger.warning("failed parse file_id", extra={"message_id": message.id})
        return 

    save = dto.Save(
        file_id=file_id,
        caption=message.text or message.caption,
        media_type=media_type,
    )
    await dao.saves.upsert(save)
    logger.info("upserting save (from channel)", extra={**save.model_dump()})


def _select_photo(photos: list[PhotoSize]) -> PhotoSize:
    return sorted(photos, reverse=True, key=lambda photo: photo.width * photo.height)[0]

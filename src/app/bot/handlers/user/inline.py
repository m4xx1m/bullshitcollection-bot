import hashlib
import logging 

from aiogram.types import (
    InlineQuery, 
    InlineQueryResult,
    InlineQueryResultCachedVideo,
    InlineQueryResultCachedAudio,
    InlineQueryResultCachedPhoto,
    InlineQueryResultCachedVoice,
    InlineQueryResultCachedSticker,
    InlineQueryResultCachedDocument,
)

from app.db import DAO
from app.db.dto import MediaType


logger = logging.getLogger("app.handlers")


async def inline(
    inline_query: InlineQuery,
    dao: DAO
):
    photo_mode = False
    sticker_mode = False

    answer = list[InlineQueryResult]()

    query = inline_query.query
    _query_split = query.split(" ", 1)
    if query and (mode := _query_split[0]) in ["p", "s"]:
        match mode:
            case "p": 
                photo_mode = True
            case "s":
                sticker_mode = True
        
        if len(_query_split) > 1:
            query = _query_split[1]
        else:
            query= ""
    
    if query:
        results = await dao.saves.get(caption=query, limit=40, reverse=True)
    else:
        results = await dao.saves.get_all(limit=40, reverse=True)

    logger.info(
        "searching query", 
        extra={
            "user_id": inline_query.from_user.id, 
            "query": query,
            "found": len(results),
            "mode": "photo" if photo_mode else "sticker" if sticker_mode else "all",
        },
    )

    for result in results:
        text_media_type = _get_text_media_type(result.media_type)
        title = f"[{text_media_type}] {result.caption}"
        result_id = hashlib.md5(result.file_id.encode()).hexdigest()

        if photo_mode and result.media_type is MediaType.PHOTO:
            answer.append(InlineQueryResultCachedPhoto(
                id=result_id,
                photo_file_id=result.file_id,
            ))

        if sticker_mode and result.media_type is MediaType.STICKER:
            answer.append(InlineQueryResultCachedSticker(
                id=result_id,
                sticker_file_id=result.file_id,
            ))
        
        if photo_mode or sticker_mode:
            continue

        match result.media_type:
            case MediaType.VIDEO | MediaType.ANIMATION | MediaType.VIDEO_NOTE:
                answer.append(InlineQueryResultCachedVideo(
                    id=result_id,
                    video_file_id=result.file_id,
                    title=title,
                ))
            case MediaType.AUDIO:
                answer.append(InlineQueryResultCachedAudio(
                    id=result_id,
                    audio_file_id=result.file_id,
                    title=title,
                ))
            case MediaType.FILE:
                answer.append(InlineQueryResultCachedDocument(
                    id=result_id,
                    document_file_id=result.file_id,
                    title=title,
                ))
            case MediaType.VOICE:
                answer.append(InlineQueryResultCachedVoice(
                    id=result_id,
                    voice_file_id=result.file_id,
                    title=title,
                ))
                    
    await inline_query.answer(
        results=answer,
        cache_time=300,
        is_personal=False,
    )
 

def _get_text_media_type(media_type: MediaType) -> str:
    match media_type:
        case MediaType.ANIMATION:
            return "GIF"
        case MediaType.VIDEO_NOTE:
            return "round"
        case MediaType.VIDEO:
            return "VID"
        case MediaType.AUDIO:
            return "AUDIO"
        case MediaType.PHOTO:
            return "PHOTO"
        case MediaType.STICKER:
            return "STICKER"
        case MediaType.FILE:
            return "FILE"
        case MediaType.VOICE:
            return "VOICE"

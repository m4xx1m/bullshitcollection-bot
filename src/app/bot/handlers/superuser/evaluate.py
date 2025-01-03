import html
import asyncio
import traceback

from meval import meval

from aiogram import Bot
from aiogram.filters import CommandObject
from aiogram.types import Message, BufferedInputFile


async def evaluate(
    message: Message, 
    bot: Bot, 
    command: CommandObject, 
    **kwargs
):
    answer = kwargs.get("_eval_answer", True)

    ex_args = kwargs.copy()
    ex_args.update({
        "bot": bot,
        "loop": asyncio.get_event_loop(),
        "message": message,
        "reply": message.reply_to_message
    })
    
    if answer:
        process_message = await message.answer("<code>Executing...</code>")
    else:
        process_message = None 

    try:
        result = await meval(command.args, globals(), **ex_args)
    except Exception as err:
        answer = True
        result = "".join(traceback.format_exception(err))
    
    if answer is False:
        return 

    result = str(result)
    if not result:
        result = "None"

    if len(result) > 4096:
        await message.answer_document(
            document=BufferedInputFile(
                file=result.encode("utf-8"),
                filename="result.txt"
            )
        )
        if process_message:
            await process_message.delete()
    else:
        answer_text = f"<code>{html.escape(result)}</code>"
        if process_message:
            await process_message.edit_text(answer_text)
        else:
            await message.answer(answer_text)


async def execute(message: Message, bot: Bot, command: CommandObject, **kwargs):
    return await evaluate(message, bot, command, _eval_answer=False, **kwargs)

from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.filters import MagicData, CommandStart, Command

from . import handlers, middlewares


def setup(router: Router):
    users_middleware = middlewares.UsersMiddleware()
    dao_middleware = middlewares.DAOMiddleware()

    is_private_chat_filter = F.chat.type == ChatType.PRIVATE
    is_user_exists_filter = F.user
    is_moder_filter = F.user.is_moder
    is_registered_channel_filter = F.event_chat.id == F.bullshit_channel_id
    is_superuser_filter = F.event_from_user.id.in_(F.superusers)
    
    router.errors.outer_middleware.register(dao_middleware)
    router.message.outer_middleware.register(dao_middleware)
    router.inline_query.outer_middleware.register(dao_middleware)
    router.edited_channel_post.outer_middleware.register(dao_middleware)

    router.errors.outer_middleware.register(users_middleware)
    router.message.outer_middleware.register(users_middleware)
    router.inline_query.outer_middleware.register(users_middleware)

    # channel
    # edited
    router.edited_channel_post.register(
        handlers.channel.edited_post,
        MagicData(is_registered_channel_filter),
    )
    
    # superuser
    # /add_moder
    router.message.register(
        handlers.superuser.moders.add_moder,
        Command(commands=["add_moder"]), MagicData(is_superuser_filter),
    )
    # /get_moders
    router.message.register(
        handlers.superuser.moders.get_moders,
        Command(commands=["get_moders"]), MagicData(is_superuser_filter),
    )
    # /del_moder
    router.message.register(
        handlers.superuser.moders.del_moder,
        Command(commands=["del_moder"]), MagicData(is_superuser_filter),
    )
    # /eval
    router.message.register(
        handlers.superuser.evaluate,
        Command(commands=["eval", "e"]), MagicData(is_superuser_filter),
    )
    # /exec
    router.message.register(
        handlers.superuser.execute,
        Command(commands=["exec", "ex"]), MagicData(is_superuser_filter),
    )
    # /load_dump
    router.message.register(
        handlers.superuser.load_dump,
        Command(commands=["load_dump"]), MagicData(is_superuser_filter),
    )

    # moders
    # /upsert
    router.message.register(
        handlers.moder.saves.upsert,
        Command(commands=["upsert"]), MagicData(is_moder_filter), is_private_chat_filter,
    )
    # /search
    router.message.register(
        handlers.moder.saves.search,
        Command(commands=["search"]), MagicData(is_moder_filter), is_private_chat_filter,
    )
    # /delete
    router.message.register(
        handlers.moder.saves.delete,
        Command(commands=["delete"]), MagicData(is_moder_filter), is_private_chat_filter,
    )
    # /add_user
    router.message.register(
        handlers.moder.users.add_user, 
        Command(commands=["add_user"]), MagicData(is_moder_filter)
    )
    # /get_users
    router.message.register(
        handlers.moder.users.get_users, 
        Command(commands=["get_users"]), MagicData(is_moder_filter)
    )
    # /del_user
    router.message.register(
        handlers.moder.users.del_user, 
        Command(commands=["del_user"]), MagicData(is_moder_filter)
    )

    # users
    # /start 
    router.message.register(
        handlers.user.start,
        CommandStart(), is_private_chat_filter,
    )
    # inline 
    router.inline_query.register(
        handlers.user.inline,
        MagicData(is_user_exists_filter),
    )


    # errors
    router.errors.register(
        handlers.errors.common_handler
    )

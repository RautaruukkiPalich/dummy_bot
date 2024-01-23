from aiogram import types, Router
from aiogram.filters import Command

from dummy_bot.bot.db_queries import (
    get_or_create_member,
    delete_member,
    create_pokak, get_pokak_stat, )
from dummy_bot.bot.utils import (
    get_user,
    create_stat,
)


router = Router()


@router.message(Command(commands=["pokakstats", "pokakall"]))
async def pokak_stats(message: types.Message) -> None:
    periods = {
        "pokakstats": "year",
        "pokakall": "all",
    }
    period = periods.get(message.text[1:])
    stat = await get_pokak_stat(period)
    stat_text = await create_stat(stat, period)
    await message.reply(text=stat_text)


@router.message(Command(commands=["join"]))
async def join(message: types.Message) -> None:
    user = await get_user(message)
    await get_or_create_member(user)
    await message.reply(text=f'@{user.username} added to `pokaks`')


@router.message(Command(commands=["leave"]))
async def leave(message: types.Message) -> None:
    user = await get_user(message)
    await delete_member(user)
    await message.reply(text=f'@{user.username} leaves from `pokaks`')


@router.message()
async def text(message: types.Message) -> any:
    ANIMATION_LIST = ['shrek-somebody.mp4']
    animation = message.animation
    if animation and animation.file_name in ANIMATION_LIST:
        user = await get_user(message)
        await create_pokak(user)
        await message.reply(text="s pokakom")

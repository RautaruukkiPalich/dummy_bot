from typing import List

from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.bot.fsm import SetMedia
from dummy_bot.bot.utils import (
    is_admin,
    get_file_unique_id,
    get_start_end_period,
    create_report,
)
from dummy_bot.db.crud import (
    create_or_update_user,
    get_user,
    delete_user,
    create_or_update_media,
    create_pokak,
    get_media,
    get_or_create_group,
    get_pokak_stat,
)

router = Router()


@router.message(Command(commands=[
    "pokakstatweek",
    "pokakstatmonth",
    "pokakstatyear",
    "pokakstatall",
]))
async def stats(message: types.Message, session: AsyncSession) -> None:
    periods = {
        "pokakstatweek": "week",
        "pokakstatmonth": "month",
        "pokakstatyear": "year",
        "pokakstatall": "all",
    }
    period = periods.get(message.text[1:].split("@")[0])
    start, end = await get_start_end_period(period)
    data = await get_pokak_stat(
        str(message.chat.id),
        start, end, session,
    )
    stat_text = await create_report(data, period)
    await message.answer(text=stat_text)


@router.message(Command(commands=["setpokakmedia"]))
async def set_media(message: types.Message, admins: List[int], session: AsyncSession, state: FSMContext) -> None:
    if not await is_admin(message, admins):
        await message.reply(text='У тебя нет прав назначать медиафайл')
        await text(message, session)
        return

    await state.set_state(SetMedia.get_media)

    await message.reply(text=f'Отправь мне гифку или стикер, которая будет обозначать успешный покак')


@router.message(SetMedia.get_media)
async def callback_set_media(message: types.Message, admins: List[int], session: AsyncSession, state: FSMContext) -> None:
    if not await is_admin(message, admins):
        await message.reply(text='У тебя нет прав назначать медиафайл')
        await text(message, session)
        return

    file_unique_id = await get_file_unique_id(message)
    if not file_unique_id:
        await message.reply(text=f'Отправь мне гифку или стикер, которая будет обозначать успешный покак')
        return

    await create_or_update_media(
        group_id=str(message.chat.id),
        new_media=file_unique_id,
        session=session,
    )
    await state.clear()
    await message.reply(text=f'Success: отправляй его, когда покакаешь')


@router.message(Command(commands=["join"]))
async def join(message: types.Message, session: AsyncSession) -> None:
    user = await create_or_update_user(
        group_id=str(message.chat.id),
        chat_id=str(message.from_user.id),
        username=message.from_user.username,
        fullname=message.from_user.full_name,
        session=session,
    )
    if not user.username:
        await message.reply(text=f'@{user.full_name} теперь с нами')
    await message.reply(text=f'@{user.username} теперь с нами')


@router.message(Command(commands=["leave"]))
async def leave(message: types.Message, session: AsyncSession) -> None:
    user = await delete_user(
        group_id=str(message.chat.id),
        chat_id=str(message.from_user.id),
        session=session,
    )
    if not user:
        await message.reply(text=f'Ты не заргистрирован. Нажми /join')
        return
    if not user.username:
        await message.reply(text=f'@{user.full_name}, чтоб тебя запоры мучали')
    await message.reply(text=f'@{user.username}, чтоб тебя запоры мучали')


@router.message()
async def text(message: types.Message, session: AsyncSession) -> any:

    if message.animation or message.sticker:
        file_unique_id = await get_file_unique_id(message)
        if not file_unique_id:
            return

        group = await get_or_create_group(
            group_id=str(message.chat.id),
            session=session,
        )
        media = await get_media(
            group=group,
            session=session,
        )
        if not media:
            return

        if not file_unique_id == media.media_unique_id:
            return

        user = await get_user(
            group=group,
            chat_id=str(message.from_user.id),
            session=session,
        )
        if not user or not user.is_active:
            return

        await create_pokak(user, session)
        await message.reply(text="👌")

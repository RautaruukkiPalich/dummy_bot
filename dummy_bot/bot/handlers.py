from typing import List

from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.bot.fsm import SetMedia
from dummy_bot.bot.utils import (
    is_admin,
    get_file_unique_id,
    CommandStatEnum,
    PeriodEnum,
    Report,
)
from dummy_bot.db.crud import (
    UserRepo,
    GroupRepo,
    PokakRepo,
    MediaRepo,
)

router = Router()


@router.message(Command(commands=[
    CommandStatEnum.WEEK.value,
    CommandStatEnum.MONTH.value,
    CommandStatEnum.YEAR.value,
    CommandStatEnum.ALL.value,
]
))
async def stats(message: types.Message, session: AsyncSession) -> None:
    group = await GroupRepo.get(session, str(message.chat.id))
    if not group:
        await message.answer(text="Вы не участвуете", parse_mode="HTML")
        return

    command = message.text[1:].split("@")[0]

    period = PeriodEnum.from_command(command)
    start, end = period.get_date_scope()

    data = await PokakRepo.group_stat_by_period(session, group, start, end)

    report_text = Report(period, data).prepare()
    await message.answer(text=report_text, parse_mode="HTML")


@router.message(Command(commands=["setpokakmedia"]))
async def set_media(message: types.Message, admins: List[int], session: AsyncSession, state: FSMContext) -> None:
    print("handled set pokak media ")
    if not await is_admin(message, admins):
        await message.reply(text='У тебя нет прав назначать медиафайл')
        await handle_text(message, session)
        return

    await state.set_state(SetMedia.get_media)

    await message.reply(text=f'Отправь мне гифку или стикер, которая будет обозначать успешный покак')


@router.message(SetMedia.get_media)
async def callback_set_media(
        message: types.Message,
        admins: List[int],
        session: AsyncSession,
        state: FSMContext,
) -> None:
    group = await GroupRepo.get(session, str(message.chat.id))
    if not group:
        await message.reply(text='Я запрещаю вам какать')
        return

    if not await is_admin(message, admins):
        await message.reply(text='У тебя нет прав назначать медиафайл')
        await handle_text(message, session)
        return

    file_unique_id = await get_file_unique_id(message)
    if not file_unique_id:
        await message.reply(text=f'Отправь мне гифку или стикер, которая будет обозначать успешный покак')
        return

    media = await MediaRepo.get(session, group)

    if not media:
        await MediaRepo.create(session, group, file_unique_id)
    else:
        media.media_unique_id = file_unique_id
        await MediaRepo.update(session, media)

    await state.clear()
    await message.reply(text=f'Success: отправляй его, когда покакаешь')


@router.message(Command(commands=["join"]))
async def join(message: types.Message, admins: List[int], session: AsyncSession) -> None:
    group = await GroupRepo.get(session, str(message.chat.id))
    if not group:
        if not await is_admin(message, admins):
            return

        group = await GroupRepo.create(session, str(message.chat.id))

    user = await UserRepo.get(session, group, str(message.from_user.id))
    if not user:
        user = await UserRepo.create(
            session, group,
            str(message.from_user.id),
            message.from_user.username,
            message.from_user.full_name,
        ),

    if not user.username:
        await message.reply(text=f'{user.fullname} теперь с нами')
    await message.reply(text=f'@{user.username} теперь с нами')


@router.message(Command(commands=["leave"]))
async def leave(message: types.Message, session: AsyncSession) -> None:
    group = await GroupRepo.get(session, str(message.chat.id))
    if not group:
        return

    user = await UserRepo.get(session, group, str(message.from_user.id))
    if not user:
        return

    if not await UserRepo.delete(session, user):
        return

    if not user.username:
        await message.reply(text=f'{user.fullname}, чтоб тебя запоры мучали')
    await message.reply(text=f'@{user.username}, чтоб тебя запоры мучали')


@router.message()
async def handle_text(message: types.Message, session: AsyncSession) -> None:
    if not (message.animation or message.sticker):
        return

    file_unique_id = await get_file_unique_id(message)
    if not file_unique_id:
        return

    group = await GroupRepo.get(session, str(message.chat.id))
    if not group:
        return

    media = await MediaRepo.get(session, group)
    if not media:
        return

    if not file_unique_id == media.media_unique_id:
        return

    user = await UserRepo.get(session, group, str(message.from_user.id))

    if not user or not user.is_active:
        return

    await PokakRepo.add(session, user)

    await message.react([types.ReactionTypeEmoji(emoji="👍")])

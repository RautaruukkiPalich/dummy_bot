import functools
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
from dummy_bot.bot.interfaces import IGroupRepo, IUserRepo, IMediaRepo, IPokakRepo
from dummy_bot.db.models import User


class Service:
    def __init__(self,
                 group_repo: IGroupRepo,
                 user_repo: IUserRepo,
                 media_repo: IMediaRepo,
                 pokak_repo: IPokakRepo,
                 rout: Router,
                 ):
        self._group_repo = group_repo
        self._user_repo = user_repo
        self._media_repo = media_repo
        self._pokak_repo = pokak_repo
        self._router = rout
        self.__register_handlers()

    @staticmethod
    def __transactional(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            session = kwargs.get('session')
            if session and not session.in_transaction():
                async with session.begin():
                    return await func(*args, **kwargs)
            return await func(*args, **kwargs)

        return wrapper

    def __register_handlers(self) -> None:

        @self._router.message(Command(commands=[
            CommandStatEnum.WEEK.value,
            CommandStatEnum.MONTH.value,
            CommandStatEnum.YEAR.value,
            CommandStatEnum.ALL.value,
        ]
        ))
        @self.__transactional
        async def stats(message: types.Message, session: AsyncSession) -> None:
            group = await self._group_repo.get(session, str(message.chat.id))
            if not group:
                await message.answer(text="Вы не участвуете", parse_mode="HTML")
                return

            command = message.text[1:].split("@")[0]

            period = PeriodEnum.from_command(command)
            start, end = period.get_date_scope()

            data = await self._pokak_repo.group_stat_by_period(session, group, start, end)

            report_text = Report(period, data).prepare()
            await message.answer(text=report_text, parse_mode="HTML")

        @self._router.message(Command(commands=["setpokakmedia"]))
        async def set_media(message: types.Message, admins: List[int], session: AsyncSession, state: FSMContext) -> None:
            if not await is_admin(message, admins):
                await message.reply(text='У тебя нет прав назначать медиафайл')
                return

            await state.set_state(SetMedia.get_media)

            await message.reply(text=f'Отправь мне гифку или стикер, которая будет обозначать успешный покак')

        @self._router.message(SetMedia.get_media)
        @self.__transactional
        async def callback_set_media(
                message: types.Message,
                admins: List[int],
                session: AsyncSession,
                state: FSMContext,
        ) -> None:
            group = await self._group_repo.get(session, str(message.chat.id))
            if not group:
                await message.reply(text='Я запрещаю вам какать')
                return

            if not await is_admin(message, admins):
                await message.reply(text='У тебя нет прав назначать медиафайл')
                return

            file_unique_id = await get_file_unique_id(message)
            if not file_unique_id:
                await message.reply(text=f'Отправь мне гифку или стикер, которая будет обозначать успешный покак')
                return

            media = await self._media_repo.get(session, group)

            if not media:
                await self._media_repo.create(session, group, file_unique_id)
            else:
                media.media_unique_id = file_unique_id
                if not await self._media_repo.update(session, media):
                    raise PermissionError("cant update media")

            await state.clear()
            await message.reply(text=f'Success: отправляй его, когда покакаешь')

        @self._router.message(Command(commands=["join"]))
        @self.__transactional
        async def join(message: types.Message, admins: List[int], session: AsyncSession) -> None:
            group = await self._group_repo.get(session, str(message.chat.id))
            if not group:
                if not await is_admin(message, admins):
                    raise AttributeError("user is not admin")

                group = await self._group_repo.create(session, str(message.chat.id))

            user = await self._user_repo.get(session, group, str(message.from_user.id))
            if not user:
                user = await self._user_repo.create(
                    session, group,
                    str(message.from_user.id),
                    message.from_user.username,
                    message.from_user.full_name,
                )

            user.activate()
            if not await self._user_repo.update(session, user):
                raise AttributeError("cant update user")

            await message.reply(text=f'{self._get_user_name(user)} теперь с нами')

        @self._router.message(Command(commands=["leave"]))
        @self.__transactional
        async def leave(message: types.Message, session: AsyncSession) -> None:
            group = await self._group_repo.get(session, str(message.chat.id))
            if not group:
                raise AttributeError("no such group")

            user = await self._user_repo.get(session, group, str(message.from_user.id))
            if not user:
                raise AttributeError("no such user")

            user.deactivate()
            if not await self._user_repo.update(session, user):
                raise AttributeError("cant update user")

            await message.reply(text=f'{self._get_user_name(user)}, чтоб тебя запоры мучали')

        @self._router.message()
        @self.__transactional
        async def handle_text(message: types.Message, session: AsyncSession) -> None:
            if not (message.animation or message.sticker):
                return

            file_unique_id = await get_file_unique_id(message)
            if not file_unique_id:
                return

            group = await self._group_repo.get(session, str(message.chat.id))
            if not group:
                return

            media = await self._media_repo.get(session, group)
            if not media:
                return

            if not file_unique_id == media.media_unique_id:
                return

            user = await self._user_repo.get(session, group, str(message.from_user.id))

            if not user or not user.is_active:
                return

            await self._pokak_repo.add(session, user)
            await message.react([types.ReactionTypeEmoji(emoji="👍")])

    @staticmethod
    def _get_user_name(user: User) -> str:
        if not user.username:
            return f'{user.fullname}'
        return f'@{user.username}'

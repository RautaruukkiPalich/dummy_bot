from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.db.models import User, Group
from internal.usecase.interfaces import IUOW, ICmdsGroupRepo, ICmdsUserRepo


class CommandsUseCase:
    def __init__(
            self,
            group_repo: ICmdsGroupRepo,
            user_repo: ICmdsUserRepo,
            uow: IUOW,
    ) -> None:
        self._group_repo: ICmdsGroupRepo = group_repo
        self._user_repo: ICmdsUserRepo = user_repo
        self._uow: IUOW = uow

    async def start(self, message: types.Message, session: AsyncSession) -> None:
        async with self._uow.with_tx(session):
            group = await self._group_repo.get_by_chat_id(session, str(message.chat.id))
            if group: return

            group = Group(group_id=str(message.chat.id))
            await self._group_repo.insert(session, group)

    async def join(self, message: types.Message, session: AsyncSession) -> None:
        async with self._uow.with_tx(session):
            group = await self._group_repo.get_by_chat_id(session, str(message.chat.id))
            if not group: raise Exception()

            user = await self._user_repo.get_by_group_and_user_id(session, str(message.from_user.id), group)

            if not user:
                user = User(
                    chat_id=str(message.from_user.id),
                    group_id=group.id,
                    username=message.from_user.username,
                    fullname=message.from_user.full_name,
                )

            user.activate()
            await self._user_repo.insert(session, user)

    async def leave(self, message: types.Message, session: AsyncSession) -> None:
        async with self._uow.with_tx(session):
            group = await self._group_repo.get_by_chat_id(session, str(message.chat.id))
            if not group: raise Exception()

            user = await self._user_repo.get_by_group_and_user_id(session, str(message.from_user.id), group)
            if not user: raise Exception()

            user.deactivate()
            await self._user_repo.update(session, user)

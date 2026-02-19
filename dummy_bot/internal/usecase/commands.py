from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.internal.dto.dto import TelegramMessageDTO
from dummy_bot.internal.models.models import User, Group
from dummy_bot.internal.usecase.interfaces import IUOW, IGroupRepo, IUserRepo


class CommandsUseCase:
    def __init__(
            self,
            group_repo: IGroupRepo,
            user_repo: IUserRepo,
            uow: IUOW,
    ) -> None:
        self._group_repo: IGroupRepo = group_repo
        self._user_repo: IUserRepo = user_repo
        self._uow: IUOW = uow

    async def start(self, session: AsyncSession, dto: TelegramMessageDTO) -> None:
        async with self._uow.with_tx(session):
            group = await self._group_repo.get_by_chat_id(session, dto.chat_id)
            if group: return

            group = Group(group_id=dto.chat_id)
            await self._group_repo.insert(session, group)

    async def join(self, session: AsyncSession, dto: TelegramMessageDTO) -> None:
        async with self._uow.with_tx(session):
            group = await self._group_repo.get_by_chat_id(session, dto.chat_id)
            if not group: raise Exception()

            user = await self._user_repo.get_by_group_and_user_chat_id(session, dto.user_chat_id, group)

            if not user:
                user = User(
                    chat_id=dto.user_chat_id,
                    group_id=group.id,
                    username=dto.username,
                    fullname=dto.fullname,
                )

            user.activate()
            await self._user_repo.insert(session, user)

    async def leave(self, session: AsyncSession, dto: TelegramMessageDTO) -> None:
        async with self._uow.with_tx(session):
            group = await self._group_repo.get_by_chat_id(session, dto.chat_id)
            if not group: raise Exception()

            user = await self._user_repo.get_by_group_and_user_chat_id(session, dto.user_chat_id, group)
            if not user: raise Exception()

            user.deactivate()
            await self._user_repo.update(session, user)

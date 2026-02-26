from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.internal.dto.dto import TelegramMessageDTO
from dummy_bot.internal.models.models import User, Group
from dummy_bot.internal.usecase.interfaces import IGroupRepo, IUserRepo, T_UOW, IUOWFactory


class CommandsUseCase:
    def __init__(
            self,
            group_repo: IGroupRepo,
            user_repo: IUserRepo,
            uow_factory: IUOWFactory[T_UOW],
    ) -> None:
        self._group_repo: IGroupRepo = group_repo
        self._user_repo: IUserRepo = user_repo
        self._uow_factory: IUOWFactory[T_UOW] = uow_factory


    async def start(self, dto: TelegramMessageDTO) -> None:
        async with self._uow_factory() as uow:
            async with uow.with_tx() as session:
                group = await self._group_repo.get_by_chat_id(session, dto.chat_id)
                if group: return

                group = Group(group_id=dto.chat_id)
                await self._group_repo.save(session, group)

    async def join(self, dto: TelegramMessageDTO) -> None:
        async with self._uow_factory() as uow:
            async with uow.with_tx() as session:
                group = await self._get_group_strict(session, dto.chat_id)

                user = await self._user_repo.get_by_group_and_user_chat_id(session, dto.user_chat_id, group)

                if not user:
                    user = User(
                        chat_id=dto.user_chat_id,
                        group_id=group.id,
                        username=dto.username,
                        fullname=dto.fullname,
                    )

                user.activate()

                await self._user_repo.save(session, user)

    async def leave(self, dto: TelegramMessageDTO) -> None:
        async with self._uow_factory() as uow:
            async with uow.with_tx() as session:
                group = await self._get_group_strict(session, dto.chat_id)
                user = await self._get_user_strict(session, dto.user_chat_id, group)
                user.deactivate()
                await self._user_repo.save(session, user)

    async def _get_group_strict(self, session: AsyncSession, chat_id: int) -> Group:
        group = await self._group_repo.get_by_chat_id(session, chat_id)
        if not group: raise Exception()
        return group

    async def _get_user_strict(self, session: AsyncSession, user_chat_id: int, group: Group) -> User:
        user = await self._user_repo.get_by_group_and_user_chat_id(session, user_chat_id, group)
        if not user: raise Exception()
        return user
from contextlib import AbstractAsyncContextManager
from typing import Protocol, List, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.internal.models.models import User, Group, Media, Pokak
from dummy_bot.internal.dto.dto import StatisticFilterDTO, UserStatInfoDTO


class IUserRepo(Protocol):
    async def get_by_group_and_user_chat_id(self, session: AsyncSession, user_chat_id: int,
                                            group: Group) -> User | None: ...

    async def save(self, session: AsyncSession, user: User) -> User: ...


class IGroupRepo(Protocol):
    async def get_by_chat_id(self, session: AsyncSession, chat_id: int) -> Group | None: ...

    async def save(self, session: AsyncSession, group: Group) -> Group: ...


class IStatisticsRepo(Protocol):
    async def statistics(self, session: AsyncSession, group: Group, f: StatisticFilterDTO) -> List[UserStatInfoDTO]: ...


class IMediaRepo(Protocol):
    async def get_by_group(self, session: AsyncSession, group: Group) -> Media | None: ...

    async def save(self, session: AsyncSession, media: Media) -> Media: ...


class IPokakRepo(Protocol):
    async def save(self, session: AsyncSession, pokak: Pokak) -> Pokak: ...


class IUnitOfWork(Protocol):
    @property
    def session(self) -> AsyncSession: ...

    def with_tx(self) -> AbstractAsyncContextManager[AsyncSession]: ...

    def readonly(self) -> AbstractAsyncContextManager[AsyncSession]: ...

    async def __aenter__(self) -> 'IUnitOfWork': ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...


T_UOW = TypeVar('T_UOW', bound=IUnitOfWork, covariant=True)


class IUOWFactory(Protocol[T_UOW]):
    def __call__(self) -> T_UOW: ...

    async def __aenter__(self) -> T_UOW: ...

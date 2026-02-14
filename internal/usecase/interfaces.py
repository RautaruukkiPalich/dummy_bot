from typing import Protocol, AsyncContextManager, List

from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.db.models import User, Group, Media, Pokak
from internal.dto.dto import StatisticFilterDTO, StatisticResponseDTO, UserStatInfoDTO


class IUserRepo(Protocol):
    async def get_by_group_and_user_id(self, session: AsyncSession, user_id: str, group: Group) -> User | None: ...

    async def insert(self, session: AsyncSession, user: User) -> User | None: ...

    async def update(self, session: AsyncSession, user: User) -> User | None: ...


class IGroupRepo(Protocol):
    async def get_by_chat_id(self, session: AsyncSession, group_id: str) -> Group | None: ...

    async def insert(self, session: AsyncSession, group: Group) -> Group | None: ...

    async def update(self, session: AsyncSession, group: Group) -> Group | None: ...


class IStatisticsRepo(Protocol):
    async def statistics(self, session: AsyncSession, group: Group, f: StatisticFilterDTO) -> List[UserStatInfoDTO]: ...


class IMediaRepo(Protocol):
    async def get_by_group(self, session: AsyncSession, group: Group) -> Media | None: ...

    async def insert(self, session: AsyncSession, media: Media) -> Media: ...

    async def update(self, session: AsyncSession, media: Media) -> Media: ...


class IPokakRepo(Protocol):
    async def insert(self, session: AsyncSession, pokak: Pokak) -> Pokak: ...


class IUOW(Protocol):
    def with_tx(self, session: AsyncSession) -> AsyncContextManager[None]: ...

    def readonly(self, session: AsyncSession) -> AsyncContextManager[None]: ...
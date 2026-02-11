from typing import Protocol, List
from datetime import datetime as dt

from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.db.models import Media, Group, User
from dummy_bot.db.schemas import PokakStatDTO


class IGroupRepo(Protocol):
    async def get_or_create(self, session: AsyncSession, group_id: str) -> Group:
        ...

    async def get(self, session: AsyncSession, group_id: str) -> Group|None:
        ...

    async def create(self, session: AsyncSession, group_id: str) -> Group:
        ...


class IUserRepo(Protocol):
    async def get(self, session: AsyncSession, group: Group, chat_id: str) -> User|None:
        ...

    async def create(self, session: AsyncSession, group: Group, chat_id: str, username: str, fullname: str) -> User:
        ...

    async def update(self, session: AsyncSession, user: User) -> User:
        ...

    # async def delete(self, session: AsyncSession, user: User) -> bool:
    #     ...


class IMediaRepo(Protocol):
    async def get(self, session: AsyncSession, group: Group) -> Media|None:
        ...

    async def create(self,session: AsyncSession, group: Group, media_unique_id: str) -> Media:
        ...

    async def update(self, session: AsyncSession, media: Media) -> bool:
        ...


class IPokakRepo(Protocol):
    async def add(self, session: AsyncSession, user: User) -> bool:
        ...

    async def group_stat_by_period(self, session: AsyncSession, group: Group, start: dt, end: dt) -> List[PokakStatDTO]:
        ...


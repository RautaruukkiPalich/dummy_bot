from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.internal.models.models import Media, Group


class MediaRepository:

    async def get_by_group(self, session: AsyncSession, group: Group) -> Media|None:
        stmt = select(
            Media
        ).where(
            Media.group_id == group.id
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def insert(self, session: AsyncSession, media: Media) -> Media:
        session.add(media)
        await session.flush()
        await session.refresh(media)
        return media

    async def update(self, session: AsyncSession, media: Media) -> Media:
        media = await session.merge(media)
        await session.flush()
        await session.refresh(media)
        return media

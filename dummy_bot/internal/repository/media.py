from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.internal.models.models import Media, Group


class MediaRepository:

    @staticmethod
    async def get_by_group(session: AsyncSession, group: Group) -> Media|None:
        stmt = select(
            Media
        ).where(
            Media.group_id == group.id
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, session: AsyncSession, media: Media) -> Media:
        if media.id:
            return await self.update(session, media)
        return await self.insert(session, media)

    @staticmethod
    async def insert(session: AsyncSession, media: Media) -> Media:
        session.add(media)
        await session.flush()
        await session.refresh(media)
        return media

    @staticmethod
    async def update(session: AsyncSession, media: Media) -> Media:
        media = await session.merge(media)
        await session.flush()
        await session.refresh(media)
        return media

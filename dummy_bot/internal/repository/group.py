from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.internal.models.models import Group


class GroupRepository:

    @staticmethod
    async def get_by_chat_id(session: AsyncSession, chat_id: int) -> Group|None:
        stmt = select(Group).where(Group.group_id == chat_id)

        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def save(self, session: AsyncSession, group: Group) -> Group:
        if group.id:
            return await self.update(session, group)
        return await self.insert(session, group)

    @staticmethod
    async def insert(session: AsyncSession, group: Group) -> Group:
        session.add(group)
        await session.flush()
        await session.refresh(group)
        return group

    @staticmethod
    async def update(session: AsyncSession, group: Group) -> Group:
        group = await session.merge(group)
        await session.flush()
        await session.refresh(group)
        return group

    @staticmethod
    async def delete(session: AsyncSession, group: Group) -> None:
        stmt = delete(Group).where(Group.id == group.id)

        await session.execute(stmt)
        await session.flush()


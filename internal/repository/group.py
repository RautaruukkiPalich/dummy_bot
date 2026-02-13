from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.db.models import Group


class GroupRepository:

    async def get(self, session: AsyncSession, group_id: str) -> Group|None:
        stmt = select(Group).where(Group.group_id == group_id)

        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def insert(self, session: AsyncSession, group: Group) -> Group|None:
        session.add(group)
        await session.flush()
        await session.refresh(group)
        return group

    async def update(self, session: AsyncSession, group: Group) -> Group|None:
        stmt = update(Group).where(Group.id == group.id)

        await session.execute(stmt)
        await session.flush()
        await session.refresh(group)
        return group

    async def delete(self, session: AsyncSession, group: Group) -> None:
        stmt = delete(Group).where(Group.id == group.id)

        await session.execute(stmt)
        await session.flush()


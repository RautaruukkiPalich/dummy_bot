from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.internal.models.models import User, Group


class UserRepository:

    @staticmethod
    async def get_by_group_and_user_chat_id(session: AsyncSession, user_chat_id: int, group: Group) -> User | None:
        stmt = select(User).where(
            and_(
                User.chat_id == user_chat_id,
                User.group_id == group.id
            )
        )

        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def save(self, session: AsyncSession, user: User) -> User:
        if user.id:
            return await self.update(session, user)
        return await self.insert(session, user)

    @staticmethod
    async def insert(session: AsyncSession, user: User) -> User:
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    @staticmethod
    async def update(session: AsyncSession, user: User) -> User:
        user = await session.merge(user)
        await session.flush()
        await session.refresh(user)
        return user

    @staticmethod
    async def delete(session: AsyncSession, user: User) -> None:
        stmt = delete(User).where(User.id == user.id)

        await session.execute(stmt)
        await session.flush()

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

    @staticmethod
    async def insert(session: AsyncSession, user: User) -> User|None:
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    @staticmethod
    async def update(session: AsyncSession, user: User) -> User|None:
        user = await session.merge(user)
        await session.flush()
        await session.refresh(user)
        return user

    @staticmethod
    async def delete(session: AsyncSession, user: User) -> None:
        stmt = delete(User).where(User.id == user.id)

        await session.execute(stmt)
        await session.flush()

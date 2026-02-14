from sqlalchemy import select, and_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.db.models import User, Group


class UserRepository:

    async def get_by_group_and_user_id(self, session: AsyncSession, user_id: str, group: Group) -> User | None:
        stmt = select(User).where(
            and_(
                User.chat_id == user_id,
                User.group_id == group.id
            )
        )

        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def insert(self, session: AsyncSession, user: User) -> User|None:
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    async def update(self, session: AsyncSession, user: User) -> User|None:
        stmt = update(User).where(User.id == user.id)

        await session.execute(stmt)
        await session.flush()
        await session.refresh(user)
        return user

    async def delete(self, session: AsyncSession, user: User) -> None:
        stmt = delete(User).where(User.id == user.id)

        await session.execute(stmt)
        await session.flush()

from typing import List

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime as dt

from dummy_bot.db.models import Group, User, Media, Pokak
from dummy_bot.db.schemas import PokakStatDTO


class GroupRepo:

    async def get_or_create(self, session: AsyncSession, group_id: str) -> Group:
        if group := await self.get(session, group_id):
            return group
        return await self.create(session, group_id)

    async def get(self, session: AsyncSession, group_id: str) -> Group:
        group = await session.execute(
            select(
                Group
            ).filter(
                Group.group_id == group_id
            )
        )
        return group.scalar_one_or_none()

    async def create(self, session: AsyncSession, group_id: str) -> Group:
        group = Group(
            group_id=group_id
        )
        session.add(group)
        # await session.commit()  # transaction in service
        await session.flush()
        await session.refresh(group)
        return group


class UserRepo:
    async def get(self, session: AsyncSession, group: Group, chat_id: str) -> User | None:
        user = await session.execute(
            select(
                User
            ).where(
                and_(
                    User.group_id == group.id,
                    User.chat_id == chat_id,
                )
            )
        )
        return user.scalar_one_or_none()

    async def create(self, session: AsyncSession, group: Group, chat_id: str, username: str, fullname: str) -> User:
        user = User(
            group_id=group.id,
            chat_id=chat_id,
            username=username,
            fullname=fullname,
            is_active=True,
        )
        session.add(user)
        # await session.commit()
        await session.flush()
        await session.refresh(user)
        return user

    async def update(self, session: AsyncSession, user: User) -> User:
        stmt = update(
            User
        ).where(
            User.id == user.id
        )

        await session.execute(stmt)
        await session.flush()
        await session.refresh(user)
        return user

    # async def delete(self, session: AsyncSession, user: User) -> bool:
    #     stmt = update(
    #         User
    #     ).where(
    #         and_(
    #             User.id == user.id,
    #         )
    #     ).values(
    #         is_active=False
    #     )
    #
    #     res = await session.execute(stmt)
    #     # await session.commit()
    #     await session.flush()
    #     return res.rowcount > 0


class MediaRepo:
    async def get(self, session: AsyncSession, group: Group) -> Media | None:
        media = await session.execute(
            select(
                Media
            ).filter(
                Media.group_id == group.id
            )
        )
        return media.scalar_one_or_none()

    async def create(self, session: AsyncSession, group: Group, media_unique_id: str) -> Media:
        media = Media(
            group_id=group.id,
            media_unique_id=media_unique_id,
        )
        session.add(media)
        # await session.commit()
        await session.flush()
        await session.refresh(media)
        return media

    async def update(self, session: AsyncSession, media: Media) -> bool:
        stmt = update(
            Media
        ).where(
            Media.id == media.id,
        )

        res = await session.execute(stmt)
        # await session.commit()
        await session.flush()
        return res.rowcount > 0


class PokakRepo:
    async def add(self, session: AsyncSession, user: User) -> bool:
        pokak = Pokak(
            user_id=user.id,
        )
        session.add(pokak)
        # await session.commit()
        await session.flush()
        return True

    async def group_stat_by_period(self, session: AsyncSession, group: Group, start: dt, end: dt) -> List[PokakStatDTO]:
        stmt = select(
            Pokak
        ).join(
            User
        ).options(
            selectinload(Pokak.user)
        ).filter(
            and_(
                User.group_id == group.id,
                User.is_active.is_(True),
                Pokak.created_at >= start,
                Pokak.created_at <= end,
            )
        )

        res = await session.execute(stmt)
        rows = res.scalars().all()
        return [PokakStatDTO.model_validate(row, from_attributes=True) for row in rows]

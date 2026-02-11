from typing import List

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime as dt

from dummy_bot.db.models import Group, User, Media, Pokak
from dummy_bot.db.schemas import PokakStatDTO


class GroupRepo:

    @staticmethod
    async def get_or_create(session: AsyncSession, group_id: str) -> Group:
        if group := await GroupRepo.get(session, group_id):
            return group
        return await GroupRepo.create(session, group_id)

    @staticmethod
    async def get(session: AsyncSession, group_id: str) -> Group:
        group = await session.execute(
            select(
                Group
            ).filter(
                Group.group_id == group_id
            )
        )
        return group.scalars().first()

    @staticmethod
    async def create(session: AsyncSession, group_id: str) -> Group:
        group = Group(
            group_id=group_id
        )
        session.add(group)
        await session.commit() # transaction in service
        await session.refresh(group)
        return group


class UserRepo:
    @staticmethod
    async def get(session: AsyncSession, group: Group, chat_id: str) -> User|None:
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

    @staticmethod
    async def create(session: AsyncSession, group: Group, chat_id: str, username: str, fullname: str) -> User:
        user = User(
            group_id=group.id,
            chat_id=chat_id,
            username=username,
            fullname=fullname,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def update(session: AsyncSession, user: User) -> User|None:
        stmt = update(
            User
        ).where(
            User.id == user.id
        ).returning(User)

        res = await session.execute(stmt)
        await session.commit()
        return res.scalar_one_or_none()

    @staticmethod
    async def delete(session: AsyncSession, user: User) -> bool:
        stmt = update(
            User
        ).where(
            and_(
                User.id == user.id,
            )
        ).values(
            is_active=False
        )

        res = await session.execute(stmt)
        await session.commit()
        await session.flush()
        return res.rowcount > 0


class MediaRepo:
    @staticmethod
    async def get(session: AsyncSession, group: Group) -> Media|None:
        media = await session.execute(
            select(
                Media
            ).filter(
                Media.group_id == group.id
            )
        )
        return media.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, group: Group, media_unique_id: str) -> Media:
        media = Media(
            group_id=group.id,
            media_unique_id=media_unique_id,
        )
        session.add(media)
        await session.commit()
        await session.refresh(media)
        return media

    @staticmethod
    async def update(session: AsyncSession, media: Media) -> bool:
        stmt = update(
                Media
            ).where(
                Media.id == media.id,
            )

        res = await session.execute(stmt)
        await session.flush()
        await session.commit()
        return res.rowcount > 0


class PokakRepo:
    @staticmethod
    async def add(session: AsyncSession, user: User) -> bool:
        pokak = Pokak(
            user_id=user.id,
        )
        session.add(pokak)
        await session.commit()
        return True

    @staticmethod
    async def group_stat_by_period(session: AsyncSession, group: Group, start: dt, end: dt) -> List[PokakStatDTO]:
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


    # await session.commit()
    # return await UserRepo.get(session, group, chat_id)

    # @staticmethod
    # async def create_or_update(session: AsyncSession, group: Group, chat_id: str, username: str, fullname: str) -> User:
    #     if user := await UserRepo.get(session, group, chat_id):
    #         return await UserRepo.update(session, user, username, fullname)
    #     return await UserRepo.create(session, group, chat_id, username, fullname)



# async def get_user(group: Group, chat_id: str, session: AsyncSession):
#     user = await session.execute(
#         select(
#             User
#         ).filter(
#             and_(
#                 User.group_id == group.id,
#                 User.chat_id == chat_id,
#             )
#         )
#     )
#     return user.scalars().first()


# async def create_user(group: Group, chat_id: str, username: str, fullname: str, session: AsyncSession):
#     user = User(
#         group_id=group.id,
#         chat_id=chat_id,
#         username=username,
#         fullname=fullname,
#         is_active=True,
#     )
#     session.add(user)
#     await session.commit()
#     await session.refresh(user)
#     return user


# async def update_user(user: User, username: str, fullname: str, session: AsyncSession):
#     await session.execute(
#         update(
#             User
#         ).where(
#             User.id == user.id,
#         ).values(
#             username=username,
#             fullname=fullname,
#             is_active=True,
#         )
#     )
#     await session.commit()
#
#     user = await get_user(user.group, user.chat_id, session)
#     return user


# async def create_or_update_user(group_id: str, chat_id: str, username: str, fullname: str, session: AsyncSession):
#     group = await get_or_create_group(group_id, session)
#     if user := await get_user(group, chat_id, session):
#         return await update_user(user, username, fullname, session)
#     return await create_user(group, chat_id, username, fullname, session)


# async def delete_user(group_id: str, chat_id: str, session: AsyncSession):
#     group = await get_or_create_group(group_id, session)
#     user = await get_user(group, chat_id, session)
#
#     if not user:
#         return
#
#     await session.execute(
#         update(
#             User
#         ).where(
#             and_(
#                 User.group_id == group.id,
#                 User.chat_id == chat_id,
#             )
#         ).values(
#             is_active=False
#         )
#     )
#     await session.commit()
#
#     user = await get_user(group, chat_id, session)
#     return user

# async def get_media(group: Group, session: AsyncSession):
#     media = await session.execute(
#         select(
#             Media
#         ).filter(
#             Media.group_id == group.id
#         )
#     )
#     return media.scalars().first()


# async def create_media(group: Group, new_media: str, session):
#     media = Media(
#         group_id=group.id,
#         media_unique_id=new_media,
#     )
#     session.add(media)
#     await session.commit()
#     await session.refresh(media)
#     return media

#
# async def update_media(media: Media, new_media: str, session: AsyncSession):
#     await session.execute(
#         update(
#             Media
#         ).where(
#             Media.group_id == media.id,
#         ).values(
#             media_unique_id=new_media,
#         )
#     )
#     await session.commit()


# async def create_or_update_media(group_id: str, new_media: str, session: AsyncSession):
#     group = await get_or_create_group(group_id, session)
#     if media := await get_media(group, session):
#         return await update_media(media, new_media, session)
#     return await create_media(group, new_media, session)

# async def create_pokak(user: User, session: AsyncSession):
#     pokak = Pokak(
#         user_id=user.id,
#     )
#     session.add(pokak)
#     await session.commit()
#     await session.refresh(pokak)
#     return pokak


# async def get_pokak_stat(group_id: str, start: dt, end: dt, session: AsyncSession) -> List[PokakStatDTO]:
#     group = await get_or_create_group(group_id, session)
#     stmt = (
#         select(
#             Pokak
#         )
#         .select_from(Pokak)
#         .join(User)
#         .options(selectinload(Pokak.user))
#         .filter(
#             and_(
#                 Pokak.created_at < end,
#                 Pokak.created_at > start,
#                 User.group_id == group.id,
#                 User.is_active.is_(True),
#             )
#         )
#     )
#     # print(stmt.compile(compile_kwargs={"literal_binds": True}))
#     pokaks = await session.execute(stmt)
#     result = pokaks.scalars().all()
#     return [PokakStatDTO.model_validate(row, from_attributes=True) for row in result]

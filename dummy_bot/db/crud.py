from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.db.models import Group, User, Media, Pokak


async def get_group(group_id: str, session: AsyncSession):
    group = await session.execute(
        select(
            Group
        ).filter(
            Group.group_id == group_id
        )
    )
    return group.scalars().first()


async def create_group(group_id: str, session: AsyncSession):
    group = Group(
        group_id=group_id
    )
    session.add(group)
    await session.commit()
    await session.refresh(group)
    return group


async def get_or_create_group(group_id: str, session: AsyncSession):
    if group := await get_group(group_id, session):
        return group
    return await create_group(group_id, session)


async def get_user(group: Group, chat_id: str, session: AsyncSession):
    user = await session.execute(
        select(
            User
        ).filter(
            User.group_id == group.id,
            User.chat_id == chat_id,
        )
    )
    return user.scalars().first()


async def create_user(group: Group, chat_id: str, username: str, fullname: str, session: AsyncSession):
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


async def update_user(user: User, username: str, fullname: str, session: AsyncSession):
    await session.execute(
        update(
            User
        ).where(
            User.id == user.id,
        ).values(
            username=username,
            fullname=fullname,
            is_active=True,
        )
    )
    await session.commit()

    user = await get_user(user.group, user.chat_id, session)
    return user


async def create_or_update_user(group_id: str, chat_id: str, username: str, fullname: str, session: AsyncSession):
    group = await get_or_create_group(group_id, session)
    if user := await get_user(group, chat_id, session):
        return await update_user(user, username, fullname, session)
    return await create_user(group, chat_id, username, fullname, session)


async def delete_user(group_id: str, chat_id: str, session: AsyncSession):
    group = await get_or_create_group(group_id, session)
    user = await get_user(group, chat_id, session)

    if not user:
        return

    await session.execute(
        update(
            User
        ).where(
            User.group_id == group.id,
            User.chat_id == chat_id,
        ).values(
            is_active=False
        )
    )
    await session.commit()

    user = await get_user(group, chat_id, session)
    return user


async def get_media_by_group_id(group_id: str, session: AsyncSession):
    group = await get_or_create_group(group_id, session)
    media = await session.execute(
        select(
            Media
        ).filter(
            Media.group_id == group.id
        )
    )
    return media.scalars().first()


async def get_media(group: Group, session: AsyncSession):
    media = await session.execute(
        select(
            Media
        ).filter(
            Media.group_id == group.id
        )
    )
    return media.scalars().first()


async def create_media(group: Group, new_media: str, session):
    media = Media(
        group_id=group.id,
        media_unique_id=new_media,
    )
    session.add(media)
    await session.commit()
    await session.refresh(media)
    return media


async def update_media(media: Media, new_media: str, session: AsyncSession):
    await session.execute(
        update(
            Media
        ).where(
            Media.group_id == media.id,
        ).values(
            media_unique_id=new_media,
        )
    )
    await session.commit()


async def create_or_update_media(group_id: str, new_media: str, session: AsyncSession):
    group = await get_or_create_group(group_id, session)
    if media := await get_media(group, session):
        return await update_media(media, new_media, session)
    return await create_media(group, new_media, session)


async def create_pokak(user: User, session: AsyncSession):
    pokak = Pokak(
        user_id=user.id,
    )
    session.add(pokak)
    await session.commit()
    await session.refresh(pokak)
    return pokak

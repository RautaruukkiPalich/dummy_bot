from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from internal.models.models import Media
from internal.usecase.interfaces import IGroupRepo, IUOW, IMediaRepo


class MediaUseCase:
    def __init__(
            self,
            group_repo: IGroupRepo,
            media_repo: IMediaRepo,
            uow: IUOW,
    ) -> None:
        self._group_repo: IGroupRepo = group_repo
        self._media_repo: IMediaRepo = media_repo
        self._uow: IUOW = uow

    async def set_media(self, message: Message, session: AsyncSession, file_unique_id: str) -> None:
        async with self._uow.with_tx(session):
            group = await self._group_repo.get_by_chat_id(session, str(message.chat.id))
            if not group: raise

            media = await self._media_repo.get_by_group(session, group)
            if not media:
                await self._insert_media(session, Media(group_id=group.id, media_unique_id=file_unique_id))
                return

            media.media_unique_id = file_unique_id
            await self._update_media(session, media)

    async def _insert_media(self, session: AsyncSession, media: Media) -> None:
        await self._media_repo.insert(session, media)

    async def _update_media(self, session: AsyncSession, media: Media) -> None:
        await self._media_repo.update(session, media)

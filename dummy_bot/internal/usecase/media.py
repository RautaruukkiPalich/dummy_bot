from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.internal.dto.dto import TelegramMessageDTO
from dummy_bot.internal.models.models import Media
from dummy_bot.internal.usecase.interfaces import IGroupRepo, IUOW, IMediaRepo


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

    async def set_media(self, session: AsyncSession, dto: TelegramMessageDTO) -> None:
        async with self._uow.with_tx(session):
            if not dto.media_file_unique_id: raise

            group = await self._group_repo.get_by_chat_id(session, str(dto.chat_id))
            if not group: raise

            media = await self._media_repo.get_by_group(session, group)
            if not media:
                await self._insert_media(session, Media(group_id=group.id, media_unique_id=dto.media_file_unique_id))
                return

            media.media_unique_id = dto.media_file_unique_id
            await self._update_media(session, media)

    async def _insert_media(self, session: AsyncSession, media: Media) -> None:
        await self._media_repo.insert(session, media)

    async def _update_media(self, session: AsyncSession, media: Media) -> None:
        await self._media_repo.update(session, media)

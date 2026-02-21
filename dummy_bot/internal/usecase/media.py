from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.internal.dto.dto import TelegramMessageDTO
from dummy_bot.internal.models.models import Media, Group
from dummy_bot.internal.usecase.interfaces import IGroupRepo, IMediaRepo, IUOWFactory, T_UOW


class MediaUseCase:
    def __init__(
            self,
            group_repo: IGroupRepo,
            media_repo: IMediaRepo,
            uow_factory: IUOWFactory[T_UOW],
    ) -> None:
        self._group_repo: IGroupRepo = group_repo
        self._media_repo: IMediaRepo = media_repo
        self._uow_factory: IUOWFactory[T_UOW] = uow_factory

    async def set_media(self, dto: TelegramMessageDTO) -> None:
        async with self._uow_factory() as uow:
            async with uow.with_tx() as session:
                if not dto.media_file_unique_id: raise

                group = await self._get_group_strict(session, dto.chat_id)

                media = await self._media_repo.get_by_group(session, group)
                if not media:
                    media = Media(
                        group_id=group.id,
                    )

                media.media_unique_id = dto.media_file_unique_id

                await self._media_repo.save(session, media)


    async def _get_group_strict(self, session: AsyncSession, chat_id: int) -> Group:
        group = await self._group_repo.get_by_chat_id(session, chat_id)
        if not group: raise Exception()
        return group

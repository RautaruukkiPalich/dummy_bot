from dummy_bot.internal.dto.dto import TelegramMessageDTO
from dummy_bot.internal.models.models import Pokak
from dummy_bot.internal.usecase.interfaces import IUserRepo, IGroupRepo, IMediaRepo, IPokakRepo, IUOWFactory, \
    T_UOW


class PokakUseCase:
    def __init__(self,
                 user_repo: IUserRepo,
                 group_repo: IGroupRepo,
                 media_repo: IMediaRepo,
                 pokak_repo: IPokakRepo,
                 uow_factory: IUOWFactory[T_UOW],
                 ) -> None:
        self._user_repo = user_repo
        self._group_repo = group_repo
        self._media_repo = media_repo
        self._pokak_repo = pokak_repo
        self._uow_factory: IUOWFactory[T_UOW] = uow_factory

    async def add(self, dto: TelegramMessageDTO) -> bool:
        async with self._uow_factory() as uow:
            async with uow.with_tx() as session:
                group = await self._group_repo.get_by_chat_id(session, dto.chat_id)
                if not group:
                    return False

                user = await self._user_repo.get_by_group_and_user_chat_id(session, dto.user_chat_id, group)
                if not user or not user.is_active:
                    return False

                media = await self._media_repo.get_by_group(session, group)
                if not media:
                    return False

                uid = dto.media_file_unique_id
                if not uid or uid != media.media_unique_id:
                    return False

                await self._pokak_repo.save(session, Pokak(user_id=user.id))
                return True


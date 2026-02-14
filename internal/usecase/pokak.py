from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.db.models import Pokak
from internal.usecase.interfaces import IUserRepo, IGroupRepo, IMediaRepo, IUOW, IPokakRepo


class PokakUseCase:
    def __init__(self,
                 user_repo: IUserRepo,
                 group_repo: IGroupRepo,
                 media_repo: IMediaRepo,
                 pokak_repo: IPokakRepo,
                 uow: IUOW,
                 ) -> None:
        self._user_repo = user_repo
        self._group_repo = group_repo
        self._media_repo = media_repo
        self._pokak_repo = pokak_repo
        self._uow: IUOW = uow

    async def add(self, message: Message, session: AsyncSession) -> bool:
        async with self._uow.with_tx(session):
            group = await self._group_repo.get_by_chat_id(session, str(message.chat.id))
            if not group:
                return False

            user = await self._user_repo.get_by_group_and_user_id(session, str(message.from_user.id), group)
            if not user or not user.is_active:
                return False

            media = await self._media_repo.get_by_group(session, group)
            if not media:
                return False

            uid = self.__get_file_unique_id(message)
            if not uid or uid != media.media_unique_id:
                return False

            await self._pokak_repo.insert(session, Pokak(user_id=user.id))
            return True


    @staticmethod
    def __get_file_unique_id(message: Message) -> str|None:
        if message.animation:
            return message.animation.file_unique_id
        if message.sticker:
            return message.sticker.file_unique_id
        return None

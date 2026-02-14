from aiogram import Router
from aiogram.types import Message, ReactionTypeEmoji
from sqlalchemy.ext.asyncio import AsyncSession

from internal.presentation.decorators import enriched_logger
from internal.presentation.interfaces import ILogger, IPokakUseCase


class TextRouter:
    def __init__(self,
                 router: Router,
                 logger: ILogger,
                 pokak_use_case: IPokakUseCase,
                 ) -> None:
        self._router = router
        self._logger = logger
        self._pokak_use_case = pokak_use_case
        self._register_router()


    def _register_router(self) -> None:
        class_name = self.__class__.__name__

        @self._router.message()
        @enriched_logger(self._logger, class_name)
        async def handle_text(message: Message, session: AsyncSession):
            if message.animation or message.sticker:
                if await self._pokak_use_case.add(message, session):
                    await message.react([ReactionTypeEmoji(emoji="👌")])
                    return


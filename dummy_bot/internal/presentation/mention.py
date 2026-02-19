from aiogram import Router
from aiogram.types import Message

from dummy_bot.internal.presentation.decorators import enriched_logger
from dummy_bot.internal.presentation.filters import BotMentionFilter
from dummy_bot.internal.presentation.interfaces import ILogger


class MentionRouter:
    def __init__(
            self,
            router: Router,
            logger: ILogger,
    ) -> None:
        self._router = router
        self._logger = logger
        self._register_router()

    def _register_router(self):
        class_name = self.__class__.__name__

        @self._router.message(BotMentionFilter())
        @enriched_logger(self._logger, class_name)
        async def bot_tag(message: Message) -> None:
            ...

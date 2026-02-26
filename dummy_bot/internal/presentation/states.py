from typing import List

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from dummy_bot.internal.dto.dto import TelegramMessageDTO
from dummy_bot.internal.fsm.fsm import SetMedia
from dummy_bot.internal.presentation.decorators import enriched_logger
from dummy_bot.internal.presentation.interfaces import ILogger, IMediaUseCase


class StatesRouter:
    def __init__(
            self,
            router: Router,
            admin_router: Router,
            logger: ILogger,
            media_use_case: IMediaUseCase,

    ):
        self.__router = router
        self.__admin_router = admin_router
        self.__logger = logger
        self.__media_use_case = media_use_case
        self._register_handlers()

    def _register_handlers(self):
        class_name = self.__class__.__name__

        @self.__admin_router.message(SetMedia.get_media)
        @enriched_logger(self.__logger, class_name)
        async def callback_set_media(
                message: Message,
                admins: List[int],
                state: FSMContext,
        ) -> None:
            if not (message.animation or message.sticker):
                return

            if message.from_user.id not in admins:
                return

            dto = TelegramMessageDTO.from_message(message)

            await self.__media_use_case.set_media(dto)

            await state.clear()
            await message.reply(text=f'Успешно: отправляй его, когда покакаешь')


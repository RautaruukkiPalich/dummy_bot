from typing import List

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.internal.fsm.fsm import SetMedia
from dummy_bot.internal.presentation.decorators import enriched_logger
from dummy_bot.internal.presentation.interfaces import ILogger, IMediaUseCase
from dummy_bot.internal.presentation.utils import get_file_unique_id


class StatesRouter:
    def __init__(
            self,
            router: Router,
            logger: ILogger,
            media_use_case: IMediaUseCase,

    ):
        self.__router = router
        self.__logger = logger
        self.__media_use_case = media_use_case
        self._register_handlers()

    def _register_handlers(self):
        class_name = self.__class__.__name__

        @self.__router.message(SetMedia.get_media)
        @enriched_logger(self.__logger, class_name)
        async def callback_set_media(
                message: Message,
                admins: List[int],
                session: AsyncSession,
                state: FSMContext,
        ) -> None:
            if not (message.animation or message.sticker):
                return

            if message.from_user.id not in admins:
                return

            file_unique_id = await get_file_unique_id(message)
            await self.__media_use_case.set_media(message, session, file_unique_id)

            await state.clear()
            await message.reply(text=f'Success: отправляй его, когда покакаешь')


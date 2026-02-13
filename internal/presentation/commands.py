from typing import List

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from internal.presentation.decorators import enriched_logger
from internal.presentation.interfaces import ICommandUseCase, ILogger


class CommandsRouter:
    def __init__(
            self,
            router: Router,
            logger: ILogger,
            start_use_case: ICommandUseCase
    ):
        self.__router = router
        self.__logger = logger
        self.__start_use_case = start_use_case
        self.__register_router()

    def __register_router(self) -> None:
        class_name = self.__class__.__name__

        @self.__router.message(Command(commands=["start"]))
        @enriched_logger(self.__logger, class_name)
        async def start(message: Message, admins: List[int], session: AsyncSession) -> None:
            if message.from_user.id not in admins:
                await message.reply("only admin can use start command")
                return

            await self.__start_use_case.start(message, session)
            await message.reply("welcome")

        @self.__router.message(Command(commands=["join"]))
        @enriched_logger(self.__logger, class_name)
        async def join(message: Message, session: AsyncSession) -> None:
            await self.__start_use_case.join(message, session)
            await message.reply("joined")

        @self.__router.message(Command(commands=["leave"]))
        @enriched_logger(self.__logger, class_name)
        async def leave(message: Message, session: AsyncSession) -> None:
            await self.__start_use_case.leave(message, session)
            await message.reply("bye")

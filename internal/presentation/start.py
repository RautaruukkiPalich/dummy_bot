from typing import List, Protocol

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession


class IStartUseCase(Protocol):
    async def start(self, message: Message, session: AsyncSession): ...

    async def join(self, message: Message, session: AsyncSession): ...

    async def leave(self, message: Message, session: AsyncSession): ...


class ILogger(Protocol):
    def debug(self, message: str, *args, **kwargs) -> None: ...

    def info(self, message: str, *args, **kwargs) -> None: ...

    def warn(self, message: str, *args, **kwargs) -> None: ...

    def error(self, message: str, *args, **kwargs) -> None: ...


class StartRouter:
    def __init__(
            self,
            router: Router,
            logger: ILogger,
            start_use_case: IStartUseCase
    ):
        self.__router = router
        self.__logger = logger
        self.__start_use_case = start_use_case
        self.__register_router()

    def __register_router(self) -> None:

        @self.__router.message(Command(commands=["start"]))
        async def start(message: Message, admins: List[int], session: AsyncSession) -> None:
            if not message.from_user.id in admins:
                await message.reply("only admin can use start command")
                return

            try:
                await self.__start_use_case.start(message, session)
                await message.reply("welcome")
            except Exception as e:
                self.__logger.info(f"Register router exception: {e}")
                raise

        @self.__router.message(Command(commands=["join"]))
        async def join(message: Message, session: AsyncSession) -> None:

            try:
                await self.__start_use_case.join(message, session)
                await message.reply("joined")
            except Exception as e:
                self.__logger.info(f"Register router exception: {e}")
                raise

        @self.__router.message(Command(commands=["leave"]))
        async def leave(message: Message, session: AsyncSession) -> None:

            try:
                await self.__start_use_case.leave(message, session)
                await message.reply("bye")
            except Exception as e:
                self.__logger.info(f"Register router exception: {e}")
                raise

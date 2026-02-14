from typing import List

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from internal.dto.dto import StatisticFilterDTO
from internal.dto.enums import StatisticEnum
from internal.fsm.fsm import SetMedia
from internal.utils.stat_flter import PeriodEnum
from internal.presentation.decorators import enriched_logger
from internal.presentation.interfaces import ICommandUseCase, ILogger, IStatisticsUseCase
from internal.utils.stat_report import ReportStat


class CommandsRouter:
    def __init__(
            self,
            router: Router,
            logger: ILogger,
            start_use_case: ICommandUseCase,
            stat_use_case: IStatisticsUseCase,
    ):
        self.__router = router
        self.__logger = logger
        self.__start_use_case = start_use_case
        self.__stat_use_case = stat_use_case
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

        @self.__router.message(Command(commands=[
            StatisticEnum.WEEK.value,
            StatisticEnum.MONTH.value,
            StatisticEnum.YEAR.value,
            StatisticEnum.ALL.value,
        ]))
        @enriched_logger(self.__logger, class_name)
        async def statistics(message: Message, session: AsyncSession) -> None:
            command = message.text[1:].split("@")[0]
            period = PeriodEnum.from_command(command)

            f = StatisticFilterDTO(*period.get_date_scope())

            stat = await self.__stat_use_case.statistics(message, session, f)
            report = ReportStat(period, stat.data, f.limit).prepare()
            await message.reply(report)

        @self.__router.message(Command(commands=["setpokakmedia"]))
        @enriched_logger(self.__logger, class_name)
        async def set_media(message: Message, admins: List[int], state: FSMContext) -> None:
            if message.from_user.id not in admins:
                await message.reply("only admin can use start command")
                return

            await state.set_state(SetMedia.get_media)

            await message.reply(text=f'Отправь мне гифку или стикер, которая будет обозначать успешный покак')
from typing import List

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from dummy_bot.internal.dto.dto import StatisticFilterDTO, TelegramMessageDTO
from dummy_bot.internal.dto.enums import StatisticEnum
from dummy_bot.internal.fsm.fsm import SetMedia
from dummy_bot.internal.utils.stat_flter import PeriodEnum
from dummy_bot.internal.presentation.decorators import enriched_logger
from dummy_bot.internal.presentation.interfaces import ICommandUseCase, ILogger, IStatisticsUseCase
from dummy_bot.internal.utils.stat_report import ReportStat


class CommandsRouter:
    def __init__(
            self,
            router: Router,
            admin_router: Router,
            logger: ILogger,
            commands_use_case: ICommandUseCase,
            stat_use_case: IStatisticsUseCase,
    ):
        self.__router = router
        self.__admin_router = admin_router
        self.__logger = logger
        self.__commands_use_case = commands_use_case
        self.__stat_use_case = stat_use_case
        self.__register_router()

    def __register_router(self) -> None:
        class_name = self.__class__.__name__

        @self.__admin_router.message(Command(commands=["start"]))
        @enriched_logger(self.__logger, class_name)
        async def start(message: Message, admins: List[int]) -> None:
            if message.from_user.id not in admins:
                await message.reply("только пользователи с ролью администратора могут использовать эту команду")
                return

            dto = TelegramMessageDTO.from_message(message)

            await self.__commands_use_case.start(dto)
            await message.reply("приветствую")

        @self.__router.message(Command(commands=["join"]))
        @enriched_logger(self.__logger, class_name)
        async def join(message: Message) -> None:
            dto = TelegramMessageDTO.from_message(message)
            await self.__commands_use_case.join(dto)
            await message.reply(f"{dto.username or dto.fullname} присоединяется")

        @self.__router.message(Command(commands=["leave"]))
        @enriched_logger(self.__logger, class_name)
        async def leave(message: Message) -> None:
            dto = TelegramMessageDTO.from_message(message)
            await self.__commands_use_case.leave(dto)
            await message.reply(f"{dto.username or dto.fullname} покидает нас")

        @self.__router.message(Command(commands=[
            StatisticEnum.WEEK.value,
            StatisticEnum.MONTH.value,
            StatisticEnum.YEAR.value,
            StatisticEnum.ALL.value,
        ]))
        @enriched_logger(self.__logger, class_name)
        async def statistics(message: Message) -> None:
            dto = TelegramMessageDTO.from_message(message)

            command = dto.text[1:].split("@")[0]
            period = PeriodEnum.from_command(command)

            f = StatisticFilterDTO(*period.get_date_scope())

            stat = await self.__stat_use_case.statistics(dto, f)
            report = ReportStat(period, stat.data, f.limit).prepare()
            await message.reply(report)

        @self.__admin_router.message(Command(commands=["setpokakmedia"]))
        @enriched_logger(self.__logger, class_name)
        async def set_media(message: Message, admins: List[int], state: FSMContext) -> None:
            if message.from_user.id not in admins:
                await message.reply("только пользователи с ролью администратора могут использовать эту команду")
                return

            await state.set_state(SetMedia.get_media)
            await message.reply(text=f'Отправь мне гифку или стикер, которая будет обозначать успешный покак')
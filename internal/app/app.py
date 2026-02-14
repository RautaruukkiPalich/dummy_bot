import logging

from dataclasses import dataclass

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from config.config import AppConfig

from internal.database.postgres.postgres import Postgres
from internal.database.redis.redis import Redis
from internal.database.transactional.uow import UOW
from internal.logger.logger import Logger, ConsoleCustomFormatter
from internal.middleware.admins_mw import AdminsMiddleware
from internal.middleware.session_mw import DBSessionMiddleware
from internal.presentation.commands import CommandsRouter
from internal.presentation.states import StatesRouter
from internal.presentation.text import TextRouter
from internal.repository.group import GroupRepository
from internal.repository.media import MediaRepository
from internal.repository.pokak import PokakRepository
from internal.repository.statistics import StatisticsRepository
from internal.repository.user import UserRepository
from internal.usecase.commands import CommandsUseCase
from internal.usecase.media import MediaUseCase
from internal.usecase.mute import MuteUseCase
from internal.usecase.pokak import PokakUseCase
from internal.usecase.statistics import StatisticsUseCase


class App:
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.logger = None
        self.database = None
        self.cache = None
        self.bot = None
        self.dp = None
        self.router = None
        self.repositories = None
        self.services = None
        self.dispatcher = None

        self._configure()

    def _configure(self):
        self._init_logger()
        self.logger.info("app configuring...")

        self._init_database()
        self._init_cache()
        self._init_bot()
        self._init_router()
        self._init_repositories()
        self._init_uow()
        self._init_usecases()
        self._init_services()
        self._init_dispatcher()

        self.logger.info("app configured successfully")

    def _init_logger(self):
        self.logger = Logger(
            level=logging.INFO,
            formatter=ConsoleCustomFormatter(),
        )

    def _init_bot(self):
        self.bot = Bot(
            token=self.cfg.telegram.get_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

    def _init_database(self):
        self.database = Postgres(cfg=self.cfg.database)

    def _init_cache(self):
        self.cache = Redis(cfg=self.cfg.redis)

    def _init_router(self):
        self.router = Router()

    def _init_repositories(self):
        self.repositories = Repositories(
            group=GroupRepository(),
            user=UserRepository(),
            media=MediaRepository(),
            pokak=PokakRepository(),
            statistics=StatisticsRepository(),
        )

    def _init_uow(self):
        self.uow = UOW()

    def _init_usecases(self):
        self.uc = UseCases(
            commands=CommandsUseCase(
                group_repo=self.repositories.group,
                user_repo=self.repositories.user,
                uow=self.uow,
            ),

            statistics=StatisticsUseCase(
                group_repo=self.repositories.group,
                stat_repo=self.repositories.statistics,
                uow=self.uow,
            ),

            media=MediaUseCase(
                group_repo=self.repositories.group,
                media_repo=self.repositories.media,
                uow=self.uow,
            ),

            pokak=PokakUseCase(
                user_repo=self.repositories.user,
                group_repo=self.repositories.group,
                media_repo=self.repositories.media,
                pokak_repo=self.repositories.pokak,
                uow=self.uow,
            ),
            mute=MuteUseCase(self.logger),
        )

    def _init_services(self):
        self.routers = Routers(
            commands=CommandsRouter(
                router=self.router,
                logger=self.logger,
                commands_use_case=self.uc.commands,
                stat_use_case=self.uc.statistics,
            ),
            states=StatesRouter(
                router=self.router,
                logger=self.logger,
                media_use_case=self.uc.media,
            ),
            text=TextRouter(
                router=self.router,
                logger=self.logger,
                pokak_use_case=self.uc.pokak,
                mute_use_case=self.uc.mute,
            ),
        )

    def _init_dispatcher(self):
        self.dp = Dispatcher()

        self.dp.update.middleware(
            DBSessionMiddleware(session_pool=self.database.get_sessionmaker()),
        )
        self.dp.update.middleware(
            AdminsMiddleware(cache=self.cache),
        )
        self.dp.callback_query.middleware(
            CallbackAnswerMiddleware(),
        )
        self.dp.include_router(self.router)

    async def run(self):
        await self.database.ping()
        await self.cache.ping()
        self.logger.info("start polling...")
        await self.dp.start_polling(self.bot)

    async def shutdown(self):
        await self.dp.shutdown()
        await self.router.shutdown()
        await self.cache.shutdown()
        await self.database.shutdown()


@dataclass
class Repositories:
    group: GroupRepository
    user: UserRepository
    media: MediaRepository
    pokak: PokakRepository
    statistics: StatisticsRepository

@dataclass
class UseCases:
    commands: CommandsUseCase
    statistics: StatisticsUseCase
    media: MediaUseCase
    pokak: PokakUseCase
    mute: MuteUseCase

@dataclass
class Routers:
    commands: CommandsRouter
    states: StatesRouter
    text: TextRouter

import logging

from dataclasses import dataclass

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from dummy_bot.config.config import AppConfig

from dummy_bot.internal.database.postgres.client import PostgresClient
from dummy_bot.internal.database.redis.client import RedisClient
from dummy_bot.internal.database.transactional.uow import UOW
from dummy_bot.internal.logger.logger import Logger, JSONCustomFormatter
from dummy_bot.internal.middleware.admins_mw import AdminsMiddleware
from dummy_bot.internal.middleware.session_mw import DBSessionMiddleware
from dummy_bot.internal.presentation.commands import CommandsRouter
from dummy_bot.internal.presentation.states import StatesRouter
from dummy_bot.internal.presentation.text import TextRouter
from dummy_bot.internal.repository.group import GroupRepository
from dummy_bot.internal.repository.media import MediaRepository
from dummy_bot.internal.repository.pokak import PokakRepository
from dummy_bot.internal.repository.statistics import StatisticsRepository
from dummy_bot.internal.repository.user import UserRepository
from dummy_bot.internal.usecase.commands import CommandsUseCase
from dummy_bot.internal.usecase.media import MediaUseCase
from dummy_bot.internal.usecase.mute import MuteUseCase
from dummy_bot.internal.usecase.pokak import PokakUseCase
from dummy_bot.internal.usecase.statistics import StatisticsUseCase


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
        logging.info("app configuring...")

        self._init_logger()
        self._init_database()
        self._init_cache()
        self._init_bot()
        self._init_router()
        self._init_dispatcher()
        self._init_repositories()
        self._init_uow()
        self._init_use_cases()
        self._init_services()

        logging.info("app configured successfully")

    def _init_logger(self):
        self.logger = Logger(
            level=logging.INFO,
            formatter=JSONCustomFormatter(),
        )

    def _init_bot(self):
        self.bot = Bot(
            token=self.cfg.telegram.get_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

    def _init_database(self):
        self.database = PostgresClient(cfg=self.cfg.database)

    def _init_cache(self):
        self.cache = RedisClient(cfg=self.cfg.redis)

    def _init_router(self):
        self.router = Router()
        self.admin_router = Router()
        self.admin_router.message.middleware(AdminsMiddleware(cache=self.cache))

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

    def _init_use_cases(self):
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
                admin_router=self.admin_router,
                logger=self.logger,
                commands_use_case=self.uc.commands,
                stat_use_case=self.uc.statistics,
            ),
            states=StatesRouter(
                router=self.router,
                admin_router=self.admin_router,
                logger=self.logger,
                media_use_case=self.uc.media,
            ),
            text=TextRouter(
                router=self.router,
                admin_router=self.admin_router,
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

        self.dp.callback_query.middleware(
            CallbackAnswerMiddleware(),
        )

        self.dp.include_router(self.admin_router)
        self.dp.include_router(self.router)

    async def run(self):
        await self.database.ping()
        await self.cache.ping()
        logging.info("start polling...")
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

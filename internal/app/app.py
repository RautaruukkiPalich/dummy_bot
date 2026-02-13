import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from config.config import AppConfig
from dummy_bot.bot.handlers import Service
from dummy_bot.db.crud import GroupRepo, UserRepo, MediaRepo, PokakRepo

from internal.database.postgres.postgres import Postgres
from internal.database.redis.redis import Redis
from internal.database.transactional.uow import UOW
from internal.logger.logger import Logger, ConsoleCustomFormatter
from internal.middleware.admins_mw import AdminsMiddleware
from internal.middleware.session_mw import DBSessionMiddleware
from internal.presentation.commands import CommandsRouter
from internal.repository.group import GroupRepository
from internal.repository.user import UserRepository
from internal.usecase.commands import CommandsUseCase


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
        self._init_database()
        self._init_cache()
        self._init_bot()
        self._init_router()
        self._init_repositories()
        # self._init_services()
        self._init_new_services()
        self._init_dispatcher()

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
            group=GroupRepo(),
            user=UserRepo(),
            media=MediaRepo(),
            pokak=PokakRepo(),
        )

    def _init_services(self):
        Service(
            group_repo=self.repositories.group,
            user_repo=self.repositories.user,
            media_repo=self.repositories.media,
            pokak_repo=self.repositories.pokak,
            rout=self.router,
        )

    def _init_new_services(self):
        urepo2 = UserRepository()
        grepo2 = GroupRepository()

        uow = UOW()

        cmd_uc = CommandsUseCase(
            grepo2,
            urepo2,
            uow,
        )

        CommandsRouter(
            self.router,
            self.logger,
            cmd_uc
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
        await self.dp.start_polling(self.bot)

    async def shutdown(self):
        await self.dp.shutdown()
        await self.router.shutdown()
        await self.cache.shutdown()
        await self.database.shutdown()


class Repositories:
    def __init__(
            self,
            group: GroupRepo,
            user: UserRepo,
            media: MediaRepo,
            pokak: PokakRepo,
    ):
        self.group = group
        self.user = user
        self.media = media
        self.pokak = pokak

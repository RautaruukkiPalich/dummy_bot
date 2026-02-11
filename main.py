import asyncio
import logging
import sys
from aiogram import Dispatcher, Bot, Router
from aiogram.enums import ParseMode
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from config import TOKEN, DB_URL
from dummy_bot.bot.handlers import Service
from dummy_bot.db.crud import GroupRepo, UserRepo, MediaRepo, PokakRepo
from dummy_bot.middlewares.check_admins_middleware import CheckAdminMiddleware
from dummy_bot.middlewares.db_middleware import DBSessionMiddleware


async def main() -> None:
    engine: AsyncEngine = create_async_engine(
        url=DB_URL,
        # echo=True,
    )
    async_session = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autobegin=False,
    )
    bot = Bot(
        token=TOKEN,
        parse_mode=ParseMode.HTML,
    )
    dp = Dispatcher()

    dp.update.middleware(DBSessionMiddleware(session_pool=async_session))
    dp.update.middleware(CheckAdminMiddleware())
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    router = Router()
    group_repository = GroupRepo()
    user_repository = UserRepo()
    media_repository = MediaRepo()
    pokak_repository = PokakRepo()

    Service(
        group_repo=group_repository,
        user_repo=user_repository,
        media_repo=media_repository,
        pokak_repo=pokak_repository,
        rout=router,
    )

    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
    )
    asyncio.run(main())

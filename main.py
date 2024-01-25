import asyncio
import logging
import sys
from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession

from config import TOKEN, DB_URL
from dummy_bot.bot.handlers import router
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
    )
    bot = Bot(
        token=TOKEN,
        parse_mode=ParseMode.HTML,
    )
    dp = Dispatcher()

    dp.update.middleware(DBSessionMiddleware(session_pool=async_session))
    dp.update.middleware(CheckAdminMiddleware())
    dp.callback_query.middleware(CallbackAnswerMiddleware())

    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
    )
    asyncio.run(main())

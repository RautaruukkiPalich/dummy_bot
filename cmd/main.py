import argparse
import asyncio
import logging
import sys
from aiogram import Dispatcher, Bot, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
)

from config.config import get_config
from dummy_bot.bot.handlers import Service
from dummy_bot.db.crud import GroupRepo, UserRepo, MediaRepo, PokakRepo
from internal.database.postgres.postgres import Postgres
from internal.database.redis.redis import Redis
from internal.middleware.session_mw import DBSessionMiddleware


from dummy_bot.middlewares.check_admins_middleware import CheckAdminMiddleware


async def main() -> None:
    print("starting bot...")
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', help='Path to .env file')
    args = parser.parse_args()

    cfg = get_config(args.env)

    db = Postgres(cfg.database)
    cache = Redis(cfg.redis)

    bot = Bot(
        token=cfg.telegram.get_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp.update.middleware(DBSessionMiddleware(session_pool=db.get_sessionmaker()))
    dp.update.middleware(CheckAdminMiddleware(cache=cache))
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

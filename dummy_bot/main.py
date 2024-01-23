import asyncio
import logging
import sys
from aiogram import Dispatcher, Bot
from aiogram.enums import ParseMode
from dummy_bot.bot.config import TOKEN
from dummy_bot.bot.handlers import router


async def main() -> None:
    bot = Bot(
        token=TOKEN,
        parse_mode=ParseMode.HTML,
    )
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
    )
    asyncio.run(main())

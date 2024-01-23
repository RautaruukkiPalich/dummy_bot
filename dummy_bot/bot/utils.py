from aiogram import types

from dummy_bot.bot.models import TelegramUser


async def get_user(message: types.Message) -> TelegramUser:
    return TelegramUser(message)


async def correct_ending(num: int) -> str:
    if 11 < num % 100 < 15:
        return "раз"
    if 1 < num % 10 < 5:
        return "раза"
    return "раз"


async def parse_pair(num: int, pair: tuple) -> str:
    return f'<b>{num}</b>: {pair[0]} - <i>{pair[1]} {await correct_ending(pair[1])}</i>'


async def create_stat(stat: dict, period: str) -> str:
    match period:
        case "year":
            head = "Топ-10 засранцев за текущий год:\n"
        case _:
            head = "Топ-10 засранцев за всё время:\n"

    stat = sorted(stat.items(), key=lambda a: a[1], reverse=True)[:10]
    body = '\n'.join([await parse_pair(num, pair) for num, pair in enumerate(stat, 1)])

    return '\n'.join([head, body])

from typing import List, Tuple
from aiogram.types import User, Message

from datetime import datetime as dt, timedelta

from dummy_bot.db.schemas import PokakStatDTO


async def is_admin(message: Message, admins: List[User]) -> bool:
    if not message.chat.id == message.from_user.id:
        if message.from_user.id not in [x.id for x in admins]:
            return False
    return True


async def get_file_unique_id(message: Message) -> str | None:
    if message.animation:
        return message.animation.file_unique_id
    if message.sticker:
        return message.sticker.file_unique_id
    return None


async def get_start_end_period(period: str) -> Tuple[dt, dt]:
    match period:
        case "all":
            return dt(1970, 1, 1), dt.now()
        case "year":
            year = dt.now().year
            return dt(year, 1, 1), dt(year, 12, 31)
        case "month":
            now = dt.now()
            return now - timedelta(days=30), now
        case "week":
            now = dt.now()
            return now - timedelta(days=7), now


# TODO: await API method setReaction
# async def send_reaction(message: Message):
#     METHOD = 'post'
#     METHOD_NAME = 'sendReaction'
#     MSG_ID = ''
#     REACTION = "👌"
#     query = f"https://api.telegram.org/bot{TOKEN}/{METHOD_NAME}"
#     pass


async def correct_ending(num: int) -> str:
    if 11 < num % 100 < 15:
        return "раз"
    if 1 < num % 10 < 5:
        return "раза"
    return "раз"


async def parse_pair(num: int, pair: tuple) -> str:
    person = pair[1]
    username = person.get("username") if person.get("username") else person.get("fullname")
    return f'<b>{num}</b>: {username} - <i>{person.get("count", 0)} {await correct_ending(person.get("count", 0))}</i>'


async def create_report(data: List[PokakStatDTO], period: str) -> str:
    match period:
        case "week":
            head = "Топ-10 засранцев текущей неделю:\n"
        case "month":
            head = "Топ-10 засранцев текущего месяца:\n"
        case "year":
            head = "Топ-10 засранцев текущего года:\n"
        case _:
            head = "Топ-10 засранцев за всё время:\n"

    stat = {}
    for elem in data:
        if elem.user.id not in stat:
            stat.update({elem.user.id: {
                "count": 0,
                "username": elem.user.username,
                "fullname": elem.user.fullname,
            }})
        stat[elem.user.id]["count"] += 1

    stat = sorted(stat.items(), key=lambda a: a[1]['count'], reverse=True)[:10]
    body = '\n'.join([await parse_pair(num, pair) for num, pair in enumerate(stat, 1)])

    return '\n'.join([head, body])

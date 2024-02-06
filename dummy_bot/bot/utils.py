from typing import List, Tuple
from aiogram.types import Message

from datetime import datetime as dt, timedelta
from calendar import monthrange

from dummy_bot.db.schemas import PokakStatDTO


async def is_admin(message: Message, admins: List[int]) -> bool:
    if not message.chat.id == message.from_user.id:
        if message.from_user.id not in admins:
            return False
    return True


async def get_file_unique_id(message: Message) -> str | None:
    if message.animation:
        return message.animation.file_unique_id
    if message.sticker:
        return message.sticker.file_unique_id
    return None


async def get_start_end_period(period: str) -> Tuple[dt, dt]:
    now = dt.now()

    match period:
        case "all":
            return dt(1970, 1, 1), now

        case "year":
            return dt(now.year, 1, 1), dt(now.year, 12, 31)

        case "month":
            start_month_date = dt(
                year=now.year, month=now.month, day=1,
                hour=0, minute=0, second=0, microsecond=0,
            )
            end_month_date = start_month_date + timedelta(
                days=monthrange(now.year, now.month)[1]
            )
            return start_month_date, end_month_date

        case "week":
            start_week = now - timedelta(now.weekday())
            start_week_date = dt(
                year=start_week.year, month=start_week.month, day=start_week.day,
                hour=0, minute=0, second=0, microsecond=0,
            )
            end_week_date = start_week_date + timedelta(days=7)
            return start_week_date, end_week_date


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
            head = "Топ-10 засранцев текущей недели:\n"
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

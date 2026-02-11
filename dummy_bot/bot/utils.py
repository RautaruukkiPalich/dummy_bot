from calendar import monthrange
from collections import defaultdict
from enum import Enum
from typing import Tuple, List
from datetime import datetime as dt, timedelta

from aiogram.types import Message

from dummy_bot.db.schemas import PokakStatDTO


class CommandStatEnum(Enum):
    WEEK = "pokakstatweek"
    MONTH = "pokakstatmonth"
    YEAR = "pokakstatyear"
    ALL = "pokakstatall"


class PeriodEnum(Enum):
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"

    @classmethod
    def from_string(cls, period: str) -> "PeriodEnum":
        return cls(period)

    @classmethod
    def from_command(cls, command: str) -> "PeriodEnum":
        cmd_map = {
            CommandStatEnum.WEEK.value: cls.WEEK,
            CommandStatEnum.MONTH.value: cls.MONTH,
            CommandStatEnum.YEAR.value: cls.YEAR,
            CommandStatEnum.ALL.value: cls.ALL,
        }

        if command not in cmd_map:
            raise ValueError(f"Unknown command: {command}")
        return cmd_map[command]

    def get_date_scope(self) -> Tuple[dt, dt]:
        now = dt.now()

        match self:
            case PeriodEnum.ALL:
                return dt(1970, 1, 1), now

            case PeriodEnum.YEAR:
                return (dt(now.year, 1, 1),
                        dt(now.year, 12, 31, 23, 59, 59, 999999))

            case PeriodEnum.MONTH:
                start = dt(now.year, now.month, 1)
                _, last_day = monthrange(now.year, now.month)
                end = dt(now.year, now.month, last_day, 23, 59, 59)
                return start, end

            case PeriodEnum.WEEK:
                start_week = now - timedelta(days=now.weekday())
                start = dt(
                    year=start_week.year,
                    month=start_week.month,
                    day=start_week.day,
                )
                end = start + timedelta(days=7)
                return start, end

    def __str__(self) -> str:
        return self.value


class Report:
    def __init__(
            self,
            period: PeriodEnum,
            data: List[PokakStatDTO],
    ) -> None:
        self.period = period
        self.data = data

    def prepare(self) -> str:
        return "\n\n".join([self.__header(), self.__body()])

    def __header(self) -> str:
        match self.period:
            case PeriodEnum.WEEK:
                return "Топ-10 засранцев текущей недели:"
            case PeriodEnum.MONTH:
                return "Топ-10 засранцев текущего месяца:"
            case PeriodEnum.YEAR:
                return "Топ-10 засранцев текущего года:"
            case PeriodEnum.ALL:
                return "Топ-10 засранцев за всё время:"

    def __body(self) -> str:
        stat = defaultdict(lambda: {"count": 0, "username": "", "fullname": ""})
        for elem in self.data:
            user = elem.user
            stat[user.id]["count"] += 1
            stat[user.id]["username"] = user.username or ""
            stat[user.id]["fullname"] = user.fullname or ""

        top10 = sorted(
            stat.items(),
            key=lambda x: x[1]["count"],
            reverse=True,
        )[:10]

        lines = [
            self.__format_line(num, user_id, data)
            for num, (user_id, data) in enumerate(top10, 1)
        ]

        return "\n".join(lines)

    def __format_line(self, num: int, user_id: int, data: dict) -> str:
        username = data.get("username") or data.get("fullname") or f"User {user_id}"
        count = data.get("count", 0)
        ending = self.__get_ending(count)
        return f"<b>{num}</b>: {username} - <i>{count} {ending}</i>"

    @staticmethod
    def __get_ending(num: int) -> str:
        if 11 < num % 100 < 15:
            return "раз"
        if 1 < num % 10 < 5:
            return "раза"
        return "раз"

    def __str__(self) -> str:
        return f"Creating report for {self.period}"


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

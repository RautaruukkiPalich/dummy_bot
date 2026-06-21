from calendar import monthrange
from enum import Enum
from datetime import datetime as dt, timedelta as td
from typing import Tuple

from dummy_bot.internal.dto.enums import StatisticEnum, GraphEnum


class PeriodEnum(Enum):
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"

    @classmethod
    def from_string(cls, period: str) -> "PeriodEnum":
        return cls(period)

    @classmethod
    def from_stat_command(cls, command: str) -> "PeriodEnum":
        cmd_map = {
            StatisticEnum.WEEK.value: cls.WEEK,
            StatisticEnum.MONTH.value: cls.MONTH,
            StatisticEnum.YEAR.value: cls.YEAR,
            StatisticEnum.ALL.value: cls.ALL,
        }

        if command not in cmd_map:
            raise ValueError(f"Unknown stat command: {command}")
        return cmd_map[command]

    @classmethod
    def from_graph_command(cls, command: str) -> "PeriodEnum":
        cmd_map = {
            GraphEnum.WEEK.value: cls.WEEK,
            GraphEnum.MONTH.value: cls.MONTH,
            GraphEnum.YEAR.value: cls.YEAR,
            GraphEnum.ALL.value: cls.ALL,
        }

        if command not in cmd_map:
            raise ValueError(f"Unknown graph command: {command}")
        return cmd_map[command]

    def get_date_scope(self) -> Tuple[dt, dt]:
        now = dt.now()

        match self:
            case PeriodEnum.ALL:
                return dt(2020, 1, 1), now

            case PeriodEnum.YEAR:
                return (dt(now.year, 1, 1),
                        dt(now.year, 12, 31, 23, 59, 59, 999999))

            case PeriodEnum.MONTH:
                start = dt(now.year, now.month, 1)
                _, last_day = monthrange(now.year, now.month)
                end = dt(now.year, now.month, last_day, 23, 59, 59)
                return start, end

            case PeriodEnum.WEEK:
                start_week = now - td(days=now.weekday())
                start = dt(
                    year=start_week.year,
                    month=start_week.month,
                    day=start_week.day,
                )
                end = start + td(days=7)
                return start, end

    def __str__(self) -> str:
        return self.value

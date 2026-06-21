from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional

from aiogram.types import Message
from sqlalchemy import Row


@dataclass
class StatisticFilterDTO:
    start_date: datetime
    end_date: datetime
    limit: int = 10


@dataclass
class UserStatInfoDTO:
    user_id: int
    username: str
    fullname: str
    count: int

    @classmethod
    def from_row(cls, row: Row) -> "UserStatInfoDTO":
        return cls(
            user_id=row.user_id,
            username=row.username,
            fullname=row.fullname,
            count=row.count
        )


@dataclass
class StatisticResponseDTO:
    data: List[UserStatInfoDTO]


@dataclass
class DailyStats:
    """Статистика за один день"""
    date: date
    users: Dict[int, UserStatInfoDTO]  # user_id -> DTO

    @classmethod
    def from_rows(cls, rows: List[Row]) -> Dict[date, 'DailyStats']:
        """{date: DailyStats} из списка Row"""
        result = {}

        for row in rows:
            row_date = row.date if isinstance(row.date, date) else row.date.date()

            if row_date not in result:
                result[row_date] = cls(date=row_date, users={})

            result[row_date].users[row.user_id] = UserStatInfoDTO.from_row(row)

        return result

    def get_top_users(self, n: int = 10) -> list[tuple[int, UserStatInfoDTO]]:
        """Получить топ N пользователей за день"""
        return sorted(
            self.users.items(),
            key=lambda x: x[1].count,
            reverse=True
        )[:n]

    def total_count(self) -> int:
        """Общее количество действий за день"""
        return sum(dto.count for dto in self.users.values())


@dataclass
class PeriodStats:
    daily_stats: Dict[date, DailyStats]

    @classmethod
    def from_rows(cls, rows: List[Row]) -> 'PeriodStats':
        daily_dict: Dict[date, DailyStats] = {}

        for row in rows:
            row_date = row.date if isinstance(row.date, date) else row.date.date()
            if row_date not in daily_dict:
                daily_dict[row_date] = DailyStats(date=row_date, users={})
            daily_dict[row_date].users[row.user_id] = UserStatInfoDTO.from_row(row)

        return cls(daily_stats=daily_dict)

    def fill_zeros(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> None:
        minimal_date = date(2020, 1, 1)
        if start_date is None or start_date < minimal_date:
            start_date = date.today() - timedelta(days=365)

        if end_date is None or end_date > date.today():
            end_date = date.today()

        current = start_date
        while current <= end_date:
            if current not in self.daily_stats:
                self.daily_stats[current] = DailyStats(date=current, users={})
            current = current + timedelta(days=1)

    def get_all_users(self) -> Dict[int, UserStatInfoDTO]:
        """Все пользователи за период с суммарной статистикой"""
        totals = defaultdict(int)
        users_info = {}

        for daily in self.daily_stats.values():
            for user_id, dto in daily.users.items():
                totals[user_id] += dto.count
                if user_id not in users_info:
                    users_info[user_id] = dto

        result = {}
        for user_id, total in totals.items():
            info = users_info[user_id]
            result[user_id] = UserStatInfoDTO(
                user_id=user_id,
                username=info.username,
                fullname=info.fullname,
                count=total
            )

        return result

    def get_top_users(self, n: int = 10) -> List[UserStatInfoDTO]:
        """Топ N пользователей за весь период"""
        all_users = self.get_all_users()
        sorted_users = sorted(all_users.values(), key=lambda x: x.count, reverse=True)
        return sorted_users[:n]

    def get_dates(self) -> List[date]:
        """Все даты в порядке возрастания"""
        return sorted(self.daily_stats.keys())

    def get_user_timeline(self, username: str) -> Dict[date, int]:
        """Активность конкретного пользователя по дням"""
        user_id = None
        for daily in self.daily_stats.values():
            for uid, dto in daily.users.items():
                if dto.username == username:
                    user_id = uid
                    break
            if user_id:
                break

        if not user_id:
            return {}

        # Собираем таймлайн
        timeline = {}
        for date, daily in self.daily_stats.items():
            if user_id in daily.users:
                timeline[date] = daily.users[user_id].count
            else:
                timeline[date] = 0

        return timeline


@dataclass
class MuteResponseDTO:
    delta: timedelta
    delta_str: str
    reason: str | None


@dataclass
class TelegramMessageDTO:
    chat_id: int
    user_chat_id: int
    username: str | None
    fullname: str | None
    text: str | None
    media_file_unique_id: str | None

    @staticmethod
    def from_message(message: Message) -> "TelegramMessageDTO":
        dto = TelegramMessageDTO(
            chat_id=message.chat.id,
            user_chat_id=message.from_user.id,
            username=message.from_user.username,
            fullname=message.from_user.full_name,
            text=message.text,
            media_file_unique_id=None,
        )

        if message.animation:
            dto.media_file_unique_id = message.animation.file_unique_id
        if message.sticker:
            dto.media_file_unique_id = message.sticker.file_unique_id

        return dto

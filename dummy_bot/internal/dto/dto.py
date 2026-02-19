from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List
from aiogram.types import Message


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

@dataclass
class StatisticResponseDTO:
    data: List[UserStatInfoDTO]

@dataclass
class MuteResponseDTO:
    delta: timedelta
    delta_str: str
    reason: str|None

@dataclass
class TelegramMessageDTO:
    chat_id: int
    user_chat_id: int
    username: str|None
    fullname: str|None
    text: str|None
    media_file_unique_id: str|None

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


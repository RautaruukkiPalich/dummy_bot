from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List


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
class MuteRequestDTO:
    text: str

@dataclass
class MuteResponseDTO:
    delta: timedelta
    delta_str: str
    reason: str|None

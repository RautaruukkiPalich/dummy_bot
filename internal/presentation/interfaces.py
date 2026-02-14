from typing import Protocol

from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from internal.dto.dto import StatisticFilterDTO, StatisticResponseDTO


class ICommandUseCase(Protocol):
    async def start(self, message: Message, session: AsyncSession): ...

    async def join(self, message: Message, session: AsyncSession): ...

    async def leave(self, message: Message, session: AsyncSession): ...


class IStatisticsUseCase(Protocol):
    async def statistics(self, message: Message, session: AsyncSession, stat_filter: StatisticFilterDTO) -> StatisticResponseDTO: ...


class IMediaUseCase(Protocol):
    async def set_media(self, message: Message, session: AsyncSession, file_unique_id: str) -> None: ...


class ILogger(Protocol):
    def debug(self, message: str, *args, **kwargs) -> None: ...

    def info(self, message: str, *args, **kwargs) -> None: ...

    def warn(self, message: str, *args, **kwargs) -> None: ...

    def error(self, message: str, *args, **kwargs) -> None: ...

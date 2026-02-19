from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.internal.dto.dto import StatisticFilterDTO, StatisticResponseDTO, MuteResponseDTO, TelegramMessageDTO


class ICommandUseCase(Protocol):
    async def start(self, session: AsyncSession, dto: TelegramMessageDTO): ...

    async def join(self, session: AsyncSession, dto: TelegramMessageDTO): ...

    async def leave(self, session: AsyncSession, dto: TelegramMessageDTO): ...


class IStatisticsUseCase(Protocol):
    async def statistics(self, session: AsyncSession, dto: TelegramMessageDTO, stat_filter: StatisticFilterDTO) -> StatisticResponseDTO: ...


class IMediaUseCase(Protocol):
    async def set_media(self, session: AsyncSession, dto: TelegramMessageDTO) -> None: ...

class IPokakUseCase(Protocol):
    async def add(self, session: AsyncSession, dto: TelegramMessageDTO) -> bool:...

class IMuteUseCase(Protocol):
    async def mute(self, dto: TelegramMessageDTO) -> MuteResponseDTO|None: ...


class ILogger(Protocol):
    def debug(self, message: str, *args, **kwargs) -> None: ...

    def info(self, message: str, *args, **kwargs) -> None: ...

    def warn(self, message: str, *args, **kwargs) -> None: ...

    def error(self, message: str, *args, **kwargs) -> None: ...

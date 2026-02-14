from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from internal.dto.dto import StatisticResponseDTO, StatisticFilterDTO
from internal.usecase.interfaces import ICmdsGroupRepo, IStatisticsRepo, IUOW


class StatisticsUseCase:
    def __init__(
            self,
            group_repo: ICmdsGroupRepo,
            stat_repo: IStatisticsRepo,
            uow: IUOW,
    ) -> None:
        self._group_repo: ICmdsGroupRepo = group_repo
        self._stat_repo: IStatisticsRepo = stat_repo
        self._uow: IUOW = uow

    async def statistics(self, message: Message, session: AsyncSession,
                         stat_filter: StatisticFilterDTO) -> StatisticResponseDTO:

        async with self._uow.readonly(session):
            group = await self._group_repo.get_by_chat_id(session, str(message.chat.id))
            if not group: raise

            res = await self._stat_repo.statistics(session, group, stat_filter)

            return StatisticResponseDTO(res)

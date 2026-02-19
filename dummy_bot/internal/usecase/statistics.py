from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.internal.dto.dto import StatisticResponseDTO, StatisticFilterDTO, TelegramMessageDTO
from dummy_bot.internal.usecase.interfaces import IGroupRepo, IStatisticsRepo, IUOW


class StatisticsUseCase:
    def __init__(
            self,
            group_repo: IGroupRepo,
            stat_repo: IStatisticsRepo,
            uow: IUOW,
    ) -> None:
        self._group_repo: IGroupRepo = group_repo
        self._stat_repo: IStatisticsRepo = stat_repo
        self._uow: IUOW = uow

    async def statistics(self, session: AsyncSession, dto: TelegramMessageDTO,
                         stat_filter: StatisticFilterDTO) -> StatisticResponseDTO:

        async with self._uow.readonly(session):
            group = await self._group_repo.get_by_chat_id(session, str(dto.chat_id))
            if not group: raise

            res = await self._stat_repo.statistics(session, group, stat_filter)

            return StatisticResponseDTO(res)

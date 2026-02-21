from dummy_bot.internal.dto.dto import StatisticResponseDTO, StatisticFilterDTO, TelegramMessageDTO
from dummy_bot.internal.usecase.interfaces import IGroupRepo, IStatisticsRepo, T_UOW, IUOWFactory


class StatisticsUseCase:
    def __init__(
            self,
            group_repo: IGroupRepo,
            stat_repo: IStatisticsRepo,
            uow_factory: IUOWFactory[T_UOW],
    ) -> None:
        self._group_repo: IGroupRepo = group_repo
        self._stat_repo: IStatisticsRepo = stat_repo
        self._uow_factory: IUOWFactory[T_UOW] = uow_factory

    async def statistics(self, dto: TelegramMessageDTO, stat_filter: StatisticFilterDTO) -> StatisticResponseDTO:

        async with self._uow_factory() as uow:
            async with uow.readonly() as session:

                group = await self._group_repo.get_by_chat_id(session, dto.chat_id)
                if not group: raise

                res = await self._stat_repo.statistics(session, group, stat_filter)

                return StatisticResponseDTO(res)

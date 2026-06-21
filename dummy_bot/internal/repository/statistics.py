from typing import List

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.internal.models.models import Group, Pokak, User
from dummy_bot.internal.dto.dto import StatisticFilterDTO, UserStatInfoDTO, PeriodStats


class StatisticsRepository:

    @staticmethod
    async def group_count_stat(session: AsyncSession, group: Group, f: StatisticFilterDTO) -> List[UserStatInfoDTO]:
        stmt = select(
            User.id.label("user_id"),
            User.username,
            User.fullname,
            func.count(Pokak.id).label("count"),
        ).select_from(Pokak).join(
            User, User.id == Pokak.user_id
        ).filter(
            and_(
                User.group_id == group.id,
                User.is_active.is_(True),
                Pokak.created_at.between(f.start_date, f.end_date)
            )
        ).group_by(
            User.id,
        ).order_by(
            func.count(Pokak.id).desc()
        ).limit(
            f.limit
        )

        result = await session.execute(stmt)

        return [UserStatInfoDTO.from_row(row) for row in result.all()]

    @staticmethod
    async def group_daily_count_stat(session: AsyncSession, group: Group, f: StatisticFilterDTO) -> PeriodStats:
        stmt = (select(
            func.date(Pokak.created_at).label("date"),
            User.id.label("user_id"),
            User.username,
            User.fullname,
            func.count(Pokak.id).label("count"),
        ).select_from(Pokak).join(
            User, User.id == Pokak.user_id
        ).filter(
            and_(
                User.group_id == group.id,
                User.is_active.is_(True),
                Pokak.created_at.between(f.start_date, f.end_date)
            )
        ).group_by(
            func.date(Pokak.created_at),
            User.id,
        ).order_by(
            func.date(Pokak.created_at),
            func.count(Pokak.id).desc()
        ))

        result = await session.execute(stmt)

        return PeriodStats.from_rows(rows=list(result.all()))

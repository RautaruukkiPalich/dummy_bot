from typing import List

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from internal.models.models import Group, Pokak, User
from internal.dto.dto import StatisticFilterDTO, UserStatInfoDTO


class StatisticsRepository:

    async def statistics(self, session: AsyncSession, group: Group, f: StatisticFilterDTO) -> List[UserStatInfoDTO]:
        stmt = select(
            User.id,
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

        return [UserStatInfoDTO(*row) for row in result.all()]

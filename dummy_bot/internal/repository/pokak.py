from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.internal.models.models import Pokak


class PokakRepository:

    @staticmethod
    async def insert(session: AsyncSession, pokak: Pokak) -> Pokak:
        session.add(pokak)
        await session.flush()
        await session.refresh(pokak)
        return pokak
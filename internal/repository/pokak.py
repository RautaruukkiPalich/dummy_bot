from sqlalchemy.ext.asyncio import AsyncSession

from internal.models.models import Pokak


class PokakRepository:

    async def insert(self, session: AsyncSession, pokak: Pokak) -> Pokak:
        session.add(pokak)
        await session.flush()
        await session.refresh(pokak)
        return pokak
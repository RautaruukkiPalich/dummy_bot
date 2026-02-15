from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession


class UOW:

    def with_tx(self, session: AsyncSession) -> AsyncContextManager[None]:
        return self._with_tx_impl(session=session)  # вот тут жалуется на ошибку "Parameter 'self' unfilled"

    @asynccontextmanager
    async def _with_tx_impl(self, session: AsyncSession) -> AsyncGenerator[None, None]:
        async with session.begin():
            yield

    def readonly(self, session: AsyncSession) -> AsyncContextManager[None]:
        return self._readonly_impl(session=session)  # вот тут жалуется на ошибку "Parameter 'self' unfilled"

    @asynccontextmanager
    async def _readonly_impl(self, session: AsyncSession) -> AsyncGenerator[None, None]:
        async with session.begin():
            yield
            await session.rollback()

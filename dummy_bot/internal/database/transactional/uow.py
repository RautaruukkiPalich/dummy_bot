from contextlib import asynccontextmanager
from typing import AsyncGenerator, AsyncContextManager

from sqlalchemy.ext.asyncio import AsyncSession


class UOW:

    @classmethod
    def with_tx(cls, session: AsyncSession) -> AsyncContextManager[None]:
        return cls._with_tx_impl(session=session)  # вот тут жалуется на ошибку "Parameter 'self' unfilled"

    @classmethod
    @asynccontextmanager
    async def _with_tx_impl(cls, session: AsyncSession) -> AsyncGenerator[None, None]:
        async with session.begin():
            yield

    @classmethod
    def readonly(cls, session: AsyncSession) -> AsyncContextManager[None]:
        return cls._readonly_impl(session=session)  # вот тут жалуется на ошибку "Parameter 'self' unfilled"

    @classmethod
    @asynccontextmanager
    async def _readonly_impl(cls, session: AsyncSession) -> AsyncGenerator[None, None]:
        async with session.begin():
            yield
            await session.rollback()

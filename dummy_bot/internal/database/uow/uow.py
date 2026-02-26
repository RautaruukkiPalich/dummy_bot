from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator, Callable

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession


class UnitOfWork:
    def __init__(
            self,
            sessionmaker: async_sessionmaker[AsyncSession],
    ):
        self._sessionmaker: async_sessionmaker[AsyncSession] = sessionmaker
        self._session: Optional[AsyncSession] = None

    async def __aenter__(self) -> 'UnitOfWork':
        if not self._session:
            self._session = self._sessionmaker()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
            self._session = None

    @asynccontextmanager
    async def with_tx(self) -> AsyncGenerator[AsyncSession, None]:
        """
        async with uow.with_tx() as session:
            await session.execute(stmt)
        """
        if not self._session:
            raise RuntimeError(
                "Session not created. Use 'async with UnitOfWork(...)' first."
            )
        async with self._session.begin():
            yield self._session

    @asynccontextmanager
    async def readonly(self) -> AsyncGenerator[AsyncSession, None]:
        """
        automatically rollback the session when it closes

        !WARNING: do not create nested transactions in READONLY mode!

        async with uow.readonly() as session:
            await session.execute(stmt)
        """
        if not self._session:
            raise RuntimeError(
                "Session not created. Use 'async with UnitOfWork(...)' first."
            )

        try:
            await self._session.begin()
            yield self._session
        finally:
            if self._session and self._session.in_transaction():
                await self._session.rollback()


class UOWFactory:
    """
    async with uow_factory() as uow:
    """
    def __init__(
            self,
            sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        self._sessionmaker: async_sessionmaker[AsyncSession] = sessionmaker

    def __call__(self, *args, **kwargs) -> UnitOfWork:
        return UnitOfWork(self._sessionmaker)

    @property
    def provider(self) -> Callable[[], UnitOfWork]:
        return self

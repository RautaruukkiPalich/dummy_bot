from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.session import async_sessionmaker, AsyncSession

from dummy_bot.config.config import DatabaseConfig


class PostgresClient:
    def __init__(self, cfg: DatabaseConfig):
        self.__cfg: DatabaseConfig = cfg
        self.__engine: Optional[AsyncEngine] = None
        self.__sessionmaker: Optional[async_sessionmaker] = None
        self.__register_engine()

    @property
    def sessionmaker(self) -> async_sessionmaker:
        if self.__sessionmaker is None:
            self.__sessionmaker = async_sessionmaker(
                bind=self.__engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autobegin=False,
            )
        return self.__sessionmaker

    def __register_engine(self) -> None:
        if self.__engine is None:
            self.__engine = create_async_engine(
                url=self.__cfg.dsn,
                # echo=True,
            )

    async def ping(self):
        async with self.__engine.connect() as conn:
            await conn.execute(text("SELECT 1"))



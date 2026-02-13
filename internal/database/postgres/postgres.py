from typing import Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.session import async_sessionmaker, AsyncSession

from config.config import DatabaseConfig


class Postgres:
    def __init__(self, cfg: DatabaseConfig):
        self.__cfg: DatabaseConfig = cfg
        self.__engine: Optional[AsyncEngine] = None
        self.__sessionmaker: Optional[async_sessionmaker] = None
        self.__register_engine()

    def __register_engine(self) -> AsyncEngine:
        if self.__engine is None:
            self.__engine = create_async_engine(
                url=self.__cfg.dsn,
                # echo=True,
            )
            import asyncio
            asyncio.create_task(self.__ping_database())
        return self.__engine

    async def __ping_database(self):
        try:
            async with self.__engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                await conn.rollback()
        except Exception as e:
            print(f"Database connection failed: {e}")
            raise Exception(f"Database connection failed: {e}")

    def get_sessionmaker(self) -> async_sessionmaker:
        if self.__sessionmaker is None:
            self.__sessionmaker = async_sessionmaker(
                bind=self.__engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autobegin=False,
            )
        return self.__sessionmaker
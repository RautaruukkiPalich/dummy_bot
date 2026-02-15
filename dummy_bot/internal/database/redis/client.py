from typing import Optional

from dummy_bot.config.config import RedisConfig
from redis import Redis


class RedisClient:
    def __init__(self, cfg: RedisConfig):
        self.__config = cfg
        self.__client = None

    @property
    def client(self) -> Redis:
        if self.__client is None:
            self.__client = Redis(**self.__config.connection_kwargs)
        return self.__client

    async def get(self, key: str):
        return self.client.get(
            f"{self.__config.connection_kwargs.get(self.__config.db, 0)}:{key}",
        )

    async def set(self, key: str, value: str, expire: Optional[int] = None):
        return self.client.set(
            f"{self.__config.connection_kwargs.get(self.__config.db, 0)}:{key}",
            value, ex=expire,
        )

    async def ping(self):
        return self.client.ping()

    def close(self):
        if self.__client:
            self.__client.close()
            self.__client = None

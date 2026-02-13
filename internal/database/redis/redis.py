from typing import Optional

from config.config import RedisConfig
import redis.asyncio as r

class Redis:
    def __init__(self, cfg: RedisConfig):
        self.__config = cfg
        self.__client = None

    @property
    def client(self) -> r.Redis:
        if self.__client is None:
            self.__client = r.Redis(**self.__config.connection_kwargs)
        return self.__client

    async def get(self, key: str):
        return await self.client.get(f"{self.__config.connection_kwargs.get('db', 0)}:{key}")

    async def set(self, key: str, value: str, expire: Optional[int] = None):
        return await self.client.set(f"{self.__config.connection_kwargs.get('db', 0)}:{key}", value, ex=expire)

    async def ping(self):
        return await self.client.ping()

    def close(self):
        if self.__client:
            self.__client.close()
            self.__client = None

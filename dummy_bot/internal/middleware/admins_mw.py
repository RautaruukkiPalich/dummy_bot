from functools import wraps
from typing import Callable, Dict, Any, Awaitable, List, Protocol, Optional

from aiogram import BaseMiddleware, Bot
from aiogram.types import Message


class ICache(Protocol):
    async def get(self, key: str):
        ...

    async def set(self, key: str, value: str, expire: Optional[int] = None):
        ...


class AdminsMiddleware(BaseMiddleware):
    def __init__(self, cache: ICache):
        self.__cache = cache

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        chat_id = event.chat.id
        bot = data["bot"]
        bot2 = data.get("bot")

        if event.from_user.id == chat_id:
            data["admins"] = [chat_id, ]
        else:
            data["admins"] = await self._get_chat_administrators(bot, chat_id)

        return await handler(event, data)

    @staticmethod
    def _cache_admins(ttl: int = 60):
        def decorator(fn):
            @wraps(fn)
            async def wrapper(self, *args, **kwargs):
                bot, chat_id = args

                try:
                    return await self._get_admins_from_cache(str(chat_id))
                except Exception as e:
                    print(f"failed get from cache: {e.__repr__()}")

                admins = await fn(self, *args)

                try:
                    await self._set_admins_to_cache(str(chat_id), admins, ttl)
                except Exception as e:
                    print(f"failed set to cache: {e.__repr__()}")

                return admins
            return wrapper
        return decorator

    @_cache_admins(ttl=40)
    async def _get_chat_administrators(self, bot: Bot, chat_id: int) -> List[int]:
        return [
            admin.user.id for admin
            in await bot.get_chat_administrators(chat_id)
            if not admin.user.is_bot
        ]

    async def _get_admins_from_cache(self, key: str) -> List[int]:
        admins = await self.__cache.get(key)
        return [int(admin) for admin in str(admins).split(";")]

    async def _set_admins_to_cache(self, key: str, data: List[int], ttl: int = 10) -> None:
        await self.__cache.set(
            key=key,
            value=';'.join(list(map(str, data))),
            expire=ttl,
        )
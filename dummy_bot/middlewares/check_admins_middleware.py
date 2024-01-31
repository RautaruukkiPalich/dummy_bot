from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware, Bot
from aiogram.types import Message
from dummy_bot.db.redis import r as redis


def cache_admins(ttl: int = 60):
    def cache(fn):
        async def wrapper(*args):
            chat_id = args[1]
            admins = await redis.get(str(chat_id))
            if not admins:
                await redis.set(
                    name=str(chat_id),
                    value=await fn(bot=args[0], chat_id=chat_id,),
                    ex=ttl,
                )
                admins = await redis.get(str(chat_id))
            return admins
        return wrapper
    return cache


class CheckAdminMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        chat_id = data["event_chat"].id
        if data["event_from_user"].id == chat_id:
            data["admins"] = [chat_id, ]
        else:
            admins = (await self.get_administrators(data["bot"], chat_id)).decode('utf-8')
            data["admins"] = [int(x) for x in admins.split(';')]
        return await handler(event, data)

    @staticmethod
    @cache_admins(ttl=20)
    async def get_administrators(bot: Bot, chat_id: int):
        return ';'.join([
            str(admin.user.id) for admin
            in await bot.get_chat_administrators(chat_id)
            if not admin.user.is_bot
        ])


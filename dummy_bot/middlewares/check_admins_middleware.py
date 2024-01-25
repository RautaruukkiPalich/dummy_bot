from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Message


class CheckAdminMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        data["admins"] = [
            x.user for x in await data["bot"].get_chat_administrators(data["event_chat"].id)
            if not x.user.is_bot
        ]
        return await handler(event, data)

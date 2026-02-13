# from functools import wraps
# from typing import Callable, Awaitable, Dict, Any, Protocol, Optional, List
#
# from aiogram import BaseMiddleware, Bot
# from aiogram.types import Message
#
#
# class ICache(Protocol):
#     async def get(self, key: str):
#         ...
#
#     async def set(self, key: str, value: str, expire: Optional[int] = None):
#         ...
#
#
# class CheckAdminMiddleware(BaseMiddleware):
#     def __init__(self, cache: ICache):
#         self.__cache = cache
#
#     async def __call__(
#             self,
#             handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
#             event: Message,
#             data: Dict[str, Any]
#     ) -> Any:
#         chat_id = data["event_chat"].id
#         bot = data["bot"]
#
#         if data["event_from_user"].id == chat_id:
#             data["admins"] = [chat_id, ]
#         else:
#             data["admins"] = await self.get_chat_administrators(bot, chat_id)
#
#         return await handler(event, data)
#
#     @staticmethod
#     def cache_admins(ttl: int = 60):
#         def decorator(fn):
#             @wraps(fn)
#             async def wrapper(self, *args, **kwargs):
#                 bot, chat_id = args
#                 admins = await self.__cache.get(str(chat_id))
#                 if admins:
#                     return [int(admin) for admin in str(admins).split(";")]
#
#                 admins = await fn(self, *args)
#
#                 await self.__cache.set(
#                     key=str(chat_id),
#                     value=';'.join(list(map(str, admins))),
#                     expire=ttl,
#                 )
#                 return admins
#             return wrapper
#         return decorator
#
#     @cache_admins(ttl=40)
#     async def get_chat_administrators(self, bot: Bot, chat_id: int) -> List[int]:
#         return [
#             admin.user.id for admin
#             in await bot.get_chat_administrators(chat_id)
#             if not admin.user.is_bot
#         ]

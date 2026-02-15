from datetime import datetime as dt
import functools
from typing import Callable, Any

from aiogram.types import Message, CallbackQuery

from dummy_bot.internal.presentation.interfaces import ILogger


def enriched_logger(logger: ILogger, class_name: str):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(event: Message | CallbackQuery, *args, **kwargs) -> Any:
            method_name = func.__name__
            call = f"{class_name}.{method_name}"

            context = {
                "call": call,
            }

            if isinstance(event, Message):
                context.update({
                    "message_id": event.message_id,
                    "chat_id": event.chat.id,
                    "chat_type": event.chat.type,
                    "user_id": event.from_user.id,
                    "username": event.from_user.username,
                    "is_bot": event.from_user.is_bot,
                    "date": event.date.isoformat() if event.date else None,
                })

                if event.content_type:
                    context["content_type"] = event.content_type


            elif isinstance(event, CallbackQuery):
                context.update({
                    "callback_id": event.id,
                    "message_id": event.message.message_id if event.message else None,
                    "data": event.data,
                    "user_id": event.from_user.id,
                    "chat_id": event.message.chat.id if event.message else None,
                })

            start = dt.now()

            try:
                result = await func(event, *args, **kwargs)
                logger.info(
                    f"success",
                    **context,
                    duration=f"{(dt.now() - start).microseconds // 1000}ms"
                )
                return result
            except Exception as e:
                logger.warn(
                    f"error: {e.__cause__}",
                    **context,
                    duration=f"{(dt.now() - start).microseconds // 1000}ms"
                )
                raise

        return wrapper

    return decorator

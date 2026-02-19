from aiogram import Bot
from aiogram.filters import BaseFilter
from aiogram.types import Message


class BotMentionFilter(BaseFilter):
    async def __call__(self, message: Message, bot: Bot):
        if not message.text or not message.entities:
            return False

        bot_username = f"@{bot._me.username}"

        for entity in message.entities:
            start = entity.offset
            end = entity.offset + entity.length
            if entity.type == "mention" and message.text[start:end].startswith(bot_username):
                 return True
        return False

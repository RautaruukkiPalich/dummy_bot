from aiogram.types import Message


async def get_file_unique_id(message: Message) -> str | None:
    if message.animation:
        return message.animation.file_unique_id
    if message.sticker:
        return message.sticker.file_unique_id
    return None
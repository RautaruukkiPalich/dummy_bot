from typing import List

from aiogram import Router, Bot, F
from aiogram.types import Message, ReactionTypeEmoji, ChatPermissions
from sqlalchemy.ext.asyncio import AsyncSession

from dummy_bot.internal.dto.dto import TelegramMessageDTO
from dummy_bot.internal.presentation.decorators import enriched_logger
from dummy_bot.internal.presentation.interfaces import ILogger, IPokakUseCase, IMuteUseCase


class TextRouter:
    def __init__(self,
                 router: Router,
                 admin_router: Router,
                 logger: ILogger,
                 pokak_use_case: IPokakUseCase,
                 mute_use_case: IMuteUseCase
                 ) -> None:
        self._router = router
        self._admin_router = admin_router
        self._logger = logger
        self._pokak_use_case = pokak_use_case
        self._mute_use_case = mute_use_case
        self._register_router()

    def _register_router(self) -> None:
        class_name = self.__class__.__name__

        @self._admin_router.message(F.text.startswith("!w "))
        @enriched_logger(self._logger, class_name)
        async def mute(message: Message, admins: List[int], bot: Bot) -> None:
            if not message.reply_to_message:
                await message.reply("command should be reply to message")
                return

            user_to_mute = message.reply_to_message.from_user
            if user_to_mute.id in admins or user_to_mute.is_bot:
                await message.reply("cant mute admins and bots")
                return

            dto = TelegramMessageDTO.from_message(message)
            resp = await self._mute_use_case.mute(dto)
            if not resp:
                await message.reply("invalid format")
                return

            await bot.restrict_chat_member(
                message.chat.id,
                user_to_mute.id,
                ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_other_messages=False,
                ),
                until_date=resp.delta,
            )
            mute_username = user_to_mute.username or user_to_mute.full_name
            mute_desc = f"Причина: {resp.reason}" if resp.reason else None

            await message.reply(
                f"Мут для @{mute_username} на {resp.delta_str}. {mute_desc or ''}")

        @self._router.message(F.entities.func(lambda entities: not entities))
        @enriched_logger(self._logger, class_name)
        async def handle_text(message: Message, session: AsyncSession) -> None:
            if message.animation or message.sticker:
                dto = TelegramMessageDTO.from_message(message)
                if await self._pokak_use_case.add(session, dto):
                    await message.react([ReactionTypeEmoji(emoji="👌")])
                    return

"""
Telegram channel adapter (aiogram v3, long-polling).

Supports three operating modes controlled by TELEGRAM_ENABLED_MODES:

  dm            — bot replies to direct messages from any user
  private_group — bot replies only in groups listed in TELEGRAM_ALLOWED_GROUP_IDS
  public_group  — bot replies in any group/supergroup/channel (public or private)

In group modes the bot reacts only when:
  - TELEGRAM_REQUIRE_MENTION=true  → message contains @bot_username
  - TELEGRAM_REQUIRE_MENTION=false → every message triggers the bot

Required ENV:
  TELEGRAM_BOT_TOKEN
  TELEGRAM_ENABLED_MODES   (comma-separated: dm, private_group, public_group)
  TELEGRAM_ALLOWED_GROUP_IDS (comma-separated negative ints, required for private_group)
  TELEGRAM_REQUIRE_MENTION (default: true)
"""
from __future__ import annotations

import time
from typing import Optional

import html

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from app.channels.base import BaseChannel, OrchestratorFn
from app.core.config import Settings, TelegramMode

# Maximum Telegram message length
_TELEGRAM_MAX_LEN = 4096


class TelegramChannel(BaseChannel):
    """
    Telegram adapter using aiogram v3 long-polling.

    Registers message handlers dynamically based on enabled modes.
    All handlers funnel through _handle_message(), which calls the
    injected orchestrator coroutine and sends the response back.
    """

    def __init__(self, on_message: OrchestratorFn, settings: Settings) -> None:
        super().__init__(on_message)
        self._settings = settings
        self._bot = Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
        self._dp = Dispatcher()
        self._router = Router(name="omnirag")
        self._dp.include_router(self._router)
        self._bot_username: Optional[str] = None
        self._register_handlers()

    # ── Handler registration ──────────────────────────────────────────────────

    def _register_handlers(self) -> None:
        modes = self._settings.telegram_modes

        # /start and /help always respond regardless of mode
        self._router.message.register(self._cmd_start, Command("start"))
        self._router.message.register(self._cmd_help, Command("help"))

        if TelegramMode.DM in modes:
            self._router.message.register(
                self._handle_message,
                F.chat.type == ChatType.PRIVATE,
            )
            logger.info("Telegram mode enabled: dm")

        if TelegramMode.PRIVATE_GROUP in modes:
            allowed = self._settings.telegram_allowed_ids
            if not allowed:
                raise ValueError(
                    "TELEGRAM_ENABLED_MODES includes 'private_group' "
                    "but TELEGRAM_ALLOWED_GROUP_IDS is empty"
                )
            self._router.message.register(
                self._handle_message,
                F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
                F.chat.id.in_(allowed),
                self._mention_filter if self._settings.telegram_require_mention else _always_true,
            )
            logger.info("Telegram mode enabled: private_group | allowed_ids={}", allowed)

        if TelegramMode.PUBLIC_GROUP in modes:
            self._router.message.register(
                self._handle_message,
                F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL}),
                self._mention_filter if self._settings.telegram_require_mention else _always_true,
            )
            logger.info("Telegram mode enabled: public_group")

    # ── Filters ───────────────────────────────────────────────────────────────

    def _mention_filter(self, message: Message) -> bool:
        """Returns True if the message mentions the bot."""
        if not message.text:
            return False
        if self._bot_username and f"@{self._bot_username}".lower() in message.text.lower():
            return True
        # Also accept replies to the bot's own messages
        if message.reply_to_message and message.reply_to_message.from_user:
            return message.reply_to_message.from_user.is_bot
        return False

    # ── Handlers ──────────────────────────────────────────────────────────────

    async def _cmd_start(self, message: Message) -> None:
        await message.answer(
            "Hi! I'm a RAG assistant. Ask me anything about the knowledge base.\n"
            "Use /help for more info."
        )

    async def _cmd_help(self, message: Message) -> None:
        await message.answer(
            "I answer questions based on the project knowledge base.\n\n"
            "Just send your question and I'll find the most relevant answer in the docs."
        )

    async def _handle_message(self, message: Message) -> None:
        if not message.text:
            return

        # Strip bot mention from group messages before processing
        query = _strip_mention(message.text, self._bot_username)
        if not query.strip():
            return

        chat_id = str(message.chat.id)
        user_id = str(message.from_user.id) if message.from_user else "unknown"
        username = message.from_user.username if message.from_user else None

        logger.info(
            "Telegram message | chat={} user={} (@{}) preview='{}'",
            chat_id, user_id, username, query[:60],
        )

        t0 = time.monotonic()
        try:
            response = await self._on_message(query)
        except Exception as exc:
            logger.exception("Orchestrator error | chat={} user={}", chat_id, user_id)
            response = "An internal error occurred. Please try again later."

        elapsed = time.monotonic() - t0
        logger.info(
            "Telegram response sent | chat={} user={} elapsed={:.2f}s",
            chat_id, user_id, elapsed,
        )

        await self.send_message(
            target_id=chat_id,
            text=response,
            thread_id=str(message.message_thread_id) if message.message_thread_id else None,
        )

    # ── BaseChannel interface ─────────────────────────────────────────────────

    async def start(self) -> None:
        me = await self._bot.get_me()
        self._bot_username = me.username
        logger.info(
            "Telegram bot starting | username=@{} modes={}",
            me.username,
            self._settings.telegram_modes,
        )
        await self._dp.start_polling(self._bot, allowed_updates=["message"])

    async def send_message(
        self,
        target_id: str,
        text: str,
        thread_id: Optional[str] = None,
    ) -> None:
        kwargs: dict = {"chat_id": int(target_id)}
        if thread_id:
            kwargs["message_thread_id"] = int(thread_id)

        safe = html.escape(text)
        for chunk in _split_text(safe, _TELEGRAM_MAX_LEN):
            await self._bot.send_message(**kwargs, text=chunk)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _always_true(_: Message) -> bool:
    return True


def _strip_mention(text: str, bot_username: Optional[str]) -> str:
    if bot_username:
        text = text.replace(f"@{bot_username}", "").replace(f"@{bot_username.lower()}", "")
    return text.strip()


def _split_text(text: str, max_len: int) -> list[str]:
    if len(text) <= max_len:
        return [text]
    parts = []
    while text:
        parts.append(text[:max_len])
        text = text[max_len:]
    return parts

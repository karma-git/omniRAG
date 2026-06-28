"""
Discord channel adapter (discord.py, Gateway / WebSocket).

Supports two operating modes controlled by DISCORD_ENABLED_MODES:

  dm     — bot replies to direct messages from any user
  server — bot replies in guild text channels (with optional allowlist)

In server mode the bot reacts only when:
  - DISCORD_REQUIRE_MENTION=true  → message must @mention the bot
  - DISCORD_REQUIRE_MENTION=false → every message in allowed channels triggers the bot

IMPORTANT: Message Content Intent must be enabled in the Discord Developer Portal
(Bot → Privileged Gateway Intents → Message Content Intent).

Required ENV:
  DISCORD_BOT_TOKEN

Optional ENV:
  DISCORD_ENABLED_MODES        (default: dm,server)
  DISCORD_ALLOWED_CHANNEL_IDS  (comma-separated channel IDs, empty = all channels)
  DISCORD_REQUIRE_MENTION      (default: true)
"""
from __future__ import annotations

import time
from typing import Optional

import discord
from loguru import logger

from app.channels.base import BaseChannel, OrchestratorFn
from app.core.config import DiscordMode, Settings

# Discord hard limit for message content
_DISCORD_MAX_LEN = 2000


class DiscordChannel(BaseChannel):
    """
    Discord adapter using discord.py Gateway (WebSocket long-connection).

    Event handlers are registered dynamically in _register_handlers().
    All messages funnel through _handle_message(), which calls the
    injected orchestrator coroutine and sends the response back.
    """

    def __init__(self, on_message: OrchestratorFn, settings: Settings) -> None:
        super().__init__(on_message)
        self._settings = settings

        intents = discord.Intents.default()
        intents.message_content = True  # Privileged — must be enabled in Dev Portal
        self._client = discord.Client(intents=intents)
        self._register_handlers()

    # ── Handler registration ──────────────────────────────────────────────────

    def _register_handlers(self) -> None:
        modes = self._settings.discord_modes

        @self._client.event
        async def on_ready() -> None:
            user = self._client.user
            logger.info(
                "Discord bot ready | user={} id={} modes={}",
                user, user.id if user else "?", modes,
            )

        @self._client.event
        async def on_message(message: discord.Message) -> None:
            await self._handle_message(message)

    # ── Message handler ───────────────────────────────────────────────────────

    async def _handle_message(self, message: discord.Message) -> None:
        # Never reply to ourselves
        if message.author == self._client.user:
            return

        modes = self._settings.discord_modes
        is_dm = isinstance(message.channel, discord.DMChannel)
        is_guild = message.guild is not None

        if is_dm:
            if DiscordMode.DM not in modes:
                return
            text = message.content.strip()
            logger.info(
                "Discord DM | user={} preview='{}'",
                message.author, text[:60],
            )

        elif is_guild:
            if DiscordMode.SERVER not in modes:
                return

            channel_id = str(message.channel.id)
            allowed = self._settings.discord_allowed_ids
            if allowed and channel_id not in allowed:
                return

            bot_user = self._client.user
            if self._settings.discord_require_mention:
                if bot_user not in message.mentions:
                    return
                text = _strip_mention(message.content, bot_user.id)
            else:
                text = message.content.strip()

            logger.info(
                "Discord server message | guild={} channel={} user={} preview='{}'",
                message.guild.id, message.channel.id, message.author, text[:60],
            )

        else:
            return

        if not text:
            return

        await self._process_and_reply(text, message.channel, str(message.author.id))

    # ── Core processing ───────────────────────────────────────────────────────

    async def _process_and_reply(
        self,
        text: str,
        channel: discord.abc.Messageable,
        user_id: str,
    ) -> None:
        t0 = time.monotonic()
        try:
            response = await self._on_message(text)
        except Exception:
            logger.exception("Orchestrator error | user={}", user_id)
            response = "An internal error occurred. Please try again later."

        elapsed = time.monotonic() - t0
        logger.info("Discord response sent | user={} elapsed={:.2f}s", user_id, elapsed)

        for chunk in _split_text(response, _DISCORD_MAX_LEN):
            await channel.send(chunk)

    # ── BaseChannel interface ─────────────────────────────────────────────────

    async def start(self) -> None:
        await self._client.start(self._settings.discord_bot_token)

    async def send_message(
        self,
        target_id: str,
        text: str,
        thread_id: Optional[str] = None,
    ) -> None:
        channel = self._client.get_channel(int(target_id))
        if channel is None:
            channel = await self._client.fetch_channel(int(target_id))
        for chunk in _split_text(text, _DISCORD_MAX_LEN):
            await channel.send(chunk)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _strip_mention(text: str, bot_id: int) -> str:
    """Remove <@BOT_ID> and <@!BOT_ID> (nickname mention) from message text."""
    return text.replace(f"<@{bot_id}>", "").replace(f"<@!{bot_id}>", "").strip()


def _split_text(text: str, max_len: int) -> list[str]:
    if len(text) <= max_len:
        return [text]
    parts = []
    while text:
        parts.append(text[:max_len])
        text = text[max_len:]
    return parts

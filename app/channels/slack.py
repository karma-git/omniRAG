"""
Slack channel adapter (slack_bolt async, Socket Mode).

Supports two operating modes controlled by SLACK_ENABLED_MODES:

  dm      — bot replies to direct messages from any user
  channel — bot replies in channels (with optional allowlist)

In channel mode the bot reacts only when:
  - SLACK_REQUIRE_MENTION=true  → message must contain @bot mention (app_mention event)
  - SLACK_REQUIRE_MENTION=false → every message in allowed channels triggers the bot

Socket Mode requires no public URL — the bot connects via WebSocket,
similar to Telegram long-polling.

Required ENV:
  SLACK_BOT_TOKEN   — xoxb-... (Bot User OAuth Token)
  SLACK_APP_TOKEN   — xapp-... (App-Level Token for Socket Mode)

Optional ENV:
  SLACK_ENABLED_MODES         (default: dm,channel)
  SLACK_ALLOWED_CHANNEL_IDS   (comma-separated, e.g. C01234,C56789)
  SLACK_REQUIRE_MENTION       (default: true)
"""

from __future__ import annotations

import time

from loguru import logger
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp

from app.channels.base import BaseChannel, OrchestratorFn
from app.core.config import Settings, SlackMode

# Slack's recommended max text length per message block
_SLACK_MAX_LEN = 3000


class SlackChannel(BaseChannel):
    """
    Slack adapter using slack_bolt async + Socket Mode.

    Registers event handlers dynamically based on enabled modes.
    All handlers funnel through _process_and_reply(), which calls the
    injected orchestrator coroutine and sends the response back.
    """

    def __init__(self, on_message: OrchestratorFn, settings: Settings) -> None:
        super().__init__(on_message)
        self._settings = settings
        self._app = AsyncApp(token=settings.slack_bot_token)
        self._handler = AsyncSocketModeHandler(
            app=self._app,
            app_token=settings.slack_app_token,
        )
        self._bot_user_id: str | None = None
        self._register_handlers()

    # ── Handler registration ──────────────────────────────────────────────────

    def _register_handlers(self) -> None:
        modes = self._settings.slack_modes

        if SlackMode.CHANNEL in modes and self._settings.slack_require_mention:
            # app_mention fires only when the bot is @mentioned in a channel
            self._app.event("app_mention")(self._handle_mention)
            logger.info("Slack mode enabled: channel (mention required)")

        # A single message handler covers DMs and/or unrestricted channel messages
        need_message_handler = SlackMode.DM in modes or (
            SlackMode.CHANNEL in modes and not self._settings.slack_require_mention
        )
        if need_message_handler:
            self._app.event("message")(self._handle_message)
            if SlackMode.DM in modes:
                logger.info("Slack mode enabled: dm")
            if SlackMode.CHANNEL in modes and not self._settings.slack_require_mention:
                logger.info("Slack mode enabled: channel (all messages)")

    # ── Handlers ──────────────────────────────────────────────────────────────

    async def _handle_mention(self, event: dict, client, say) -> None:
        """Handle @bot mentions in channels (SLACK_REQUIRE_MENTION=true)."""
        if event.get("bot_id") or event.get("subtype"):
            return

        channel_id = event.get("channel", "unknown")
        allowed = self._settings.slack_allowed_ids
        if allowed and channel_id not in allowed:
            logger.debug("Slack mention ignored: channel {} not in allowlist", channel_id)
            return

        text = _strip_mention(event.get("text", ""), self._bot_user_id)
        if not text.strip():
            return

        user_id = event.get("user", "unknown")
        # Reply in thread when possible
        thread_ts = event.get("thread_ts") or event.get("ts")

        logger.info(
            "Slack mention | channel={} user={} preview='{}'",
            channel_id,
            user_id,
            text[:60],
        )
        await self._process_and_reply(text, channel_id, user_id, thread_ts=thread_ts)

    async def _handle_message(self, event: dict, client, say) -> None:
        """
        Handle DM and/or all-channel messages (SLACK_REQUIRE_MENTION=false).

        Routes based on channel_type:
          im            → DM (processed when dm mode is enabled)
          channel/group → channel message (processed when channel mode is enabled)
        """
        if event.get("bot_id") or event.get("subtype"):
            return

        channel_type = event.get("channel_type")
        channel_id = event.get("channel", "unknown")
        modes = self._settings.slack_modes

        is_dm = channel_type == "im"
        is_channel = channel_type in ("channel", "group", "mpim")

        if is_dm:
            if SlackMode.DM not in modes:
                return
        elif is_channel:
            if SlackMode.CHANNEL not in modes or self._settings.slack_require_mention:
                return
            allowed = self._settings.slack_allowed_ids
            if allowed and channel_id not in allowed:
                return
        else:
            return

        text = event.get("text", "").strip()
        if not text:
            return

        user_id = event.get("user", "unknown")
        thread_ts = event.get("thread_ts") or event.get("ts")

        logger.info(
            "Slack message | channel={} type={} user={} preview='{}'",
            channel_id,
            channel_type,
            user_id,
            text[:60],
        )
        await self._process_and_reply(text, channel_id, user_id, thread_ts=thread_ts)

    # ── Core processing ───────────────────────────────────────────────────────

    async def _process_and_reply(
        self,
        text: str,
        channel_id: str,
        user_id: str,
        thread_ts: str | None = None,
    ) -> None:
        t0 = time.monotonic()
        try:
            response = await self._on_message(text)
        except Exception:
            logger.exception("Orchestrator error | channel={} user={}", channel_id, user_id)
            response = "An internal error occurred. Please try again later."

        elapsed = time.monotonic() - t0
        logger.info(
            "Slack response sent | channel={} user={} elapsed={:.2f}s",
            channel_id,
            user_id,
            elapsed,
        )

        await self.send_message(target_id=channel_id, text=response, thread_id=thread_ts)

    # ── BaseChannel interface ─────────────────────────────────────────────────

    async def start(self) -> None:
        auth = await self._app.client.auth_test()
        self._bot_user_id = auth["user_id"]
        logger.info(
            "Slack bot starting | user_id={} bot={} modes={}",
            self._bot_user_id,
            auth.get("user"),
            self._settings.slack_modes,
        )
        await self._handler.start_async()

    async def send_message(
        self,
        target_id: str,
        text: str,
        thread_id: str | None = None,
    ) -> None:
        for chunk in _split_text(text, _SLACK_MAX_LEN):
            kwargs: dict = {"channel": target_id, "text": chunk}
            if thread_id:
                kwargs["thread_ts"] = thread_id
            await self._app.client.chat_postMessage(**kwargs)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _strip_mention(text: str, bot_user_id: str | None) -> str:
    """Remove <@BOT_USER_ID> mention from message text."""
    if bot_user_id:
        text = text.replace(f"<@{bot_user_id}>", "")
    return text.strip()


def _split_text(text: str, max_len: int) -> list[str]:
    if len(text) <= max_len:
        return [text]
    parts = []
    while text:
        parts.append(text[:max_len])
        text = text[max_len:]
    return parts

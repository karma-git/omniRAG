"""
Central configuration via pydantic-settings.

All values come from environment variables or a .env file.
The app crashes on startup with a clear error if required vars are missing.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Literal, Optional, Set

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ChatProvider(str, Enum):
    TELEGRAM = "telegram"
    DISCORD = "discord"  # reserved for Phase 2
    SLACK = "slack"
    WEB = "web"


class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"  # reserved for Phase 2


class FaissSource(str, Enum):
    LOCAL = "local"
    S3 = "s3"


class TelegramMode(str, Enum):
    DM = "dm"
    PRIVATE_GROUP = "private_group"
    PUBLIC_GROUP = "public_group"


class DiscordMode(str, Enum):
    DM = "dm"
    SERVER = "server"


class SlackMode(str, Enum):
    DM = "dm"
    CHANNEL = "channel"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Platform selectors ────────────────────────────────────────────────────
    chat_provider: ChatProvider = ChatProvider.TELEGRAM
    llm_provider: LLMProvider = LLMProvider.OPENAI

    # ── OpenAI ────────────────────────────────────────────────────────────────
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_max_tokens: int = 1024
    openai_temperature: float = 0.2

    # ── Anthropic (Phase 2) ───────────────────────────────────────────────────
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-sonnet-4-6"

    # ── Telegram ──────────────────────────────────────────────────────────────
    telegram_bot_token: Optional[str] = None

    # Comma-separated list of TelegramMode values
    telegram_enabled_modes: str = "dm,private_group"

    # Comma-separated list of allowed group IDs for private_group mode
    telegram_allowed_group_ids: str = ""

    telegram_require_mention: bool = True

    # ── Discord ───────────────────────────────────────────────────────────────
    discord_bot_token: Optional[str] = None

    # Comma-separated list of DiscordMode values
    discord_enabled_modes: str = "dm,server"

    # Comma-separated list of allowed channel IDs for server mode (empty = all channels)
    discord_allowed_channel_ids: str = ""

    discord_require_mention: bool = True

    # ── Slack ─────────────────────────────────────────────────────────────────
    slack_bot_token: Optional[str] = None   # xoxb-...
    slack_app_token: Optional[str] = None   # xapp-... (Socket Mode)

    # Comma-separated list of SlackMode values
    slack_enabled_modes: str = "dm,channel"

    # Comma-separated list of allowed channel IDs for channel mode
    slack_allowed_channel_ids: str = ""

    slack_require_mention: bool = True

    # ── Web ───────────────────────────────────────────────────────────────────
    web_host: str = "0.0.0.0"
    web_port: int = 8000

    # ── RAG / FAISS ───────────────────────────────────────────────────────────
    faiss_source: FaissSource = FaissSource.LOCAL
    faiss_index_path: str = "./data/faiss.index"
    faiss_meta_path: str = "./data/chunks_meta.json"

    s3_bucket: Optional[str] = None
    s3_index_key: str = "faiss/faiss.index"
    s3_meta_key: str = "faiss/chunks_meta.json"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"

    rag_min_similarity: float = 0.30
    rag_top_k: int = 5
    rag_domain_description: str = "project knowledge base"

    # Optional path to a markdown file with custom bot instructions.
    # If the file exists, its content replaces rag_domain_description in the system prompt.
    system_prompt_path: Optional[str] = "./user/system-prompt.md"

    # ── Derived / cached properties ───────────────────────────────────────────
    @property
    def telegram_modes(self) -> Set[TelegramMode]:
        modes: Set[TelegramMode] = set()
        for raw in self.telegram_enabled_modes.split(","):
            raw = raw.strip()
            if raw:
                modes.add(TelegramMode(raw))
        return modes

    @property
    def telegram_allowed_ids(self) -> Set[int]:
        ids: Set[int] = set()
        for raw in self.telegram_allowed_group_ids.split(","):
            raw = raw.strip()
            if raw:
                ids.add(int(raw))
        return ids

    @property
    def discord_modes(self) -> Set[DiscordMode]:
        modes: Set[DiscordMode] = set()
        for raw in self.discord_enabled_modes.split(","):
            raw = raw.strip()
            if raw:
                modes.add(DiscordMode(raw))
        return modes

    @property
    def discord_allowed_ids(self) -> Set[str]:
        ids: Set[str] = set()
        for raw in self.discord_allowed_channel_ids.split(","):
            raw = raw.strip()
            if raw:
                ids.add(raw)
        return ids

    @property
    def slack_modes(self) -> Set[SlackMode]:
        modes: Set[SlackMode] = set()
        for raw in self.slack_enabled_modes.split(","):
            raw = raw.strip()
            if raw:
                modes.add(SlackMode(raw))
        return modes

    @property
    def slack_allowed_ids(self) -> Set[str]:
        ids: Set[str] = set()
        for raw in self.slack_allowed_channel_ids.split(","):
            raw = raw.strip()
            if raw:
                ids.add(raw)
        return ids

    # ── Startup validation ────────────────────────────────────────────────────
    @model_validator(mode="after")
    def _validate_providers(self) -> "Settings":
        if self.llm_provider == LLMProvider.OPENAI and not self.openai_api_key:
            raise ValueError("LLM_PROVIDER=openai but OPENAI_API_KEY is not set")
        if self.llm_provider == LLMProvider.ANTHROPIC and not self.anthropic_api_key:
            raise ValueError("LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set")
        if self.chat_provider == ChatProvider.TELEGRAM and not self.telegram_bot_token:
            raise ValueError("CHAT_PROVIDER=telegram but TELEGRAM_BOT_TOKEN is not set")
        if self.chat_provider == ChatProvider.DISCORD and not self.discord_bot_token:
            raise ValueError("CHAT_PROVIDER=discord but DISCORD_BOT_TOKEN is not set")
        if self.chat_provider == ChatProvider.SLACK and not self.slack_bot_token:
            raise ValueError("CHAT_PROVIDER=slack but SLACK_BOT_TOKEN is not set")
        if self.chat_provider == ChatProvider.SLACK and not self.slack_app_token:
            raise ValueError("CHAT_PROVIDER=slack but SLACK_APP_TOKEN is not set")
        # WEB provider needs no token
        if (
            self.faiss_source == FaissSource.S3
            and not self.s3_bucket
        ):
            raise ValueError("FAISS_SOURCE=s3 but S3_BUCKET is not set")
        return self


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

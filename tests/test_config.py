"""Tests for config.py — validation and derived properties."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings, TelegramMode


def _base_env(**overrides) -> dict:
    """Minimal valid env for Telegram + OpenAI."""
    base = {
        "chat_provider": "telegram",
        "llm_provider": "openai",
        "openai_api_key": "sk-test",
        "telegram_bot_token": "123:AAtest",
        "telegram_enabled_modes": "dm,private_group",
        "telegram_allowed_group_ids": "-100123",
    }
    base.update(overrides)
    return base


def test_valid_config_loads() -> None:
    s = Settings(**_base_env())
    assert s.openai_api_key == "sk-test"
    assert s.telegram_bot_token == "123:AAtest"


def test_missing_openai_key_raises() -> None:
    with pytest.raises(ValidationError, match="OPENAI_API_KEY"):
        Settings(**_base_env(openai_api_key=None))


def test_missing_telegram_token_raises() -> None:
    with pytest.raises(ValidationError, match="TELEGRAM_BOT_TOKEN"):
        Settings(**_base_env(telegram_bot_token=None))


def test_anthropic_key_required_when_selected() -> None:
    with pytest.raises(ValidationError, match="ANTHROPIC_API_KEY"):
        Settings(**_base_env(llm_provider="anthropic", anthropic_api_key=None))


def test_telegram_modes_parsed_correctly() -> None:
    s = Settings(**_base_env(telegram_enabled_modes="dm,public_group"))
    assert TelegramMode.DM in s.telegram_modes
    assert TelegramMode.PUBLIC_GROUP in s.telegram_modes
    assert TelegramMode.PRIVATE_GROUP not in s.telegram_modes


def test_telegram_allowed_ids_parsed() -> None:
    s = Settings(**_base_env(telegram_allowed_group_ids="-100123,-100456"))
    assert -100123 in s.telegram_allowed_ids
    assert -100456 in s.telegram_allowed_ids


def test_empty_allowed_ids() -> None:
    s = Settings(**_base_env(telegram_allowed_group_ids=""))
    assert s.telegram_allowed_ids == set()

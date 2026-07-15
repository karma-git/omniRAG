"""
OmniRAG entry point.

Bootstraps the selected channel and LLM provider from environment config,
wires them together via the orchestrate() coroutine, and starts the event loop.

Flow per message:
  Channel  →  security.check_input()
           →  RAGEngine.search()        (similarity guard)
           →  security.build_system_prompt()
           →  LLMProvider.generate_response()
           →  Channel.send_message()

To add a new platform: implement BaseChannel, register below in _build_channel().
To add a new LLM:      implement BaseLLMProvider, register in _build_provider().
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

from loguru import logger

from app.core.config import ChatProvider, LLMProvider, Settings, get_settings
from app.core.rag_engine import RAGEngine
from app.core.security import (
    build_system_prompt,
    check_input,
    get_rejection_message,
)

# ── Orchestrator ──────────────────────────────────────────────────────────────


class Orchestrator:
    """
    Stateless request handler injected into each channel as on_message.

    Each call is independent; no conversation history is maintained between
    requests (Strict Stateless per AGENTS.md principle #1).
    """

    def __init__(
        self, rag: RAGEngine, provider, settings: Settings, domain_description: str
    ) -> None:
        self._rag = rag
        self._provider = provider
        self._settings = settings
        self._domain_description = domain_description

    async def __call__(self, query: str) -> str:
        t0 = time.monotonic()

        # Stage 1 — input sanitisation / injection detection
        check = check_input(query)
        if not check.is_safe:
            logger.warning("Security check failed | reason={}", check.rejection_reason)
            return get_rejection_message(check.rejection_reason or "off_topic")

        # Stage 2 — vector search
        result = await self._rag.search(query)
        if not result.is_relevant:
            logger.info(
                "Query rejected: low similarity | top_score={:.3f}",
                result.scores[0] if result.scores else 0.0,
            )
            return get_rejection_message("low_similarity")

        # Stage 3 — assemble system prompt and call LLM
        system_prompt = build_system_prompt(
            domain_description=self._domain_description,
            context_chunks=result.chunks,
        )
        response = await self._provider.generate_response(
            system_prompt=system_prompt,
            context_chunks=result.chunks,
            user_query=query,
        )

        elapsed = time.monotonic() - t0
        logger.info(
            "Orchestrator done | channel→RAG→LLM elapsed={:.2f}s",
            elapsed,
        )
        return response


# ── Factories ─────────────────────────────────────────────────────────────────


def _build_provider(settings: Settings):
    if settings.llm_provider == LLMProvider.OPENAI:
        from app.providers.openai_prov import OpenAIProvider  # noqa: PLC0415

        return OpenAIProvider(settings)

    if settings.llm_provider == LLMProvider.ANTHROPIC:
        from app.providers.anthropic import AnthropicProvider  # noqa: PLC0415

        return AnthropicProvider(settings)

    raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider}")


def _load_domain_description(settings: Settings) -> str:
    """Return custom system-prompt file content if it exists, else fall back to env var."""
    if settings.system_prompt_path:
        path = Path(settings.system_prompt_path)
        if path.exists():
            content = path.read_text(encoding="utf-8").strip()
            if content:
                logger.info("Loaded custom system prompt from {}", path)
                return content
            logger.warning("system-prompt.md is empty — falling back to RAG_DOMAIN_DESCRIPTION")
    return settings.rag_domain_description


def _build_channel(settings: Settings, on_message, domain_description: str = ""):
    if settings.chat_provider == ChatProvider.TELEGRAM:
        from app.channels.telegram import TelegramChannel  # noqa: PLC0415

        return TelegramChannel(on_message=on_message, settings=settings)

    if settings.chat_provider == ChatProvider.DISCORD:
        from app.channels.discord import DiscordChannel  # noqa: PLC0415

        return DiscordChannel(on_message=on_message, settings=settings)

    if settings.chat_provider == ChatProvider.SLACK:
        from app.channels.slack import SlackChannel  # noqa: PLC0415

        return SlackChannel(on_message=on_message, settings=settings)

    if settings.chat_provider == ChatProvider.WEB:
        from app.channels.web import WebChannel  # noqa: PLC0415

        return WebChannel(
            on_message=on_message, settings=settings, system_prompt=domain_description
        )

    if settings.chat_provider == ChatProvider.MCP:
        from app.channels.mcp_channel import MCPChannel  # noqa: PLC0415

        return MCPChannel(on_message=on_message, settings=settings)

    raise ValueError(f"Unknown CHAT_PROVIDER: {settings.chat_provider}")


# ── Main ──────────────────────────────────────────────────────────────────────


async def main() -> None:
    settings = get_settings()

    if settings.chat_provider == ChatProvider.TELEGRAM:
        _modes = settings.telegram_modes
    elif settings.chat_provider == ChatProvider.DISCORD:
        _modes = settings.discord_modes
    elif settings.chat_provider == ChatProvider.SLACK:
        _modes = settings.slack_modes
    elif settings.chat_provider == ChatProvider.WEB:
        _modes = f"{settings.web_host}:{settings.web_port}"
    elif settings.chat_provider == ChatProvider.MCP:
        _modes = f"transport={settings.mcp_transport}"
        if settings.mcp_transport == "sse":
            _modes += f" {settings.mcp_host}:{settings.mcp_port}"
    else:
        _modes = "N/A"
    logger.info(
        "Starting OmniRAG | chat={} llm={} modes={}",
        settings.chat_provider,
        settings.llm_provider,
        _modes,
    )

    # Load FAISS index into RAM
    rag = RAGEngine(settings)
    await rag.load()

    # Build provider + orchestrator
    provider = _build_provider(settings)
    domain_description = _load_domain_description(settings)
    orchestrator = Orchestrator(
        rag=rag, provider=provider, settings=settings, domain_description=domain_description
    )

    # Build and start channel (runs until process is killed)
    channel = _build_channel(
        settings, on_message=orchestrator, domain_description=domain_description
    )
    if settings.hot_reload_enabled:
        from app.core.reload_server import ReloadServer  # noqa: PLC0415

        reload_server = ReloadServer(rag, settings)
        logger.info(
            "Hot reload endpoint enabled | {}:{}",
            settings.hot_reload_host,
            settings.hot_reload_port,
        )
        await asyncio.gather(channel.start(), reload_server.start(), reload_server.watch())
    else:
        await channel.start()


if __name__ == "__main__":
    asyncio.run(main())

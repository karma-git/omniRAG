"""
Anthropic (Claude) LLM provider adapter — Phase 2.

Required ENV:
  ANTHROPIC_API_KEY
  ANTHROPIC_MODEL  (default: claude-sonnet-4-6)
"""

from __future__ import annotations

from loguru import logger

from app.core.config import Settings
from app.providers.base import BaseLLMProvider


class AnthropicProvider(BaseLLMProvider):
    """
    Async Anthropic adapter using the Messages API.

    The system prompt is passed as the `system` parameter (not as a message),
    which is the recommended pattern for Claude models.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        # Lazy import so the package is not required when using OpenAI
        import anthropic  # noqa: PLC0415

        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def generate_response(
        self,
        system_prompt: str,
        context_chunks: list[str],
        user_query: str,
    ) -> str:
        logger.debug(
            "Anthropic request | model={} chunks={} query_preview='{}'",
            self._settings.anthropic_model,
            len(context_chunks),
            user_query[:60],
        )

        message = await self._client.messages.create(
            model=self._settings.anthropic_model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_query}],
        )

        response_text = message.content[0].text if message.content else ""
        logger.debug("Anthropic response | preview='{}'", response_text[:80])
        return response_text

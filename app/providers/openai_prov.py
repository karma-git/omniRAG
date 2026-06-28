"""
OpenAI LLM provider adapter (GPT-4o by default).

Required ENV:
  OPENAI_API_KEY
  OPENAI_MODEL         (default: gpt-4o)
  OPENAI_MAX_TOKENS    (default: 1024)
  OPENAI_TEMPERATURE   (default: 0.2)
"""

from __future__ import annotations

from loguru import logger
from openai import AsyncOpenAI

from app.core.config import Settings
from app.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """
    Async OpenAI adapter.

    Uses the Chat Completions API with a two-message structure:
      - system: assembled RAG prompt (domain rules + context)
      - user:   the sanitised query
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate_response(
        self,
        system_prompt: str,
        context_chunks: list[str],
        user_query: str,
    ) -> str:
        logger.debug(
            "OpenAI request | model={} chunks={} query_preview='{}'",
            self._settings.openai_model,
            len(context_chunks),
            user_query[:60],
        )

        completion = await self._client.chat.completions.create(
            model=self._settings.openai_model,
            max_tokens=self._settings.openai_max_tokens,
            temperature=self._settings.openai_temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
            ],
        )

        response_text = completion.choices[0].message.content or ""
        logger.debug(
            "OpenAI response | tokens_used={} preview='{}'",
            completion.usage.total_tokens if completion.usage else "?",
            response_text[:80],
        )
        return response_text

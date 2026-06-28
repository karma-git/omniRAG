"""
Abstract base classes for LLM and Embedding providers.

To add a new provider (e.g. Anthropic):
  1. Create app/providers/anthropic.py
  2. Subclass BaseLLMProvider
  3. Implement generate_response()
  4. Register the class in app/main.py provider factory
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


class BaseLLMProvider(ABC):
    """
    Interface for an LLM text-generation backend.

    The provider receives an already-assembled system prompt (containing
    context chunks and safety rules from security.py) plus the raw user query.
    It returns a single response string.
    """

    @abstractmethod
    async def generate_response(
        self,
        system_prompt: str,
        context_chunks: List[str],
        user_query: str,
    ) -> str:
        """
        Generate a response given the RAG context and user query.

        Args:
            system_prompt:  Pre-assembled system prompt (includes domain rules,
                            safety instructions, and injected context chunks).
            context_chunks: Raw chunk texts (already embedded in system_prompt;
                            passed separately for potential logging/audit).
            user_query:     The sanitised user question.

        Returns:
            The model's response as a plain string.
        """

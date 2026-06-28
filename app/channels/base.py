"""
Abstract base class for all chat channel adapters.

To add a new platform (e.g. Discord):
  1. Create app/channels/discord.py
  2. Subclass BaseChannel
  3. Implement start() and send_message()
  4. Register the class in app/main.py channel factory
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Coroutine, Optional


# Signature of the coroutine the orchestrator injects into each channel.
# channel receives a query string, channel returns a response string.
OrchestratorFn = Callable[[str], Coroutine[None, None, str]]


@dataclass
class IncomingMessage:
    """Unified representation of an incoming user message."""
    text: str
    user_id: str
    chat_id: str
    message_id: Optional[str] = None
    thread_id: Optional[str] = None
    username: Optional[str] = None


class BaseChannel(ABC):
    """
    Abstract interface for a chat platform adapter.

    Each subclass owns its own event loop binding, authentication,
    and platform-specific quirks.  The rest of the app never imports
    platform SDKs directly.
    """

    def __init__(self, on_message: OrchestratorFn) -> None:
        """
        Args:
            on_message: Async callable injected by main.py.
                        Accepts raw user text, returns the RAG answer string.
        """
        self._on_message = on_message

    @abstractmethod
    async def start(self) -> None:
        """Start listening for messages (polling / webhook / socket)."""

    @abstractmethod
    async def send_message(
        self,
        target_id: str,
        text: str,
        thread_id: Optional[str] = None,
    ) -> None:
        """Send a response back to the user/group."""

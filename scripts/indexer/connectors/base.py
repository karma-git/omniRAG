from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from scripts.indexer.embed_cache import EmbedCache


@dataclass(frozen=True)
class SourceDocument:
    text: str
    source: str
    metadata: dict[str, str | int] = field(default_factory=dict)


class DocumentSource(Protocol):
    def iter_documents(self, cache: EmbedCache | None = None) -> list[SourceDocument]: ...

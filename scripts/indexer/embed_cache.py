from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

import numpy as np
from loguru import logger


class EmbedCache:
    """Persistent embeddings and source-document cache backed by one JSON file.

    Vectors are stored as base64-encoded float32 blobs (~8 KB each) rather than
    raw JSON arrays (~16 KB each) to keep the file size reasonable.  Schema v2
    also stores connector state so an unchanged remote document can participate
    in a full FAISS rebuild without downloading its body again.
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        self._data: dict[str, str] = {}  # sha256 hex → base64-encoded float32 blob
        self._documents: dict[str, dict[str, dict]] = {}
        self._hits = 0
        self._misses = 0
        if path.exists():
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(raw, dict) and raw.get("schema_version") == 2:
                    self._data = raw.get("embeddings", {})
                    self._documents = raw.get("documents", {})
                elif isinstance(raw, dict):
                    # v1 was a flat sha256 -> encoded-vector mapping.
                    self._data = raw
                else:
                    raise ValueError("embed cache root must be a JSON object")
                logger.info("Embed cache loaded: {} entries ({})", len(self._data), path)
            except Exception as exc:
                logger.warning("Could not load embed cache ({}), starting fresh", exc)

    def get(self, text: str) -> list[float] | None:
        encoded = self._data.get(_sha256(text))
        if encoded is not None:
            self._hits += 1
            return _decode(encoded)
        self._misses += 1
        return None

    def set(self, text: str, vector: list[float]) -> None:
        self._data[_sha256(text)] = _encode(vector)

    def save(self) -> None:
        payload = {
            "schema_version": 2,
            "embeddings": self._data,
            "documents": self._documents,
        }
        self._path.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
        logger.info("Embed cache saved: {} entries ({})", len(self._data), self._path)

    def get_documents(self, source: str) -> dict[str, dict]:
        """Return a copy of cached documents for a connector namespace."""
        return dict(self._documents.get(source, {}))

    def replace_documents(self, source: str, documents: dict[str, dict]) -> None:
        """Replace connector state, removing documents absent after reconciliation."""
        self._documents[source] = documents

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def misses(self) -> int:
        return self._misses

    def __len__(self) -> int:
        return len(self._data)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _encode(vector: list[float]) -> str:
    return base64.b64encode(np.array(vector, dtype=np.float32).tobytes()).decode()


def _decode(encoded: str) -> list[float]:
    return np.frombuffer(base64.b64decode(encoded), dtype=np.float32).tolist()

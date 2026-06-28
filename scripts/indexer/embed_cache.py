from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

import numpy as np
from loguru import logger


class EmbedCache:
    """Persistent SHA-256 → float32 embedding cache backed by a JSON file.

    Vectors are stored as base64-encoded float32 blobs (~8 KB each) rather than
    raw JSON arrays (~16 KB each) to keep the file size reasonable.
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        self._data: dict[str, str] = {}  # sha256 hex → base64-encoded float32 blob
        self._hits = 0
        self._misses = 0
        if path.exists():
            try:
                self._data = json.loads(path.read_text(encoding="utf-8"))
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
        self._path.write_text(json.dumps(self._data, separators=(",", ":")), encoding="utf-8")
        logger.info("Embed cache saved: {} entries ({})", len(self._data), self._path)

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

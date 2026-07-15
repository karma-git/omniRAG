from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.rag_engine import RAGEngine


@pytest.mark.asyncio
async def test_reload_swaps_complete_candidate(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = MagicMock()
    rag = RAGEngine(settings)
    old_index = SimpleNamespace(ntotal=1)
    new_index = SimpleNamespace(ntotal=2)
    rag._index = old_index
    rag._chunks = ["old"]
    rag._version = "old"

    monkeypatch.setattr(rag, "_read_manifest", lambda: {"version": "new"})
    monkeypatch.setattr(rag, "_resolve_paths", lambda: ("index", "meta", None))
    monkeypatch.setattr(
        rag,
        "_load_candidate",
        lambda *args: (new_index, ["a", "b"]),
    )

    result = await rag.reload()

    assert result.changed is True
    assert rag._index is new_index
    assert rag._chunks == ["a", "b"]
    assert rag.version == "new"


@pytest.mark.asyncio
async def test_failed_reload_keeps_previous_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = MagicMock()
    rag = RAGEngine(settings)
    old_index = SimpleNamespace(ntotal=1)
    rag._index = old_index
    rag._chunks = ["old"]
    rag._version = "old"

    monkeypatch.setattr(rag, "_read_manifest", lambda: {"version": "broken"})
    monkeypatch.setattr(rag, "_resolve_paths", lambda: ("index", "meta", None))

    def fail(*args):
        raise ValueError("checksum mismatch")

    monkeypatch.setattr(rag, "_load_candidate", fail)

    with pytest.raises(ValueError, match="checksum"):
        await rag.reload()

    assert rag._index is old_index
    assert rag._chunks == ["old"]
    assert rag.version == "old"

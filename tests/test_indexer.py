"""Tests for chunking logic in scripts/indexer/pipeline.py."""

from scripts.indexer.pipeline import chunk_text


def test_short_text_returns_single_chunk() -> None:
    chunks = chunk_text("Hello world", chunk_size=800, overlap=100)
    assert chunks == ["Hello world"]


def test_long_text_splits_into_multiple_chunks() -> None:
    text = "word " * 300  # ~1500 chars
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) > 1


def test_no_empty_chunks() -> None:
    text = "sentence one. sentence two. sentence three. " * 50
    chunks = chunk_text(text, chunk_size=200, overlap=30)
    for chunk in chunks:
        assert chunk.strip() != ""


def test_overlap_content_shared() -> None:
    """With overlap > 0 some text should appear in consecutive chunks."""
    text = "abcdefghij" * 40  # 400 chars
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) >= 2
    tail = chunks[0][-20:]
    head = chunks[1][:20]
    assert any(c in head for c in tail)


def test_exact_chunk_size_returns_one_chunk() -> None:
    text = "x" * 800
    chunks = chunk_text(text, chunk_size=800, overlap=0)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_empty_text_returns_empty_list() -> None:
    chunks = chunk_text("", chunk_size=800, overlap=100)
    assert chunks == []

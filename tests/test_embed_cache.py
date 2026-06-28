"""Tests for scripts/indexer/embed_cache.py."""

from pathlib import Path

import numpy as np
import pytest

from scripts.indexer.embed_cache import EmbedCache, _decode, _encode, _sha256


def test_sha256_is_deterministic() -> None:
    assert _sha256("hello") == _sha256("hello")
    assert _sha256("hello") != _sha256("world")


def test_encode_decode_roundtrip() -> None:
    vec = list(np.random.default_rng(42).standard_normal(1536).astype(np.float32))
    assert _decode(_encode(vec)) == pytest.approx(vec, rel=1e-5)


def test_cache_miss_returns_none(tmp_path: Path) -> None:
    cache = EmbedCache(tmp_path / "cache.json")
    assert cache.get("unknown text") is None


def test_cache_set_then_get(tmp_path: Path) -> None:
    cache = EmbedCache(tmp_path / "cache.json")
    vec = [0.1, 0.2, 0.3]
    cache.set("hello", vec)
    assert cache.get("hello") == pytest.approx(vec, rel=1e-5)


def test_cache_hit_miss_counters(tmp_path: Path) -> None:
    cache = EmbedCache(tmp_path / "cache.json")
    cache.set("a", [1.0])
    cache.get("a")  # hit
    cache.get("b")  # miss
    assert cache.hits == 1
    assert cache.misses == 1


def test_cache_persists_across_instances(tmp_path: Path) -> None:
    path = tmp_path / "cache.json"
    vec = [0.5, -0.5, 1.0]

    c1 = EmbedCache(path)
    c1.set("text", vec)
    c1.save()

    c2 = EmbedCache(path)
    assert c2.get("text") == pytest.approx(vec, rel=1e-5)
    assert len(c2) == 1


def test_cache_file_is_compact_json(tmp_path: Path) -> None:
    path = tmp_path / "cache.json"
    cache = EmbedCache(path)
    cache.set("x", [1.0, 2.0])
    cache.save()
    raw = path.read_text()
    assert " " not in raw  # no spaces — compact separators


def test_cache_len(tmp_path: Path) -> None:
    cache = EmbedCache(tmp_path / "cache.json")
    assert len(cache) == 0
    cache.set("a", [1.0])
    cache.set("b", [2.0])
    assert len(cache) == 2


def test_corrupt_cache_file_starts_fresh(tmp_path: Path) -> None:
    path = tmp_path / "cache.json"
    path.write_text("not valid json")
    cache = EmbedCache(path)  # should not raise
    assert len(cache) == 0

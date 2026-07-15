from pathlib import Path

import pytest

from scripts.indexer.connectors.confluence import (
    ConfluenceConfig,
    ConfluenceSource,
    _Page,
    storage_to_text,
)
from scripts.indexer.embed_cache import EmbedCache


def test_storage_html_to_normalized_text() -> None:
    html = "<h1>Runbook</h1><p>Restart <strong>the service</strong>.</p><script>x</script>"
    assert storage_to_text(html) == "Runbook\n\nRestart the service."


def test_config_requires_selector(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONFLUENCE_BASE_URL", "https://example.atlassian.net")
    monkeypatch.setenv("CONFLUENCE_EMAIL", "bot@example.com")
    monkeypatch.setenv("CONFLUENCE_API_TOKEN", "token")
    monkeypatch.delenv("CONFLUENCE_SPACE_KEYS", raising=False)
    monkeypatch.delenv("CONFLUENCE_CQL", raising=False)
    with pytest.raises(ValueError, match="SPACE_KEYS"):
        ConfluenceConfig.from_env()


def test_unchanged_page_uses_cached_content_and_reconciles(
    tmp_path: Path, monkeypatch
) -> None:
    cache = EmbedCache(tmp_path / "cache.json")
    cache.replace_documents(
        "confluence",
        {
            "1": {
                "version": 3,
                "title": "Kept",
                "content": "cached",
                "sha256": "x",
            },
            "2": {
                "version": 1,
                "title": "Deleted",
                "content": "old",
                "sha256": "y",
            },
        },
    )
    config = ConfluenceConfig(
        base_url="https://example.atlassian.net",
        deployment="cloud",
        space_keys=("OPS",),
        cql=None,
        workers=2,
        auth=object(),
    )
    source = ConfluenceSource(config)
    monkeypatch.setattr(
        source,
        "_discover_cloud",
        lambda client: [_Page("1", "Kept", 3, "2026-01-01")],
    )

    class _ClientContext:
        def __enter__(self):
            return object()

        def __exit__(self, *args):
            return None

    monkeypatch.setattr(source, "_client", lambda: _ClientContext())
    monkeypatch.setattr(
        source,
        "_fetch_page",
        lambda page: pytest.fail("unchanged body must not be downloaded"),
    )

    documents = source.iter_documents(cache)

    assert [doc.text for doc in documents] == ["cached"]
    assert set(cache.get_documents("confluence")) == {"1"}


def test_changed_page_reuses_pipeline_embedding_cache(
    tmp_path: Path, monkeypatch
) -> None:
    cache = EmbedCache(tmp_path / "cache.json")
    config = ConfluenceConfig(
        base_url="https://example.atlassian.net",
        deployment="cloud",
        space_keys=("OPS",),
        cql=None,
        workers=1,
        auth=object(),
    )
    source = ConfluenceSource(config)
    monkeypatch.setattr(
        source,
        "_discover_cloud",
        lambda client: [_Page("1", "Page", 4, "2026-01-02")],
    )

    class _ClientContext:
        def __enter__(self):
            return object()

        def __exit__(self, *args):
            return None

    monkeypatch.setattr(source, "_client", lambda: _ClientContext())
    monkeypatch.setattr(
        source,
        "_fetch_page",
        lambda page: (
            "1",
            {
                "version": 4,
                "updated_at": "2026-01-02",
                "title": "Page",
                "content": "same normalized content",
                "sha256": "hash",
                "url": "",
            },
        ),
    )

    assert source.iter_documents(cache)[0].metadata["version"] == 4
    assert cache.get_documents("confluence")["1"]["content"] == "same normalized content"

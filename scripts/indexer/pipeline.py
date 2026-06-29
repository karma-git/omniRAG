from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import faiss
import numpy as np
from loguru import logger
from openai import OpenAI

from app.core.normalizer import normalize
from scripts.indexer.connectors import iter_documents
from scripts.indexer.embed_cache import EmbedCache
from scripts.indexer.propositions import extract_propositions
from scripts.indexer.storage import StorageBackend


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping character-level chunks.

    Tries to break at sentence boundaries ('. ', '! ', '? ', '\\n\\n') when possible.
    """
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        search_from = start + int(chunk_size * 0.80)
        best_break = -1
        for sep in (". ", "! ", "? ", "\n\n", "\n"):
            pos = text.rfind(sep, search_from, end)
            if pos != -1 and pos > best_break:
                best_break = pos + len(sep)

        cut = best_break if best_break != -1 else end
        chunk = text[start:cut].strip()
        if chunk:
            chunks.append(chunk)
        start = max(cut - overlap, start + 1)

    return chunks


def _embed_texts(
    texts: list[str],
    client: OpenAI,
    model: str,
    cache: EmbedCache | None,
    batch_size: int = 100,
) -> list[list[float]]:
    """Embed a list of texts, using cache for previously seen ones."""
    # Split into cached and uncached
    cached: dict[int, list[float]] = {}
    uncached_idx: list[int] = []
    uncached_texts: list[str] = []

    for i, text in enumerate(texts):
        vec = cache.get(text) if cache else None
        if vec is not None:
            cached[i] = vec
        else:
            uncached_idx.append(i)
            uncached_texts.append(text)

    if cache:
        logger.info(
            "Embed cache: {} hits, {} misses ({}% saved)",
            cache.hits,
            cache.misses,
            int(100 * cache.hits / len(texts)) if texts else 0,
        )

    # Call OpenAI only for uncached texts
    new_vecs: list[list[float]] = []
    if uncached_texts:
        logger.info("Embedding {} new texts via OpenAI model={}...", len(uncached_texts), model)
        for i in range(0, len(uncached_texts), batch_size):
            batch = uncached_texts[i : i + batch_size]
            response = client.embeddings.create(model=model, input=batch)
            batch_vecs = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
            new_vecs.extend(batch_vecs)
            logger.info(
                "  embedded {}/{}", min(i + batch_size, len(uncached_texts)), len(uncached_texts)
            )

        if cache:
            for text, vec in zip(uncached_texts, new_vecs, strict=True):
                cache.set(text, vec)

    # Reconstruct full list in original order
    new_iter = iter(new_vecs)
    return [cached[i] if i in cached else next(new_iter) for i in range(len(texts))]


def build_index(
    docs_dir: Path,
    storage: StorageBackend,
    chunk_size: int,
    overlap: int,
    embedding_model: str,
    recursive: bool,
    use_propositions: bool = False,
    chat_model: str = "gpt-4o-mini",
    use_cache: bool = True,
) -> None:
    client = OpenAI()

    cache: EmbedCache | None = None
    _tmp_dir: tempfile.TemporaryDirectory | None = None
    if use_cache:
        _tmp_dir = tempfile.TemporaryDirectory(prefix="rag_cache_")
        tmp_cache_path = Path(_tmp_dir.name) / "embed_cache.json"
        cached_data = storage.read("embed_cache.json")
        if cached_data:
            tmp_cache_path.write_bytes(cached_data)
        cache = EmbedCache(tmp_cache_path)

    all_chunks: list[dict] = []
    texts_to_embed: list[str] = []
    chunk_id = 0

    for doc_path, raw_text in iter_documents(docs_dir, recursive):
        clean_text = normalize(raw_text)
        for chunk in chunk_text(clean_text, chunk_size, overlap):
            if use_propositions:
                props = extract_propositions(chunk, client, chat_model)
                logger.debug("  chunk {} → {} propositions", chunk_id, len(props))
                for prop in props:
                    all_chunks.append(
                        {
                            "text": chunk,  # original chunk returned to LLM as context
                            "proposition": prop,  # atomic fact used for embedding/retrieval
                            "source": str(doc_path.name),
                            "chunk_id": chunk_id,
                        }
                    )
                    texts_to_embed.append(prop)
                    chunk_id += 1
            else:
                all_chunks.append(
                    {
                        "text": chunk,
                        "source": str(doc_path.name),
                        "chunk_id": chunk_id,
                    }
                )
                texts_to_embed.append(chunk)
                chunk_id += 1

    if not all_chunks:
        logger.error("No text found in {}. Aborting.", docs_dir)
        sys.exit(1)

    mode = "proposition" if use_propositions else "chunk"
    logger.info("Total {}s to embed: {}", mode, len(texts_to_embed))

    all_vecs = _embed_texts(texts_to_embed, client, embedding_model, cache)

    if cache:
        cache.save()
        cache_data = Path(cache._path).read_bytes()
        storage.write("embed_cache.json", cache_data)
        if _tmp_dir:
            _tmp_dir.cleanup()

    embeddings = np.array(all_vecs, dtype=np.float32)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings /= norms

    dim = embeddings.shape[1]
    logger.info("Embedding dim: {}", dim)

    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    with tempfile.NamedTemporaryFile(suffix=".index", delete=False) as tmp:
        tmp_index_path = tmp.name
    faiss.write_index(index, tmp_index_path)
    storage.write("faiss.index", Path(tmp_index_path).read_bytes())
    Path(tmp_index_path).unlink(missing_ok=True)

    meta_bytes = json.dumps(all_chunks, ensure_ascii=False, indent=2).encode()
    storage.write("chunks_meta.json", meta_bytes)

    logger.success(
        "Index built | vectors={} dim={}",
        index.ntotal,
        dim,
    )

from __future__ import annotations

import json
import sys
from pathlib import Path

import faiss
import numpy as np
from loguru import logger
from openai import OpenAI

from app.core.normalizer import normalize
from scripts.indexer.connectors import iter_documents
from scripts.indexer.propositions import extract_propositions


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


def build_index(
    docs_dir: Path,
    out_dir: Path,
    chunk_size: int,
    overlap: int,
    embedding_model: str,
    recursive: bool,
    use_propositions: bool = False,
    chat_model: str = "gpt-4o-mini",
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    client = OpenAI()

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

    logger.info("Embedding via OpenAI model={}...", embedding_model)
    batch_size = 100
    all_vecs: list[list[float]] = []
    for i in range(0, len(texts_to_embed), batch_size):
        batch = texts_to_embed[i : i + batch_size]
        response = client.embeddings.create(model=embedding_model, input=batch)
        all_vecs.extend(item.embedding for item in sorted(response.data, key=lambda x: x.index))
        logger.info(
            "  embedded {}/{}", min(i + batch_size, len(texts_to_embed)), len(texts_to_embed)
        )

    embeddings = np.array(all_vecs, dtype=np.float32)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings /= norms

    dim = embeddings.shape[1]
    logger.info("Embedding dim: {}", dim)

    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    index_path = out_dir / "faiss.index"
    meta_path = out_dir / "chunks_meta.json"

    faiss.write_index(index, str(index_path))
    meta_path.write_text(json.dumps(all_chunks, ensure_ascii=False, indent=2), encoding="utf-8")

    logger.success(
        "Index built | vectors={} dim={} -> {} + {}",
        index.ntotal,
        dim,
        index_path,
        meta_path,
    )

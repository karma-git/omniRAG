#!/usr/bin/env python3
"""
Document indexer: chunk → embed → FAISS index.

Supported formats: .txt, .md, .pdf

Usage:
  python scripts/index_documents.py --docs-dir ./my_docs --out-dir ./data

Options:
  --docs-dir   DIR   Directory with source documents (default: ./docs)
  --out-dir    DIR   Output directory for faiss.index + chunks_meta.json (default: ./data)
  --chunk-size INT   Max characters per chunk (default: 800)
  --overlap    INT   Overlap between adjacent chunks in chars (default: 100)
  --model      STR   OpenAI embedding model (default: text-embedding-3-small)
  --recursive        Scan docs-dir recursively (default: True)

Output files:
  <out-dir>/faiss.index
  <out-dir>/chunks_meta.json   — list of {"text": str, "source": str, "chunk_id": int}
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from collections.abc import Iterator
from pathlib import Path

import faiss
import numpy as np
from loguru import logger
from openai import OpenAI

# ── Text extraction ───────────────────────────────────────────────────────────


def extract_text_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def extract_text_pdf(path: Path) -> str:
    try:
        import pypdf  # noqa: PLC0415
    except ImportError:
        logger.warning("pypdf not installed — skipping {}", path)
        return ""
    reader = pypdf.PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


_EXTRACTORS = {
    ".txt": extract_text_txt,
    ".md": extract_text_txt,
    ".markdown": extract_text_txt,
    ".pdf": extract_text_pdf,
}


def iter_documents(docs_dir: Path, recursive: bool) -> Iterator[tuple[Path, str]]:
    glob = "**/*" if recursive else "*"
    for path in sorted(docs_dir.glob(glob)):
        if not path.is_file():
            continue
        extractor = _EXTRACTORS.get(path.suffix.lower())
        if extractor is None:
            logger.debug("Skipping unsupported file: {}", path)
            continue
        logger.info("Reading: {}", path.relative_to(docs_dir))
        text = extractor(path)
        if text.strip():
            yield path, text
        else:
            logger.warning("Empty content: {}", path)


# ── Chunking ──────────────────────────────────────────────────────────────────


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """
    Split text into overlapping character-level chunks.
    Tries to break at sentence boundaries ('. ', '! ', '? ', '\n\n') when possible.
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

        # Try to find a clean sentence boundary within the last 20% of the chunk
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
        start = max(cut - overlap, start + 1)  # ensure forward progress

    return chunks


# ── Main ──────────────────────────────────────────────────────────────────────


def build_index(
    docs_dir: Path,
    out_dir: Path,
    chunk_size: int,
    overlap: int,
    model_name: str,
    recursive: bool,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # Collect all chunks
    all_chunks: list[dict] = []
    chunk_id = 0
    for doc_path, text in iter_documents(docs_dir, recursive):
        for chunk in chunk_text(text, chunk_size, overlap):
            all_chunks.append(
                {
                    "text": chunk,
                    "source": str(doc_path.name),
                    "chunk_id": chunk_id,
                }
            )
            chunk_id += 1

    if not all_chunks:
        logger.error("No text found in {}. Aborting.", docs_dir)
        sys.exit(1)

    logger.info("Total chunks: {}", len(all_chunks))

    # Embed via OpenAI API
    client = OpenAI()
    texts = [c["text"] for c in all_chunks]
    logger.info("Embedding {} chunks via OpenAI model={}...", len(texts), model_name)

    batch_size = 100
    all_vecs: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(model=model_name, input=batch)
        all_vecs.extend(item.embedding for item in sorted(response.data, key=lambda x: x.index))
        logger.info("  embedded {}/{}", min(i + batch_size, len(texts)), len(texts))

    embeddings = np.array(all_vecs, dtype=np.float32)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings /= norms

    dim = embeddings.shape[1]
    logger.info("Embedding dim: {}", dim)

    # Build FAISS index (Inner Product on L2-normalised vectors == cosine similarity)
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    # Write outputs
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build FAISS index from documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(__doc__ or ""),
    )
    parser.add_argument("--docs-dir", default="./docs", type=Path)
    parser.add_argument("--out-dir", default="./data", type=Path)
    parser.add_argument("--chunk-size", default=800, type=int)
    parser.add_argument("--overlap", default=100, type=int)
    parser.add_argument(
        "--model",
        default=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
    )
    parser.add_argument("--recursive", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    if not args.docs_dir.exists():
        logger.error("--docs-dir does not exist: {}", args.docs_dir)
        sys.exit(1)

    build_index(
        docs_dir=args.docs_dir,
        out_dir=args.out_dir,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        model_name=args.model,
        recursive=args.recursive,
    )


if __name__ == "__main__":
    main()

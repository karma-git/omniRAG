"""Document indexer: normalize → chunk → embed → FAISS index.

Supported formats: .txt, .md, .pdf

Usage:
  python -m scripts.indexer --docs-dir ./my_docs --out-dir ./data

  # With AI proposition extraction (better retrieval, costs more):
  python -m scripts.indexer --extract-propositions

Options:
  --docs-dir            DIR   Directory with source documents (default: ./docs)
  --out-dir             DIR   Output directory for faiss.index + chunks_meta.json (default: ./data)
  --chunk-size          INT   Max characters per chunk (default: 800)
  --overlap             INT   Overlap between adjacent chunks in chars (default: 100)
  --model               STR   OpenAI embedding model (default: text-embedding-3-small)
  --recursive                 Scan docs-dir recursively (default: True)
  --extract-propositions      Use LLM to extract atomic propositions before embedding
  --chat-model          STR   Chat model for proposition extraction (default: gpt-4o-mini)

Output files:
  <out-dir>/faiss.index
  <out-dir>/chunks_meta.json  — list of {"text", "source", "chunk_id"[, "proposition"]}
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from loguru import logger

from scripts.indexer.pipeline import build_index


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build FAISS index from documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
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
    parser.add_argument(
        "--extract-propositions",
        action="store_true",
        help="Use LLM to extract atomic propositions before embedding (improves retrieval precision)",
    )
    parser.add_argument(
        "--chat-model",
        default=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        help="Chat model used for proposition extraction (default: gpt-4o-mini)",
    )
    args = parser.parse_args()

    if not args.docs_dir.exists():
        logger.error("--docs-dir does not exist: {}", args.docs_dir)
        sys.exit(1)

    if args.extract_propositions:
        logger.info(
            "Proposition extraction enabled (chat_model={}). "
            "This makes 1 LLM call per chunk — costs more but improves retrieval precision.",
            args.chat_model,
        )

    build_index(
        docs_dir=args.docs_dir,
        out_dir=args.out_dir,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        embedding_model=args.model,
        recursive=args.recursive,
        use_propositions=args.extract_propositions,
        chat_model=args.chat_model,
    )


if __name__ == "__main__":
    main()

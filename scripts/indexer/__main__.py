"""Document indexer: normalize → chunk → embed → FAISS index.

Supported formats: .txt, .md, .pdf

Usage:
  python -m scripts.indexer --docs-dir ./my_docs --out-dir ./data
  python -m scripts.indexer --storage-backend s3 --s3-bucket my-bucket

  # With AI proposition extraction (better retrieval, costs more):
  python -m scripts.indexer --extract-propositions

Options:
  --docs-dir            DIR   Directory with source documents (default: ./docs)
  --storage-backend     STR   Where to store index artifacts: local|s3 (default: local)
  --out-dir             DIR   [local] Output directory (default: ./data)
  --s3-bucket           STR   [s3] S3 bucket name (or env S3_BUCKET)
  --s3-prefix           STR   [s3] Key prefix inside the bucket (default: faiss)
  --chunk-size          INT   Max characters per chunk (default: 800)
  --overlap             INT   Overlap between adjacent chunks in chars (default: 100)
  --model               STR   OpenAI embedding model (default: text-embedding-3-small)
  --recursive                 Scan docs-dir recursively (default: True)
  --extract-propositions      Use LLM to extract atomic propositions before embedding
  --chat-model          STR   Chat model for proposition extraction (default: gpt-4o-mini)

Output artifacts (faiss.index, chunks_meta.json, embed_cache.json):
  local: written to <out-dir>/
  s3:    uploaded to s3://<bucket>/<prefix>/
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from loguru import logger

from scripts.indexer.pipeline import build_index
from scripts.indexer.storage import LocalStorage, S3Storage, StorageBackend


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build FAISS index from documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--docs-dir", default="./docs", type=Path)
    parser.add_argument(
        "--storage-backend",
        default=os.getenv("STORAGE_BACKEND", "local"),
        choices=["local", "s3"],
    )
    parser.add_argument("--out-dir", default="./data", type=Path)
    parser.add_argument("--s3-bucket", default=os.getenv("S3_BUCKET"))
    parser.add_argument("--s3-prefix", default=os.getenv("S3_PREFIX", "faiss"))
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
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable embedding cache and re-embed everything from scratch",
    )
    args = parser.parse_args()

    if not args.docs_dir.exists():
        logger.error("--docs-dir does not exist: {}", args.docs_dir)
        sys.exit(1)

    storage: StorageBackend
    if args.storage_backend == "s3":
        if not args.s3_bucket:
            logger.error("--storage-backend s3 requires --s3-bucket or S3_BUCKET env var")
            sys.exit(1)
        storage = S3Storage(bucket=args.s3_bucket, prefix=args.s3_prefix)
        logger.info("Storage backend: s3://{}/{}/", args.s3_bucket, args.s3_prefix)
    else:
        storage = LocalStorage(args.out_dir)
        logger.info("Storage backend: local ({})", args.out_dir)

    if args.extract_propositions:
        logger.info(
            "Proposition extraction enabled (chat_model={}). "
            "This makes 1 LLM call per chunk — costs more but improves retrieval precision.",
            args.chat_model,
        )

    build_index(
        docs_dir=args.docs_dir,
        storage=storage,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        embedding_model=args.model,
        recursive=args.recursive,
        use_propositions=args.extract_propositions,
        chat_model=args.chat_model,
        use_cache=not args.no_cache,
    )


if __name__ == "__main__":
    main()

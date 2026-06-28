"""
RAG Engine: loads a FAISS index into RAM at startup and performs similarity search.

Supported index sources:
  - local  — reads from FAISS_INDEX_PATH / FAISS_META_PATH on disk
  - s3     — downloads from S3 into a temp directory at startup

ENV variables (all via config.py):
  FAISS_SOURCE, FAISS_INDEX_PATH, FAISS_META_PATH,
  S3_BUCKET, S3_INDEX_KEY, S3_META_KEY,
  RAG_MIN_SIMILARITY, RAG_TOP_K
"""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from typing import List, Optional

import faiss
import numpy as np
from loguru import logger
from openai import AsyncOpenAI

from app.core.config import FaissSource, Settings


@dataclass
class SearchResult:
    chunks: List[str]
    scores: List[float]
    is_relevant: bool  # False when best score < RAG_MIN_SIMILARITY


class RAGEngine:
    """
    Stateless RAG engine.  One instance lives for the entire process lifetime.
    The FAISS index and metadata are loaded once into RAM; no disk access occurs
    during query processing.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._index: Optional[faiss.Index] = None
        self._chunks: List[str] = []

        self._embedder: AsyncOpenAI | None = None

    # ── Startup ───────────────────────────────────────────────────────────────

    async def load(self) -> None:
        """Load FAISS index and chunk metadata into RAM. Call once at startup."""
        index_path, meta_path = await self._resolve_paths()
        self._index = faiss.read_index(index_path)
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        # meta is expected to be a list of strings (raw chunk texts)
        # or a list of dicts with a "text" key
        self._chunks = [
            item if isinstance(item, str) else item["text"] for item in meta
        ]
        logger.info(
            "FAISS index loaded | vectors={} chunks={}",
            self._index.ntotal,
            len(self._chunks),
        )
        self._embedder = self._build_embedder()

    async def _resolve_paths(self) -> tuple[str, str]:
        if self._settings.faiss_source == FaissSource.LOCAL:
            return (
                self._settings.faiss_index_path,
                self._settings.faiss_meta_path,
            )
        # S3 download
        import boto3  # noqa: PLC0415

        s3 = boto3.client(
            "s3",
            aws_access_key_id=self._settings.aws_access_key_id,
            aws_secret_access_key=self._settings.aws_secret_access_key,
            region_name=self._settings.aws_region,
        )
        tmp_dir = tempfile.mkdtemp(prefix="rag_")
        index_path = os.path.join(tmp_dir, "faiss.index")
        meta_path = os.path.join(tmp_dir, "chunks_meta.json")
        logger.info("Downloading FAISS index from S3 bucket={}", self._settings.s3_bucket)
        s3.download_file(self._settings.s3_bucket, self._settings.s3_index_key, index_path)
        s3.download_file(self._settings.s3_bucket, self._settings.s3_meta_key, meta_path)
        return index_path, meta_path

    def _build_embedder(self) -> AsyncOpenAI:
        logger.info("Embedding via OpenAI API | model={}", self._settings.openai_embedding_model)
        return AsyncOpenAI(api_key=self._settings.openai_api_key)

    # ── Query ─────────────────────────────────────────────────────────────────

    async def search(self, query: str) -> SearchResult:
        """
        Embed query via OpenAI API and return top-K most similar chunks.
        If the best score is below RAG_MIN_SIMILARITY, marks result as not relevant.
        """
        if self._index is None or self._embedder is None:
            raise RuntimeError("RAGEngine.load() must be called before search()")

        response = await self._embedder.embeddings.create(
            model=self._settings.openai_embedding_model,
            input=query,
        )
        raw = np.array(response.data[0].embedding, dtype=np.float32)
        raw /= np.linalg.norm(raw)
        vec = raw.reshape(1, -1)
        k = min(self._settings.rag_top_k, self._index.ntotal)
        if k == 0:
            return SearchResult(chunks=[], scores=[], is_relevant=False)

        scores, indices = self._index.search(vec, k)
        scores = scores[0].tolist()
        indices = indices[0].tolist()

        valid_chunks = []
        valid_scores = []
        for score, idx in zip(scores, indices):
            if idx == -1:
                continue
            valid_chunks.append(self._chunks[idx])
            valid_scores.append(float(score))

        is_relevant = bool(valid_scores and valid_scores[0] >= self._settings.rag_min_similarity)

        logger.debug(
            "RAG search | query_preview='{}' top_score={:.3f} relevant={}",
            query[:60],
            valid_scores[0] if valid_scores else 0.0,
            is_relevant,
        )
        return SearchResult(chunks=valid_chunks, scores=valid_scores, is_relevant=is_relevant)

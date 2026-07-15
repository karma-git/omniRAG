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

import asyncio
import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np
from loguru import logger
from openai import AsyncOpenAI

from app.core.config import FaissSource, Settings


@dataclass
class SearchResult:
    chunks: list[str]
    scores: list[float]
    is_relevant: bool  # False when best score < RAG_MIN_SIMILARITY


@dataclass(frozen=True)
class ReloadResult:
    changed: bool
    version: str | None
    vectors: int


class RAGEngine:
    """
    Stateless RAG engine.  One instance lives for the entire process lifetime.
    The FAISS index and metadata are loaded once into RAM; no disk access occurs
    during query processing.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._index: faiss.Index | None = None
        self._chunks: list[str] = []
        self._embedder: AsyncOpenAI | None = None
        self._version: str | None = None
        self._state_lock = asyncio.Lock()
        self._reload_lock = asyncio.Lock()

    # ── Startup ───────────────────────────────────────────────────────────────

    async def load(self) -> None:
        """Load FAISS index and chunk metadata into RAM. Call once at startup."""
        result = await self.reload(force=True)
        self._embedder = self._build_embedder()
        logger.info(
            "FAISS index loaded | vectors={} version={}",
            result.vectors,
            (result.version or "legacy")[:12],
        )

    async def reload(self, force: bool = False) -> ReloadResult:
        """Validate a snapshot and atomically replace the in-memory index."""
        async with self._reload_lock:
            manifest = await asyncio.to_thread(self._read_manifest)
            version = manifest.get("version") if manifest else None
            if not force and version and version == self._version:
                return ReloadResult(
                    False,
                    self._version,
                    self._index.ntotal if self._index else 0,
                )

            index_path, meta_path, tmp_dir = await asyncio.to_thread(self._resolve_paths)
            try:
                index, chunks = await asyncio.to_thread(
                    self._load_candidate, index_path, meta_path, manifest
                )
            finally:
                if tmp_dir:
                    shutil.rmtree(tmp_dir, ignore_errors=True)
            async with self._state_lock:
                self._index = index
                self._chunks = chunks
                self._version = version
            logger.info(
                "FAISS snapshot activated | vectors={} chunks={} version={}",
                index.ntotal,
                len(chunks),
                (version or "legacy")[:12],
            )
            return ReloadResult(True, version, index.ntotal)

    def _read_manifest(self) -> dict | None:
        if self._settings.faiss_source == FaissSource.LOCAL:
            path = Path(self._settings.faiss_index_path).with_name("version.json")
            return json.loads(path.read_text()) if path.exists() else None

        import boto3  # noqa: PLC0415
        from botocore.exceptions import ClientError  # noqa: PLC0415

        s3 = boto3.client(
            "s3",
            aws_access_key_id=self._settings.aws_access_key_id,
            aws_secret_access_key=self._settings.aws_secret_access_key,
            region_name=self._settings.aws_region,
        )
        try:
            response = s3.get_object(
                Bucket=self._settings.s3_bucket,
                Key=self._settings.s3_version_key,
            )
        except ClientError as exc:
            if exc.response["Error"]["Code"] in {"NoSuchKey", "404"}:
                return None
            raise
        return json.loads(response["Body"].read())

    @staticmethod
    def _load_candidate(index_path: str, meta_path: str, manifest: dict | None):
        index_bytes = Path(index_path).read_bytes()
        meta_bytes = Path(meta_path).read_bytes()
        if manifest:
            artifacts = manifest.get("artifacts", {})
            expected_index = artifacts.get("faiss.index", {}).get("sha256")
            expected_meta = artifacts.get("chunks_meta.json", {}).get("sha256")
            if expected_index and hashlib.sha256(index_bytes).hexdigest() != expected_index:
                raise ValueError("faiss.index checksum does not match version.json")
            if expected_meta and hashlib.sha256(meta_bytes).hexdigest() != expected_meta:
                raise ValueError("chunks_meta.json checksum does not match version.json")

        index = faiss.read_index(index_path)
        meta = json.loads(meta_bytes)
        chunks = [item if isinstance(item, str) else item["text"] for item in meta]
        if index.ntotal != len(chunks):
            raise ValueError(
                f"FAISS vectors ({index.ntotal}) do not match metadata chunks ({len(chunks)})"
            )
        return index, chunks

    def _resolve_paths(self) -> tuple[str, str, str | None]:
        if self._settings.faiss_source == FaissSource.LOCAL:
            return (
                self._settings.faiss_index_path,
                self._settings.faiss_meta_path,
                None,
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
        try:
            s3.download_file(self._settings.s3_bucket, self._settings.s3_index_key, index_path)
            s3.download_file(self._settings.s3_bucket, self._settings.s3_meta_key, meta_path)
        except Exception:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            raise
        return index_path, meta_path, tmp_dir

    def _build_embedder(self) -> AsyncOpenAI:
        logger.info("Embedding via OpenAI API | model={}", self._settings.openai_embedding_model)
        return AsyncOpenAI(api_key=self._settings.openai_api_key)

    # ── Query ─────────────────────────────────────────────────────────────────

    async def search(self, query: str) -> SearchResult:
        """
        Embed query via OpenAI API and return top-K most similar chunks.
        If the best score is below RAG_MIN_SIMILARITY, marks result as not relevant.
        """
        if self._embedder is None:
            raise RuntimeError("RAGEngine.load() must be called before search()")

        async with self._state_lock:
            index = self._index
            chunks = self._chunks
        if index is None:
            raise RuntimeError("RAGEngine.load() must be called before search()")

        response = await self._embedder.embeddings.create(
            model=self._settings.openai_embedding_model,
            input=query,
        )
        raw = np.array(response.data[0].embedding, dtype=np.float32)
        raw /= np.linalg.norm(raw)
        vec = raw.reshape(1, -1)
        k = min(self._settings.rag_top_k, index.ntotal)
        if k == 0:
            return SearchResult(chunks=[], scores=[], is_relevant=False)

        scores, indices = index.search(vec, k)
        scores = scores[0].tolist()
        indices = indices[0].tolist()

        valid_chunks = []
        valid_scores = []
        for score, idx in zip(scores, indices, strict=True):
            if idx == -1:
                continue
            valid_chunks.append(chunks[idx])
            valid_scores.append(float(score))

        is_relevant = bool(valid_scores and valid_scores[0] >= self._settings.rag_min_similarity)

        logger.debug(
            "RAG search | query_preview='{}' top_score={:.3f} relevant={}",
            query[:60],
            valid_scores[0] if valid_scores else 0.0,
            is_relevant,
        )
        return SearchResult(chunks=valid_chunks, scores=valid_scores, is_relevant=is_relevant)

    @property
    def version(self) -> str | None:
        return self._version

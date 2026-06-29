"""Storage backends for indexer output artifacts (faiss.index, chunks_meta.json, embed_cache.json)."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class StorageBackend(Protocol):
    def write(self, filename: str, data: bytes) -> None: ...
    def read(self, filename: str) -> bytes | None: ...


class LocalStorage:
    def __init__(self, out_dir: Path) -> None:
        self._dir = out_dir
        out_dir.mkdir(parents=True, exist_ok=True)

    def write(self, filename: str, data: bytes) -> None:
        (self._dir / filename).write_bytes(data)

    def read(self, filename: str) -> bytes | None:
        p = self._dir / filename
        return p.read_bytes() if p.exists() else None


class S3Storage:
    def __init__(self, bucket: str, prefix: str = "faiss") -> None:
        import boto3  # noqa: PLC0415

        self._bucket = bucket
        self._prefix = prefix.rstrip("/")
        self._s3 = boto3.client("s3")

    def _key(self, filename: str) -> str:
        return f"{self._prefix}/{filename}"

    def write(self, filename: str, data: bytes) -> None:
        from loguru import logger  # noqa: PLC0415

        key = self._key(filename)
        self._s3.put_object(Bucket=self._bucket, Key=key, Body=data)
        logger.info("S3 upload: s3://{}/{}", self._bucket, key)

    def read(self, filename: str) -> bytes | None:
        from botocore.exceptions import ClientError  # noqa: PLC0415
        from loguru import logger  # noqa: PLC0415

        key = self._key(filename)
        try:
            resp = self._s3.get_object(Bucket=self._bucket, Key=key)
            data = resp["Body"].read()
            logger.info("S3 download: s3://{}/{} ({} bytes)", self._bucket, key, len(data))
            return data
        except ClientError as e:
            if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
                return None
            raise

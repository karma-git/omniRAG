"""Authenticated internal HTTP endpoint for atomic FAISS hot reloads."""

from __future__ import annotations

import asyncio
import hmac

import uvicorn
from fastapi import FastAPI, Header, HTTPException, Query
from loguru import logger

from app.core.config import Settings
from app.core.rag_engine import RAGEngine


class ReloadServer:
    def __init__(self, rag: RAGEngine, settings: Settings) -> None:
        self._rag = rag
        self._settings = settings
        self._app = self._build_app()

    def _authorize(self, authorization: str | None) -> None:
        expected = f"Bearer {self._settings.hot_reload_token}"
        if not authorization or not hmac.compare_digest(authorization, expected):
            raise HTTPException(status_code=401, detail="invalid reload token")

    def _build_app(self) -> FastAPI:
        app = FastAPI(title="OmniRAG reload API", docs_url=None, redoc_url=None)

        @app.get("/health")
        async def health():
            return {"status": "ok", "index_version": self._rag.version}

        @app.post("/internal/reload")
        async def reload_index(
            force: bool = Query(default=False),
            authorization: str | None = Header(default=None),
        ):
            self._authorize(authorization)
            try:
                result = await self._rag.reload(force=force)
            except Exception as exc:
                logger.exception("FAISS hot reload failed; previous snapshot remains active")
                raise HTTPException(status_code=503, detail="reload failed") from exc
            return {
                "changed": result.changed,
                "version": result.version,
                "vectors": result.vectors,
            }

        return app

    async def start(self) -> None:
        config = uvicorn.Config(
            self._app,
            host=self._settings.hot_reload_host,
            port=self._settings.hot_reload_port,
            log_level="info",
        )
        await uvicorn.Server(config).serve()

    async def watch(self) -> None:
        """Poll the cheap manifest so every replica eventually reloads itself."""
        interval = self._settings.hot_reload_poll_interval_seconds
        if interval == 0:
            return
        while True:
            await asyncio.sleep(interval)
            try:
                await self._rag.reload()
            except Exception:
                logger.exception(
                    "Automatic FAISS reload failed; previous snapshot remains active"
                )

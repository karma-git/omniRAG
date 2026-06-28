"""
Web channel — FastAPI + Jinja2.

Exposes:
  GET  /           → chat UI (Jinja2 template)
  POST /api/chat   → {"query": "..."} → {"response": "..."}
  GET  /api/health        → {"status": "ok"}
  GET  /api/system-prompt → {"content": "...", "source": "file|env"}

The same HTML page is used as a Telegram Mini App by pointing
the bot's menu_button or inline_button at the hosted URL.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from loguru import logger
from pydantic import BaseModel

from app.channels.base import BaseChannel, OrchestratorFn
from app.core.config import Settings

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


class _ChatRequest(BaseModel):
    query: str


class _ChatResponse(BaseModel):
    response: str


class _FeedbackRequest(BaseModel):
    sentiment: Literal["like", "dislike"]
    query: str
    response: str


class WebChannel(BaseChannel):
    def __init__(
        self, on_message: OrchestratorFn, settings: Settings, system_prompt: str = ""
    ) -> None:
        super().__init__(on_message)
        self._settings = settings
        self._system_prompt = system_prompt
        self._system_prompt_source = settings.system_prompt_path or "RAG_DOMAIN_DESCRIPTION env var"
        self._app = self._build_app()

    def _build_app(self) -> FastAPI:
        app = FastAPI(title="OmniRAG", docs_url="/api/docs", redoc_url=None)
        templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

        @app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            return templates.TemplateResponse(request, "index.html")

        @app.get("/api/health")
        async def health():
            return {"status": "ok"}

        @app.get("/api/system-prompt")
        async def system_prompt():
            return {
                "content": self._system_prompt,
                "source": self._system_prompt_source,
            }

        @app.post("/api/chat", response_model=_ChatResponse)
        async def chat(body: _ChatRequest):
            response = await self._on_message(body.query)
            return _ChatResponse(response=response)

        @app.post("/api/feedback")
        async def feedback(body: _FeedbackRequest):
            logger.info(
                "Feedback | sentiment={} query={:.80} response={:.80}",
                body.sentiment,
                body.query,
                body.response,
            )
            return {"ok": True}

        return app

    async def start(self) -> None:
        config = uvicorn.Config(
            self._app,
            host=self._settings.web_host,
            port=self._settings.web_port,
            log_level="info",
        )
        server = uvicorn.Server(config)
        await server.serve()

    async def send_message(
        self,
        target_id: str,
        text: str,
        thread_id: str | None = None,
    ) -> None:
        # HTTP is request-response; push is not applicable for this channel.
        pass

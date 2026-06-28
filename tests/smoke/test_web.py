"""
Smoke tests for WebChannel — no external APIs, no real FAISS index.

Uses FastAPI TestClient with a mock orchestrator to verify that all
HTTP endpoints exist, accept correct payloads, and return expected shapes.
"""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client() -> TestClient:
    from app.channels.web import WebChannel

    settings = MagicMock()
    settings.system_prompt_path = "user/system-prompt.md"

    async def _mock_orchestrator(query: str) -> str:
        return f"Answer: {query}"

    channel = WebChannel(
        on_message=_mock_orchestrator,
        settings=settings,
        system_prompt="You are a test assistant.",
    )
    return TestClient(channel._app)


# ── GET / ─────────────────────────────────────────────────────────────────────


def test_index_returns_html(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "OmniRAG" in r.text


# ── GET /api/health ───────────────────────────────────────────────────────────


def test_health(client: TestClient) -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# ── POST /api/chat ────────────────────────────────────────────────────────────


def test_chat_returns_response(client: TestClient) -> None:
    r = client.post("/api/chat", json={"query": "Hello"})
    assert r.status_code == 200
    data = r.json()
    assert "response" in data
    assert "Answer: Hello" in data["response"]


def test_chat_missing_query_is_422(client: TestClient) -> None:
    r = client.post("/api/chat", json={})
    assert r.status_code == 422


def test_chat_empty_body_is_422(client: TestClient) -> None:
    r = client.post("/api/chat")
    assert r.status_code == 422


# ── GET /api/system-prompt ────────────────────────────────────────────────────


def test_system_prompt_shape(client: TestClient) -> None:
    r = client.get("/api/system-prompt")
    assert r.status_code == 200
    data = r.json()
    assert data["content"] == "You are a test assistant."
    assert "source" in data


# ── POST /api/feedback ────────────────────────────────────────────────────────


def test_feedback_like(client: TestClient) -> None:
    r = client.post(
        "/api/feedback",
        json={
            "sentiment": "like",
            "query": "test query",
            "response": "test response",
        },
    )
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_feedback_dislike(client: TestClient) -> None:
    r = client.post(
        "/api/feedback",
        json={
            "sentiment": "dislike",
            "query": "q",
            "response": "r",
        },
    )
    assert r.status_code == 200


def test_feedback_invalid_sentiment_is_422(client: TestClient) -> None:
    r = client.post(
        "/api/feedback",
        json={
            "sentiment": "meh",
            "query": "q",
            "response": "r",
        },
    )
    assert r.status_code == 422

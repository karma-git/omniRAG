from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.core.rag_engine import ReloadResult
from app.core.reload_server import ReloadServer


def _client():
    rag = MagicMock()
    rag.version = "old"
    rag.reload = AsyncMock(return_value=ReloadResult(True, "new", 12))
    settings = MagicMock()
    settings.hot_reload_token = "secret"
    server = ReloadServer(rag, settings)
    return TestClient(server._app), rag


def test_reload_requires_bearer_token() -> None:
    client, rag = _client()
    response = client.post("/internal/reload")
    assert response.status_code == 401
    rag.reload.assert_not_awaited()


def test_reload_activates_snapshot() -> None:
    client, rag = _client()
    response = client.post(
        "/internal/reload",
        headers={"Authorization": "Bearer secret"},
    )
    assert response.status_code == 200
    assert response.json() == {"changed": True, "version": "new", "vectors": 12}
    rag.reload.assert_awaited_once_with(force=False)

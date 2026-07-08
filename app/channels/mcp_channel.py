"""
MCP channel — exposes OmniRAG as a Model Context Protocol server.

Transports:
  stdio          — Claude Desktop spawns this process directly (default)
  sse            — HTTP SSE server, useful for Docker / remote clients

Tool exposed:
  ask(query: str) → str
    Full RAG pipeline: retrieval + generation inside OmniRAG.
    The client model receives a ready answer, not raw chunks.

Claude Desktop config (stdio):
  {
    "mcpServers": {
      "omnirag": {
        "command": "uv",
        "args": ["run", "python", "-m", "app.main"],
        "env": {"CHAT_PROVIDER": "mcp", "OPENAI_API_KEY": "...", ...}
      }
    }
  }

Claude Desktop config (SSE, running omnirag-mcp container):
  {
    "mcpServers": {
      "omnirag": {"url": "http://localhost:8001/sse"}
    }
  }
"""

from mcp.server.fastmcp import FastMCP

from app.channels.base import BaseChannel, OrchestratorFn
from app.core.config import Settings


class MCPChannel(BaseChannel):
    def __init__(self, on_message: OrchestratorFn, settings: Settings) -> None:
        super().__init__(on_message)
        self._transport = settings.mcp_transport
        self._server = FastMCP(
            "OmniRAG",
            instructions=(
                "Knowledge base assistant. "
                "Use the `ask` tool to query indexed documents — "
                "it returns a complete answer, not raw chunks."
            ),
            host=settings.mcp_host,
            port=settings.mcp_port,
        )

        @self._server.tool()
        async def ask(query: str) -> str:
            """Query the OmniRAG knowledge base and get a complete answer."""
            return await self._on_message(query)

    async def start(self) -> None:
        if self._transport == "sse":
            await self._server.run_sse_async()
        else:
            await self._server.run_stdio_async()

    async def send_message(
        self,
        target_id: str,
        text: str,
        thread_id: str | None = None,
    ) -> None:
        pass

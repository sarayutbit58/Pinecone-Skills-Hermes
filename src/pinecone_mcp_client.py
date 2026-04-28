from __future__ import annotations

from typing import Any


class PineconeMcpClient:
    """Placeholder MCP client.

    NOTE: This is a stub implementation. Real MCP integration depends on the
    exact Pinecone MCP server API and transport (HTTP / stdio / tool runtime).
    """

    def __init__(self, config: Any) -> None:
        self.config = config

    def query(self, vector, top_k, include_metadata=True):
        raise NotImplementedError("MCP client not implemented yet")

    def upsert(self, records):
        raise NotImplementedError("MCP client not implemented yet")

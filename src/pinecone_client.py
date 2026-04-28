from __future__ import annotations

from typing import Any, Protocol


class PineconeSkillClient(Protocol):
    """Transport interface used by router and indexer.

    Implementations may use the Pinecone Python SDK, Pinecone MCP, or another
    transport. Keeping this interface small preserves the core objective of the
    project: Hermes skill selection logic stays independent from Pinecone access
    details.
    """

    def query(self, vector: list[float], top_k: int, include_metadata: bool = True) -> dict[str, Any]:
        ...

    def upsert(self, records: list[tuple[str, list[float], dict[str, Any]]]) -> Any:
        ...


def build_pinecone_client(config: Any) -> PineconeSkillClient:
    transport = getattr(config.pinecone, "transport", "sdk")

    if transport == "mcp":
        from .pinecone_mcp_client import PineconeMcpClient

        return PineconeMcpClient(config)

    from .pinecone_sdk_client import PineconeSdkClient

    return PineconeSdkClient(config)

from __future__ import annotations

from typing import Any

from pinecone import Pinecone


class PineconeSdkError(RuntimeError):
    """Raised when the Pinecone SDK transport fails."""


class PineconeSdkClient:
    def __init__(self, config: Any) -> None:
        self.namespace = config.pinecone.namespace
        try:
            self._pc = Pinecone(api_key=config.pinecone.api_key)
            self._index = self._pc.Index(config.pinecone.index_name)
        except Exception as exc:
            raise PineconeSdkError(
                f"Failed to initialize Pinecone index '{config.pinecone.index_name}'."
            ) from exc

    def query(self, vector, top_k, include_metadata=True):
        try:
            return self._index.query(
                vector=vector,
                top_k=top_k,
                include_metadata=include_metadata,
                namespace=self.namespace,
            )
        except Exception as exc:
            raise PineconeSdkError("Pinecone query failed.") from exc

    def upsert(self, records):
        try:
            return self._index.upsert(vectors=records, namespace=self.namespace)
        except Exception as exc:
            raise PineconeSdkError("Pinecone upsert failed.") from exc

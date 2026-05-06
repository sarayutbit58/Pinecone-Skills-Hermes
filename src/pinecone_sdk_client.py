from __future__ import annotations

from typing import Any

from pinecone import Pinecone


class PineconeSdkClient:
    def __init__(self, config: Any) -> None:
        self._index_name = config.pinecone.index_name
        self._pc = Pinecone(api_key=config.pinecone.api_key)
        self._index = self._pc.Index(self._index_name)

    def query(self, vector, top_k, include_metadata=True):
        try:
            return self._index.query(vector=vector, top_k=top_k, include_metadata=include_metadata)
        except Exception as exc:
            raise RuntimeError(f"Pinecone query failed for index '{self._index_name}'") from exc

    def upsert(self, records):
        try:
            return self._index.upsert(vectors=records)
        except Exception as exc:
            raise RuntimeError(f"Pinecone upsert failed for index '{self._index_name}'") from exc

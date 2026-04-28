from __future__ import annotations

from typing import Any

from pinecone import Pinecone


class PineconeSdkClient:
    def __init__(self, config: Any) -> None:
        self._pc = Pinecone(api_key=config.pinecone.api_key)
        self._index = self._pc.Index(config.pinecone.index_name)

    def query(self, vector, top_k, include_metadata=True):
        return self._index.query(vector=vector, top_k=top_k, include_metadata=include_metadata)

    def upsert(self, records):
        return self._index.upsert(vectors=records)

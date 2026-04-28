from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class JsonCache:
    """Tiny file-backed JSON cache for free-tier optimization.

    Used for query embeddings, routing results, and skill content hashes so the
    plugin does not spend Pinecone read/write units or embedding tokens when the
    same work has already been done.
    """

    def __init__(self, path: str, ttl_seconds: int = 86400) -> None:
        self.path = Path(os.path.expanduser(path))
        self.ttl_seconds = ttl_seconds
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save(self) -> None:
        self.path.write_text(json.dumps(self._data, indent=2, sort_keys=True), encoding="utf-8")

    def get(self, key: str) -> Any | None:
        item = self._data.get(key)
        if not item:
            return None
        ts = item.get("ts", 0)
        if self.ttl_seconds > 0 and time.time() - ts > self.ttl_seconds:
            self._data.pop(key, None)
            return None
        return item.get("value")

    def set(self, key: str, value: Any) -> None:
        self._data[key] = {"ts": time.time(), "value": value}
        self.save()

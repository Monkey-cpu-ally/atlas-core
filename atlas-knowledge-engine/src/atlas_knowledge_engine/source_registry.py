"""Traceable source registry for the ATLAS learning engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import RLock
from typing import Any


@dataclass(frozen=True, slots=True)
class SourceRecord:
    source_type: str
    source_id: str
    title: str
    content_hash: str
    canonical_url: str | None = None
    creator: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    registered_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class SourceRegistry:
    """Thread-safe in-memory source registry.

    Persistence can be swapped in later without changing the learning pipeline.
    """

    def __init__(self) -> None:
        self._by_identity: dict[tuple[str, str], SourceRecord] = {}
        self._by_hash: dict[str, SourceRecord] = {}
        self._lock = RLock()

    @staticmethod
    def _identity(source_type: str, source_id: str) -> tuple[str, str]:
        normalized_type = source_type.strip().lower()
        normalized_id = source_id.strip()
        if not normalized_type or not normalized_id:
            raise ValueError("source_type and source_id are required")
        return normalized_type, normalized_id

    def register(self, record: SourceRecord, *, replace: bool = False) -> SourceRecord:
        identity = self._identity(record.source_type, record.source_id)
        if not record.content_hash.strip():
            raise ValueError("content_hash is required")

        with self._lock:
            existing = self._by_identity.get(identity)
            if existing is not None and not replace:
                raise KeyError(f"source already registered: {identity[0]}:{identity[1]}")

            hash_match = self._by_hash.get(record.content_hash)
            if hash_match is not None and hash_match != existing and not replace:
                raise KeyError(
                    "content hash already registered by "
                    f"{hash_match.source_type}:{hash_match.source_id}"
                )

            if existing is not None:
                self._by_hash.pop(existing.content_hash, None)

            self._by_identity[identity] = record
            self._by_hash[record.content_hash] = record
            return record

    def get(self, source_type: str, source_id: str) -> SourceRecord:
        identity = self._identity(source_type, source_id)
        with self._lock:
            try:
                return self._by_identity[identity]
            except KeyError as exc:
                raise KeyError(f"source not registered: {identity[0]}:{identity[1]}") from exc

    def find_by_hash(self, content_hash: str) -> SourceRecord | None:
        with self._lock:
            return self._by_hash.get(content_hash.strip())

    def contains_identity(self, source_type: str, source_id: str) -> bool:
        identity = self._identity(source_type, source_id)
        with self._lock:
            return identity in self._by_identity

    def records(self) -> tuple[SourceRecord, ...]:
        with self._lock:
            return tuple(self._by_identity[key] for key in sorted(self._by_identity))

    def health(self) -> dict[str, object]:
        with self._lock:
            return {
                "status": "healthy",
                "sources": len(self._by_identity),
                "content_hashes": len(self._by_hash),
            }

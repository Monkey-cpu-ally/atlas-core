"""Duplicate detection for normalized ATLAS learning content."""

from __future__ import annotations

from dataclasses import dataclass

from .source_registry import SourceRecord, SourceRegistry


@dataclass(frozen=True, slots=True)
class DuplicateMatch:
    reason: str
    existing: SourceRecord


class DuplicateDetector:
    """Detect duplicate source identities and duplicate content hashes."""

    def __init__(self, registry: SourceRegistry) -> None:
        self.registry = registry

    def find(
        self,
        *,
        source_type: str,
        source_id: str,
        content_hash: str,
    ) -> DuplicateMatch | None:
        if self.registry.contains_identity(source_type, source_id):
            return DuplicateMatch(
                reason="source_identity",
                existing=self.registry.get(source_type, source_id),
            )

        existing = self.registry.find_by_hash(content_hash)
        if existing is not None:
            return DuplicateMatch(reason="content_hash", existing=existing)
        return None

    def health(self) -> dict[str, object]:
        return {"status": "healthy", "registry": self.registry.health()}

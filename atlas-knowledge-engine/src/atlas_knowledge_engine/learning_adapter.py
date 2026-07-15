"""Replaceable source-adapter contracts for the ATLAS learning engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class LearningSource:
    """A source submitted to the universal learning pipeline."""

    source_type: str
    locator: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ExtractedContent:
    """Normalized content returned by a source adapter."""

    source_type: str
    source_id: str
    title: str
    text: str
    canonical_url: str | None = None
    creator: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class LearningAdapter(Protocol):
    """Contract implemented by YouTube, GitHub, PDF, and future adapters."""

    source_type: str

    def can_handle(self, source: LearningSource) -> bool: ...

    def validate(self, source: LearningSource) -> None: ...

    def extract(self, source: LearningSource) -> ExtractedContent: ...


class AdapterRegistry:
    """Registry for replaceable learning adapters keyed by source type."""

    def __init__(self) -> None:
        self._adapters: dict[str, LearningAdapter] = {}

    def register(self, adapter: LearningAdapter, *, replace: bool = False) -> None:
        source_type = adapter.source_type.strip().lower()
        if not source_type:
            raise ValueError("adapter source_type cannot be empty")
        if source_type in self._adapters and not replace:
            raise KeyError(f"adapter already registered: {source_type}")
        self._adapters[source_type] = adapter

    def get(self, source_type: str) -> LearningAdapter:
        normalized = source_type.strip().lower()
        try:
            return self._adapters[normalized]
        except KeyError as exc:
            raise KeyError(f"no learning adapter registered for: {normalized}") from exc

    def resolve(self, source: LearningSource) -> LearningAdapter:
        direct = self._adapters.get(source.source_type.strip().lower())
        if direct is not None and direct.can_handle(source):
            return direct
        for adapter in self._adapters.values():
            if adapter.can_handle(source):
                return adapter
        raise KeyError(f"no learning adapter can handle: {source.locator}")

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._adapters))

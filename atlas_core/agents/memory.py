from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(slots=True, frozen=True)
class MemoryEntry:
    key: str
    value: Any
    author: str
    scope: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MemoryAccessError(PermissionError):
    pass


class AtlasMemory:
    def __init__(self) -> None:
        self._global: dict[str, MemoryEntry] = {}
        self._private: dict[str, dict[str, MemoryEntry]] = {}

    def remember_global(self, key: str, value: Any, author: str) -> MemoryEntry:
        entry = MemoryEntry(key, value, author, "global")
        self._global[key] = entry
        return entry

    def remember_private(self, agent: str, key: str, value: Any) -> MemoryEntry:
        entry = MemoryEntry(key, value, agent, f"private:{agent}")
        self._private.setdefault(agent, {})[key] = entry
        return entry

    def recall(self, key: str, requester: str, owner: str | None = None) -> MemoryEntry | None:
        if owner is None:
            return self._global.get(key)
        if requester != owner:
            raise MemoryAccessError(f"{requester} cannot read {owner}'s private memory")
        return self._private.get(owner, {}).get(key)

    def search_global(self, text: str) -> list[MemoryEntry]:
        needle = text.lower()
        return [entry for entry in self._global.values() if needle in entry.key.lower() or needle in str(entry.value).lower()]

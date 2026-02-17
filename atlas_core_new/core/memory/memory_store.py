"""
atlas_core/core/memory/memory_store.py

Simple in-memory store.
"""

from typing import Dict, List, Optional

from .memory_models import MemoryItem, MemoryEntry, MemorySnapshot


class SimpleMemoryStore:
    """
    Simple in-memory store. Replace with DB later.
    """
    def __init__(self):
        self._items: Dict[str, MemoryItem] = {}
        self._transcript: List[MemoryEntry] = []

    def add_entry(self, entry: MemoryEntry) -> None:
        self._transcript.append(entry)

    def upsert_item(self, item: MemoryItem) -> None:
        self._items[item.key] = item

    def get_item(self, key: str) -> Optional[MemoryItem]:
        return self._items.get(key)

    def snapshot(self) -> MemorySnapshot:
        return MemorySnapshot(items=list(self._items.values()), transcript=list(self._transcript))

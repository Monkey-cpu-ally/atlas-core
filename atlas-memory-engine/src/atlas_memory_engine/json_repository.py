"""JSON-backed memory repository."""

from __future__ import annotations

from dataclasses import dataclass

from atlas_persistence.json_store import JsonFileStore

from .models import MemoryRecord


@dataclass
class JsonMemoryRepository:
    """Persist memory records to a JSON collection."""

    store: JsonFileStore
    collection: str = "memory_records"

    def save(self, record: MemoryRecord) -> MemoryRecord:
        self.store.append_record(self.collection, record)
        return record

    def list_all(self) -> list[dict[str, object]]:
        return self.store.read_collection(self.collection)

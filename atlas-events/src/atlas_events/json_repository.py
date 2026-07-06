"""JSON-backed event repository."""

from __future__ import annotations

from dataclasses import dataclass

from atlas_persistence.json_store import JsonFileStore

from .models import AtlasEvent


@dataclass
class JsonEventRepository:
    """Persist event records to a JSON collection."""

    store: JsonFileStore
    collection: str = "events"

    def save(self, event: AtlasEvent) -> AtlasEvent:
        self.store.append_record(self.collection, event)
        return event

    def list_all(self) -> list[dict[str, object]]:
        return self.store.read_collection(self.collection)

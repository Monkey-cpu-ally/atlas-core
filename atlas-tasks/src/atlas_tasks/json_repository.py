"""JSON-backed task repository."""

from __future__ import annotations

from dataclasses import dataclass

from atlas_persistence.json_store import JsonFileStore

from .models import AtlasTask


@dataclass
class JsonTaskRepository:
    """Persist task records to a JSON collection."""

    store: JsonFileStore
    collection: str = "tasks"

    def save(self, task: AtlasTask) -> AtlasTask:
        self.store.append_record(self.collection, task)
        return task

    def list_all(self) -> list[dict[str, object]]:
        return self.store.read_collection(self.collection)

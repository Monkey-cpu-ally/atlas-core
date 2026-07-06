"""JSON-backed repositories for ATLAS knowledge."""

from __future__ import annotations

from dataclasses import dataclass

from atlas_persistence.json_store import JsonFileStore

from .models import KnowledgeEntry, SourcePassport


@dataclass
class JsonSourceRepository:
    """Persist source passports to a JSON collection."""

    store: JsonFileStore
    collection: str = "source_passports"

    def save(self, source: SourcePassport) -> SourcePassport:
        self.store.append_record(self.collection, source)
        return source

    def list_all(self) -> list[dict[str, object]]:
        return self.store.read_collection(self.collection)


@dataclass
class JsonKnowledgeRepository:
    """Persist knowledge entries to a JSON collection."""

    store: JsonFileStore
    collection: str = "knowledge_entries"

    def save(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        self.store.append_record(self.collection, entry)
        return entry

    def list_all(self) -> list[dict[str, object]]:
        return self.store.read_collection(self.collection)

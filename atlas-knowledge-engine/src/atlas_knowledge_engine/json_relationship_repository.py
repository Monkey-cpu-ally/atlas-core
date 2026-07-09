"""JSON-backed repositories for ATLAS knowledge relationships."""

from __future__ import annotations

from dataclasses import dataclass

from atlas_persistence.json_store import JsonFileStore

from .relationships import KnowledgeNode, KnowledgeRelationship


@dataclass
class JsonKnowledgeNodeRepository:
    """Persist knowledge nodes to JSON."""

    store: JsonFileStore
    collection: str = "knowledge_nodes"

    def save(self, node: KnowledgeNode) -> KnowledgeNode:
        self.store.append_record(self.collection, node)
        return node

    def list_all(self) -> list[dict[str, object]]:
        return self.store.read_collection(self.collection)


@dataclass
class JsonKnowledgeRelationshipRepository:
    """Persist knowledge relationships to JSON."""

    store: JsonFileStore
    collection: str = "knowledge_relationships"

    def save(self, relationship: KnowledgeRelationship) -> KnowledgeRelationship:
        self.store.append_record(self.collection, relationship)
        return relationship

    def list_all(self) -> list[dict[str, object]]:
        return self.store.read_collection(self.collection)

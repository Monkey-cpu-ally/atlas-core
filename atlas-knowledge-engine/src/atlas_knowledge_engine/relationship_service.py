"""Service for managing ATLAS knowledge relationships."""

from __future__ import annotations

from dataclasses import dataclass, field

from .relationship_repository import KnowledgeNodeRepository, KnowledgeRelationshipRepository
from .relationships import (
    KnowledgeNode,
    KnowledgeNodeType,
    KnowledgeRelationship,
    KnowledgeRelationshipType,
)


@dataclass
class KnowledgeRelationshipService:
    """Creates and queries knowledge nodes and relationships."""

    node_repository: KnowledgeNodeRepository | None = None
    relationship_repository: KnowledgeRelationshipRepository | None = None
    _nodes: dict[str, KnowledgeNode] = field(default_factory=dict)
    _relationships: dict[str, KnowledgeRelationship] = field(default_factory=dict)

    def create_node(
        self,
        title: str,
        node_type: KnowledgeNodeType,
        external_id: str | None = None,
        summary: str = "",
        tags: list[str] | None = None,
    ) -> KnowledgeNode:
        node = KnowledgeNode(
            title=title,
            node_type=node_type,
            external_id=external_id,
            summary=summary,
            tags=tags or [],
        )
        self._nodes[node.node_id] = node
        if self.node_repository is not None:
            self.node_repository.save(node)
        return node

    def connect(
        self,
        from_node_id: str,
        to_node_id: str,
        relationship_type: KnowledgeRelationshipType,
        reason: str,
        confidence: float = 0.5,
        evidence_source_ids: list[str] | None = None,
        created_by: str = "atlas-knowledge-engine",
    ) -> KnowledgeRelationship:
        if from_node_id not in self._nodes:
            raise KeyError(f"Unknown from_node_id: {from_node_id}")
        if to_node_id not in self._nodes:
            raise KeyError(f"Unknown to_node_id: {to_node_id}")
        relationship = KnowledgeRelationship(
            from_node_id=from_node_id,
            to_node_id=to_node_id,
            relationship_type=relationship_type,
            reason=reason,
            confidence=confidence,
            evidence_source_ids=evidence_source_ids or [],
            created_by=created_by,
        )
        self._relationships[relationship.relationship_id] = relationship
        if self.relationship_repository is not None:
            self.relationship_repository.save(relationship)
        return relationship

    def get_node(self, node_id: str) -> KnowledgeNode:
        return self._nodes[node_id]

    def list_nodes(self, node_type: KnowledgeNodeType | None = None) -> list[KnowledgeNode]:
        nodes = list(self._nodes.values())
        if node_type is not None:
            nodes = [node for node in nodes if node.node_type == node_type]
        return nodes

    def list_relationships(
        self,
        relationship_type: KnowledgeRelationshipType | None = None,
    ) -> list[KnowledgeRelationship]:
        relationships = list(self._relationships.values())
        if relationship_type is not None:
            relationships = [
                relationship
                for relationship in relationships
                if relationship.relationship_type == relationship_type
            ]
        return relationships

    def related_to(self, node_id: str) -> list[KnowledgeRelationship]:
        return [
            relationship
            for relationship in self._relationships.values()
            if relationship.from_node_id == node_id or relationship.to_node_id == node_id
        ]

    def outbound_from(self, node_id: str) -> list[KnowledgeRelationship]:
        return [
            relationship
            for relationship in self._relationships.values()
            if relationship.from_node_id == node_id
        ]

    def inbound_to(self, node_id: str) -> list[KnowledgeRelationship]:
        return [
            relationship
            for relationship in self._relationships.values()
            if relationship.to_node_id == node_id
        ]

    def persisted_nodes(self) -> list[dict[str, object]]:
        if self.node_repository is None:
            return []
        return self.node_repository.list_all()

    def persisted_relationships(self) -> list[dict[str, object]]:
        if self.relationship_repository is None:
            return []
        return self.relationship_repository.list_all()

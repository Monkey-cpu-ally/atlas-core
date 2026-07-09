"""Tests for ATLAS Knowledge Relationship Engine."""

from atlas_knowledge_engine.json_relationship_repository import (
    JsonKnowledgeNodeRepository,
    JsonKnowledgeRelationshipRepository,
)
from atlas_knowledge_engine.relationship_service import KnowledgeRelationshipService
from atlas_knowledge_engine.relationships import KnowledgeNodeType, KnowledgeRelationshipType
from atlas_persistence.json_store import JsonFileStore


def test_knowledge_relationship_service_can_connect_project_to_banks_and_sources():
    service = KnowledgeRelationshipService()

    project = service.create_node(
        title="Mother Box",
        node_type=KnowledgeNodeType.PROJECT,
        summary="Adaptive manufacturing concept grounded in ATLAS research.",
    )
    robotics = service.create_node(
        title="Robotics",
        node_type=KnowledgeNodeType.KNOWLEDGE_BANK,
    )
    materials = service.create_node(
        title="Materials Science",
        node_type=KnowledgeNodeType.KNOWLEDGE_BANK,
    )
    source = service.create_node(
        title="Advanced Materials Source",
        node_type=KnowledgeNodeType.SOURCE,
    )

    service.connect(
        from_node_id=project.node_id,
        to_node_id=robotics.node_id,
        relationship_type=KnowledgeRelationshipType.APPLIES_TO,
        reason="The project requires robotics research.",
        confidence=0.9,
    )
    service.connect(
        from_node_id=project.node_id,
        to_node_id=materials.node_id,
        relationship_type=KnowledgeRelationshipType.APPLIES_TO,
        reason="The project depends on material behavior.",
        confidence=0.85,
    )
    service.connect(
        from_node_id=source.node_id,
        to_node_id=project.node_id,
        relationship_type=KnowledgeRelationshipType.SUPPORTS,
        reason="The source supports material selection research.",
        confidence=0.8,
    )

    assert len(service.list_nodes()) == 4
    assert len(service.related_to(project.node_id)) == 3
    assert len(service.outbound_from(project.node_id)) == 2
    assert len(service.inbound_to(project.node_id)) == 1


def test_knowledge_relationship_service_can_persist_nodes_and_relationships(tmp_path):
    store = JsonFileStore(tmp_path)
    service = KnowledgeRelationshipService(
        node_repository=JsonKnowledgeNodeRepository(store),
        relationship_repository=JsonKnowledgeRelationshipRepository(store),
    )

    project = service.create_node("Power Cell", KnowledgeNodeType.PROJECT)
    bank = service.create_node("Chemistry", KnowledgeNodeType.KNOWLEDGE_BANK)
    relationship = service.connect(
        from_node_id=project.node_id,
        to_node_id=bank.node_id,
        relationship_type=KnowledgeRelationshipType.APPLIES_TO,
        reason="The power cell depends on chemistry.",
        confidence=0.9,
    )

    persisted_nodes = service.persisted_nodes()
    persisted_relationships = service.persisted_relationships()

    assert len(persisted_nodes) == 2
    assert len(persisted_relationships) == 1
    assert persisted_nodes[0]["title"] == "Power Cell"
    assert persisted_relationships[0]["relationship_id"] == relationship.relationship_id
    assert persisted_relationships[0]["relationship_type"] == "applies_to"

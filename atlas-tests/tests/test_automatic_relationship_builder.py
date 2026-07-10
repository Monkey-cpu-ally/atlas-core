"""Tests for the ATLAS automatic relationship builder."""

from atlas_knowledge_engine.automatic_relationship_builder import AutomaticRelationshipBuilder
from atlas_knowledge_engine.relationship_service import KnowledgeRelationshipService
from atlas_knowledge_engine.relationships import KnowledgeNodeType, KnowledgeRelationshipType


def test_classifier_suggests_relevant_knowledge_banks():
    service = KnowledgeRelationshipService()
    builder = AutomaticRelationshipBuilder(service)

    result = builder.classify(
        title="Mini Oxygen Converter",
        text=(
            "A compact oxygen conversion system using chemical catalysts, sensors, "
            "electronics, air-quality monitoring, and manufacturable components."
        ),
    )

    banks = {suggestion.knowledge_bank for suggestion in result.suggestions}

    assert "Chemistry" in banks
    assert "Electronics" in banks
    assert "Environmental Science" in banks
    assert "Manufacturing" in banks
    assert all(0.0 <= suggestion.confidence <= 1.0 for suggestion in result.suggestions)
    assert all(suggestion.matched_terms for suggestion in result.suggestions)


def test_builder_creates_bank_nodes_and_relationships_automatically():
    service = KnowledgeRelationshipService()
    builder = AutomaticRelationshipBuilder(service)

    project = service.create_node(
        title="Power Cell",
        node_type=KnowledgeNodeType.PROJECT,
        summary="Electric-eel-inspired stacked energy cell.",
    )

    result = builder.apply_to_node(
        source_node=project,
        text=(
            "An energy storage project using electrolyte chemistry, voltage monitoring, "
            "electronics, materials, manufacturing, and cost analysis."
        ),
    )

    relationships = service.outbound_from(project.node_id)
    bank_nodes = service.list_nodes(KnowledgeNodeType.KNOWLEDGE_BANK)

    assert result.suggestions
    assert len(relationships) == len(result.suggestions)
    assert len(bank_nodes) == len(result.suggestions)
    assert all(
        relationship.relationship_type == KnowledgeRelationshipType.APPLIES_TO
        for relationship in relationships
    )
    assert all(relationship.created_by == "automatic-relationship-builder" for relationship in relationships)


def test_classifier_returns_no_suggestions_for_unmatched_text():
    service = KnowledgeRelationshipService()
    builder = AutomaticRelationshipBuilder(service)

    result = builder.classify("Unknown", "No recognized domain terms are present here.")

    assert result.suggestions == []

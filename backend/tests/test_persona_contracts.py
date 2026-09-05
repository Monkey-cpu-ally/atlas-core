"""Regression tests for the canonical ATLAS persona contracts."""

from services.knowledge_distiller import route_agent
from services.persona_chat import PERSONAS


def test_persona_registry_domains_are_not_swapped():
    assert "Engineering" in PERSONAS["ajani"].domain
    assert "Science" in PERSONAS["minerva"].domain
    assert "Logic" in PERSONAS["hermes"].domain


def test_knowledge_router_matches_runtime_persona_contracts():
    assert route_agent("robotics manufacturing actuator blueprint") == "ajani"
    assert route_agent("biology chemistry reproducible research") == "minerva"
    assert route_agent("algorithm optimization software validation") == "hermes"


def test_council_remains_cross_disciplinary():
    assert "Cross-disciplinary" in PERSONAS["council"].domain

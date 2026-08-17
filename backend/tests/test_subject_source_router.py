"""Tests for ATLAS 22-subject -> source routing."""
from services.subject_source_router import (
    SUBJECTS,
    normalize_subject,
    route_subject,
    sources_for_subject,
    subjects_for_agent,
)


def test_exactly_22_subjects():
    assert len(SUBJECTS) == 22
    assert len(set(SUBJECTS)) == 22


def test_core_domains_present():
    for subject in (
        "Aerospace Engineering", "Artificial Intelligence", "Biology",
        "Robotics", "Software Engineering", "Visual Arts",
    ):
        assert subject in SUBJECTS


def test_aliases_normalize():
    assert normalize_subject("AI") == "Artificial Intelligence"
    assert normalize_subject("math") == "Mathematics"
    assert normalize_subject("software development") == "Software Engineering"
    assert normalize_subject("art") == "Visual Arts"


def test_aerospace_prefers_nasa():
    sources = sources_for_subject("aerospace")
    assert sources[0] == "nasa_ntrs"
    assert "nist" in sources
    assert "arxiv" in sources


def test_biology_prefers_pubmed():
    assert sources_for_subject("Biology")[0] == "pubmed"


def test_software_prefers_github():
    assert sources_for_subject("Software Engineering")[0] == "github"


def test_history_prefers_library_of_congress():
    assert sources_for_subject("History")[0] == "library_of_congress"


def test_all_subjects_have_redundant_sources():
    for subject in SUBJECTS:
        assert len(sources_for_subject(subject)) >= 4, subject


def test_persona_affinity_is_advisory():
    assert "Artificial Intelligence" in subjects_for_agent("hermes")
    decision = route_subject("Artificial Intelligence")
    assert decision["all_personas_have_access"] is True
    assert decision["found"] is True


def test_unknown_subject_is_safe():
    assert sources_for_subject("alchemy of dragons") == []
    assert route_subject("alchemy of dragons")["found"] is False

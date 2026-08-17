"""Regression tests for the canonical ATLAS 22-subject internal knowledge core."""
from services.knowledge_core import get_knowledge_core


EXPECTED = {
    "Aerospace Engineering",
    "Architecture",
    "Artificial Intelligence",
    "Biology",
    "Business",
    "Chemistry",
    "Creative Writing",
    "Economics",
    "Electronics",
    "Environmental Science",
    "Film Studies",
    "Game Design",
    "History",
    "Mathematics",
    "Music Theory",
    "Nanotechnology",
    "Philosophy",
    "Physics",
    "Psychology",
    "Robotics",
    "Software Engineering",
    "Visual Arts",
}


def test_canonical_22_subjects_are_loaded():
    core = get_knowledge_core()
    assert set(core.list_all_subjects()) == EXPECTED
    assert len(core.list_all_subjects()) == 22


def test_every_subject_has_starter_content():
    core = get_knowledge_core()
    for name in EXPECTED:
        subject = core.get_subject(name)
        assert subject is not None
        assert subject.core_topics
        assert subject.projects
        assert subject.video_help_sources
        assert subject.books.beginner
        assert subject.books.university
        assert subject.lessons


def test_teach_works_for_newly_populated_subject():
    core = get_knowledge_core()
    response = core.teach("Software Engineering", "testing")
    assert response.subject == "Software Engineering"
    assert "tests" in response.hermes.lower() or "testing" in response.hermes.lower()
    assert response.projects

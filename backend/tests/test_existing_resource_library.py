"""Regression tests for the ATLAS Existing Resource Library."""
from services.existing_resource_library import all_resources, coverage, search_resources
from services.subject_source_router import SUBJECTS


def test_seed_library_has_real_existing_resources():
    rows = all_resources()
    assert len(rows) >= 30
    assert all(r.get("status") == "verified" for r in rows)
    assert all(r.get("url", "").startswith("https://") for r in rows)
    assert all(r.get("resource_type") in {"lesson_plan", "lesson_collection", "research_paper"} for r in rows)


def test_all_22_subjects_have_seed_resource_coverage():
    report = coverage(SUBJECTS)
    assert set(report) == set(SUBJECTS)
    assert all(stats["total"] > 0 for stats in report.values())


def test_library_can_filter_lessons_and_papers():
    nasa_lessons = search_resources(provider="NASA", resource_type="lesson_plan")
    assert nasa_lessons
    robotics_papers = search_resources(subject="Robotics", resource_type="research_paper")
    assert robotics_papers
    history_lessons = search_resources(subject="History", resource_type="lesson_plan")
    assert history_lessons


def test_cross_subject_resource_is_not_duplicated():
    uas = search_resources(q="Unmanned Aircraft Systems Educator Guide")
    assert len(uas) == 1
    assert "Aerospace Engineering" in uas[0]["subjects"]
    assert "Robotics" in uas[0]["subjects"]
    assert "Software Engineering" in uas[0]["subjects"]

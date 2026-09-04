import pytest

from backend.services import art_study_knowledge as knowledge
from creative_intelligence.art_study import ArtStudy
from creative_intelligence.technique_profile import synthesize_technique_profile


def profile():
    study = ArtStudy.from_mapping({
        "source_id": "study:authorized-knowledge-001",
        "medium": "ink drawing",
        "source_kind": "user artwork",
        "rights_basis": "user_provided",
        "observations": ["Silhouette carries the pose before interior marks"],
        "transferable_principles": ["Solve silhouette before surface detail"],
        "construction_steps": ["Gesture", "Silhouette", "Interior marks"],
        "limitations": ["Do not imitate or copy distinctive creator expression"],
        "provenance": ["user-authorized source"],
        "dimensions": ["gesture", "shape_and_silhouette", "line_and_mark"],
    })
    return synthesize_technique_profile([study])


def test_all_three_ais_receive_distinct_role_focus_with_same_safe_profile():
    views = knowledge.council_interpretations(profile())
    assert set(views) == {"ajani", "minerva", "hermes"}
    assert views["ajani"]["role_focus"] != views["minerva"]["role_focus"]
    assert views["minerva"]["role_focus"] != views["hermes"]["role_focus"]
    for view in views.values():
        assert view["direct_imitation_forbidden"] is True
        assert view["project_identity_authoritative"] is True
        assert view["source_ids"] == ["study:authorized-knowledge-001"]


@pytest.mark.asyncio
async def test_store_profile_uses_shared_knowledge_bank_and_traceable_source(monkeypatch):
    captured = {}
    async def fake_store(content, **kwargs):
        captured.update(kwargs)
        return {"id": "memory:1", "content": content, **kwargs}
    monkeypatch.setattr(knowledge.memory_bank, "auto_store", fake_store)
    row = await knowledge.store_profile(profile())
    assert row["id"] == "memory:1"
    assert captured["persona"] == "council"
    assert captured["category"] == "research"
    assert captured["source_type"] == "art_study_technique_profile"
    assert captured["source_id"] == "study:authorized-knowledge-001"
    assert "art-study" in captured["tags"]


@pytest.mark.asyncio
async def test_store_profile_fails_closed_when_memory_write_fails(monkeypatch):
    async def failed_store(*args, **kwargs):
        return None
    monkeypatch.setattr(knowledge.memory_bank, "auto_store", failed_store)
    with pytest.raises(RuntimeError, match="persistence failed"):
        await knowledge.store_profile(profile())


@pytest.mark.asyncio
async def test_retrieval_returns_only_art_study_profile_rows(monkeypatch):
    async def fake_search(*args, **kwargs):
        return [
            {"id": "1", "source_type": "art_study_technique_profile"},
            {"id": "2", "source_type": "chat"},
        ]
    monkeypatch.setattr(knowledge.memory_bank, "search_memory", fake_search)
    rows = await knowledge.retrieve_profiles("silhouette")
    assert [row["id"] for row in rows] == ["1"]


def test_unknown_persona_cannot_claim_art_study_role():
    with pytest.raises(ValueError, match="persona"):
        knowledge.interpretation_for("unknown", profile())

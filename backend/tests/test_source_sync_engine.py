"""Tests for the ATLAS Source Sync Engine."""
import pytest

from services import research_lab_engine as labs
from services import source_sync_engine as sync


@pytest.fixture(autouse=True)
def clean_state(monkeypatch):
    labs.reset_in_memory_state()
    sync.reset_in_memory_state()
    yield
    labs.reset_in_memory_state()
    sync.reset_in_memory_state()


@pytest.mark.asyncio
async def test_sync_source_preview_creates_discovery(monkeypatch):
    async def fake_preview_source(source_id: str, limit: int = 5):
        return {
            "source_id": source_id,
            "source_name": "NASA",
            "title": "NASA Research",
            "description": "Public metadata preview for aerospace research.",
            "headings": ["Missions", "Technology", "Aeronautics"],
            "content_stored": False,
        }

    monkeypatch.setattr(sync.live, "preview_source", fake_preview_source)

    mission = labs.create_mission(
        title="Aerospace materials review",
        owner_ai="Ajani",
        goal="Review aerospace source metadata for ATLAS engineering.",
        source_ids=["nasa"],
        subject_tags=["aerospace"],
        related_projects=["Weaver"],
        council_review_required=True,
    )

    run = await sync.sync_source_preview(
        source_id="nasa",
        mission_id=mission["mission_id"],
        create_discovery=True,
        limit=3,
    )

    assert run["status"] == "completed"
    assert run["preview"]["title"] == "NASA Research"
    assert run["discovery"] is not None
    assert run["discovery"]["owner_ai"] == "Ajani"
    assert run["discovery"]["citations"][0]["source_id"] == "nasa"
    assert run["content_stored"] is False


def test_list_sync_runs_filters_by_source_and_status():
    sync._SYNC_RUNS["SYNC-test1"] = {
        "run_id": "SYNC-test1",
        "source_id": "nasa",
        "status": "completed",
        "started_at": "2026-01-01T00:00:00+00:00",
    }
    sync._SYNC_RUNS["SYNC-test2"] = {
        "run_id": "SYNC-test2",
        "source_id": "pubmed",
        "status": "failed",
        "started_at": "2026-01-02T00:00:00+00:00",
    }

    assert len(sync.list_sync_runs(source_id="nasa")) == 1
    assert len(sync.list_sync_runs(status="failed")) == 1


@pytest.mark.asyncio
async def test_sync_source_preview_unknown_source_fails():
    with pytest.raises(sync.SourceSyncError):
        await sync.sync_source_preview(source_id="does_not_exist")

import pytest

from creative_intelligence.job_store import CreativeJobStore


def test_new_job_is_queued_not_fake_completed(tmp_path):
    store = CreativeJobStore(tmp_path / "jobs.json")
    job = store.create(project_id="p1", stage="create")
    assert job.status == "queued"
    assert job.result == {}
    assert store.get(job.id).status == "queued"


def test_job_lifecycle_requires_real_transition(tmp_path):
    store = CreativeJobStore(tmp_path / "jobs.json")
    job = store.create(project_id="p1", stage="critique", artifact_id="a1")
    running = store.transition(job.id, status="running")
    completed = store.transition(running.id, status="completed", result={"artifact_id": "a1", "approved": True})
    assert completed.status == "completed"
    assert completed.result["approved"] is True


def test_cannot_jump_from_queued_to_completed(tmp_path):
    store = CreativeJobStore(tmp_path / "jobs.json")
    job = store.create(project_id="p1", stage="master")
    with pytest.raises(ValueError):
        store.transition(job.id, status="completed")


def test_blocked_job_can_be_requeued(tmp_path):
    store = CreativeJobStore(tmp_path / "jobs.json")
    job = store.create(project_id="p1", stage="revision")
    blocked = store.transition(job.id, status="blocked", blockers=["missing_artifact"])
    assert blocked.blockers == ["missing_artifact"]
    queued = store.transition(job.id, status="queued")
    assert queued.status == "queued"
    assert queued.blockers == []


def test_project_filter_isolated(tmp_path):
    store = CreativeJobStore(tmp_path / "jobs.json")
    store.create(project_id="p1", stage="create")
    store.create(project_id="p2", stage="create")
    assert len(store.list(project_id="p1")) == 1

from atlas_knowledge_engine.json_learning_queue import JsonLearningQueue
from atlas_knowledge_engine.learning_adapter import LearningSource


def test_queue_survives_restart_and_preserves_priority(tmp_path):
    path = tmp_path / "learning-queue.json"
    queue = JsonLearningQueue(path)
    low = queue.submit(LearningSource("youtube", "https://youtu.be/low"), priority=80)
    high = queue.submit(LearningSource("youtube", "https://youtu.be/high"), priority=10)

    restored = JsonLearningQueue(path)
    assert restored.counts()["queued"] == 2
    assert restored.claim().job_id == high.job_id
    assert restored.claim().job_id == low.job_id


def test_running_job_is_requeued_after_restart(tmp_path):
    path = tmp_path / "learning-queue.json"
    queue = JsonLearningQueue(path)
    submitted = queue.submit(LearningSource("youtube", "https://youtu.be/recover"))
    claimed = queue.claim()
    assert claimed.job_id == submitted.job_id
    assert claimed.status == "running"

    restored = JsonLearningQueue(path)
    recovered = restored.get(submitted.job_id)
    assert recovered.status == "queued"
    assert recovered.started_at is None
    assert recovered.error == "recovered after interrupted processing"
    assert restored.claim().job_id == submitted.job_id


def test_completed_and_failed_jobs_remain_terminal(tmp_path):
    path = tmp_path / "learning-queue.json"
    queue = JsonLearningQueue(path)

    completed = queue.submit(LearningSource("youtube", "https://youtu.be/done"))
    queue.claim()
    queue.complete(completed.job_id)

    failed = queue.submit(LearningSource("youtube", "https://youtu.be/fail"))
    queue.claim()
    queue.fail(failed.job_id, "boom")

    restored = JsonLearningQueue(path)
    assert restored.get(completed.job_id).status == "completed"
    assert restored.get(failed.job_id).status == "failed"
    assert restored.get(failed.job_id).error == "boom"
    assert restored.claim() is None


def test_invalid_json_is_rejected(tmp_path):
    path = tmp_path / "learning-queue.json"
    path.write_text("not-json", encoding="utf-8")

    try:
        JsonLearningQueue(path)
    except ValueError as exc:
        assert "invalid learning queue JSON" in str(exc)
    else:
        raise AssertionError("invalid JSON should fail")

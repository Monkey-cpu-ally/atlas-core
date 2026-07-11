"""Unit tests for Qdrant semantic memory without external services."""
from services import qdrant_memory as qm


def test_embed_text_rejects_empty():
    try:
        qm.embed_text("   ")
    except ValueError as exc:
        assert "empty" in str(exc)
    else:
        raise AssertionError("empty text should fail")


def test_health_reports_failure_without_raising(monkeypatch):
    class BrokenClient:
        def get_collections(self):
            raise RuntimeError("offline")

    monkeypatch.setattr(qm, "client", lambda: BrokenClient())
    status = qm.health()
    assert status["ok"] is False
    assert "offline" in status["error"]
    assert status["collection"] == qm.QDRANT_COLLECTION


def test_upsert_memory_builds_point(monkeypatch):
    calls = {}

    class FakeClient:
        def upsert(self, collection_name, points, wait):
            calls["collection"] = collection_name
            calls["points"] = points
            calls["wait"] = wait

    monkeypatch.setattr(qm, "ensure_collection", lambda: {"created": False})
    monkeypatch.setattr(qm, "embed_text", lambda text: [0.1, 0.2, 0.3])
    monkeypatch.setattr(qm, "client", lambda: FakeClient())

    result = qm.upsert_memory("memory-1", "ATLAS test", {"persona": "hermes"})
    assert result["stored"] is True
    assert calls["collection"] == qm.QDRANT_COLLECTION
    assert calls["points"][0].payload["persona"] == "hermes"

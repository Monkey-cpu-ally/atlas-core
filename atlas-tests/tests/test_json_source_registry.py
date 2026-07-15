from __future__ import annotations

import json

import pytest

from atlas_knowledge_engine.json_source_registry import JsonSourceRegistry
from atlas_knowledge_engine.source_registry import SourceRecord


def _record(source_id: str = "video-1", content_hash: str = "abc123") -> SourceRecord:
    return SourceRecord(
        source_type="youtube",
        source_id=source_id,
        title="A Useful Video",
        content_hash=content_hash,
        canonical_url=f"https://youtube.com/watch?v={source_id}",
        creator="ATLAS Test Channel",
        metadata={"review_status": "pending"},
    )


def test_registry_persists_and_reloads(tmp_path):
    path = tmp_path / "sources.json"
    first = JsonSourceRegistry(path)
    saved = first.register(_record())

    second = JsonSourceRegistry(path)
    loaded = second.get("youtube", "video-1")

    assert loaded == saved
    assert second.find_by_hash("abc123") == saved
    assert second.health()["persistent"] is True
    assert second.health()["file_exists"] is True


def test_registry_replaces_record_and_updates_hash_index(tmp_path):
    path = tmp_path / "sources.json"
    registry = JsonSourceRegistry(path)
    registry.register(_record(content_hash="old"))
    replacement = _record(content_hash="new")

    registry.register(replacement, replace=True)
    reloaded = JsonSourceRegistry(path)

    assert reloaded.get("youtube", "video-1").content_hash == "new"
    assert reloaded.find_by_hash("old") is None
    assert reloaded.find_by_hash("new") == replacement


def test_registry_rejects_corrupt_json(tmp_path):
    path = tmp_path / "sources.json"
    path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid source registry JSON"):
        JsonSourceRegistry(path)


def test_registry_rejects_unknown_format_version(tmp_path):
    path = tmp_path / "sources.json"
    path.write_text(
        json.dumps({"format_version": 999, "records": []}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unsupported source registry format version"):
        JsonSourceRegistry(path)


def test_registry_rejects_duplicate_content_after_restart(tmp_path):
    path = tmp_path / "sources.json"
    JsonSourceRegistry(path).register(_record())
    restarted = JsonSourceRegistry(path)

    with pytest.raises(KeyError, match="content hash already registered"):
        restarted.register(_record(source_id="video-2"))

"""Tests for ATLAS JSON persistence."""

from atlas_knowledge_engine.models import SourcePassport
from atlas_persistence.json_store import JsonFileStore


def test_json_store_can_append_and_read_dataclass_record(tmp_path):
    store = JsonFileStore(tmp_path)

    source = SourcePassport(
        title="Persistence Test Source",
        source_type="Test",
        creator_or_organization="test-suite",
        primary_knowledge_bank="Software Engineering",
        status="approved",
    )

    saved = store.append_record("sources", source)
    records = store.read_collection("sources")

    assert saved["title"] == "Persistence Test Source"
    assert len(records) == 1
    assert records[0]["primary_knowledge_bank"] == "Software Engineering"
    assert records[0]["status"] == "approved"

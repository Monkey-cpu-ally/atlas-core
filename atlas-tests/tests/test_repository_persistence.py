"""Tests for JSON-backed repositories used by ATLAS services."""

from atlas_knowledge_engine.json_repository import JsonKnowledgeRepository, JsonSourceRepository
from atlas_knowledge_engine.models import KnowledgeEntry, SourcePassport
from atlas_knowledge_engine.service import KnowledgeService
from atlas_memory_engine.json_repository import JsonMemoryRepository
from atlas_memory_engine.models import MemoryRecord, MemoryType
from atlas_memory_engine.service import MemoryService
from atlas_persistence.json_store import JsonFileStore


def test_memory_service_can_persist_records_through_json_repository(tmp_path):
    store = JsonFileStore(tmp_path)
    repository = JsonMemoryRepository(store)
    service = MemoryService(repository=repository)
    service.start()

    record = service.create_record(
        MemoryRecord(
            title="Persistent Memory Test",
            memory_type=MemoryType.PROJECT,
            summary="Testing repository-backed memory.",
            content="This should persist through the JSON repository.",
            created_by="test-suite",
        )
    )

    persisted = service.persisted_records()

    assert record.title == "Persistent Memory Test"
    assert len(persisted) == 1
    assert persisted[0]["title"] == "Persistent Memory Test"
    assert persisted[0]["memory_type"] == "project_memory"


def test_knowledge_service_can_persist_sources_and_entries_through_json_repositories(tmp_path):
    store = JsonFileStore(tmp_path)
    source_repository = JsonSourceRepository(store)
    knowledge_repository = JsonKnowledgeRepository(store)
    service = KnowledgeService(
        source_repository=source_repository,
        knowledge_repository=knowledge_repository,
    )
    service.start()

    source = service.add_source(
        SourcePassport(
            title="Persistent Source Test",
            source_type="Test",
            creator_or_organization="test-suite",
            primary_knowledge_bank="Software Engineering",
            status="approved",
        )
    )

    entry = service.add_entry(
        KnowledgeEntry(
            title="Persistent Knowledge Test",
            summary="Testing repository-backed knowledge.",
            primary_knowledge_bank="Software Engineering",
            created_by="test-suite",
            source_ids=[source.source_id],
        )
    )

    persisted_sources = service.persisted_sources()
    persisted_entries = service.persisted_entries()

    assert source.title == "Persistent Source Test"
    assert entry.title == "Persistent Knowledge Test"
    assert len(persisted_sources) == 1
    assert len(persisted_entries) == 1
    assert persisted_sources[0]["status"] == "approved"
    assert persisted_entries[0]["source_ids"] == [source.source_id]

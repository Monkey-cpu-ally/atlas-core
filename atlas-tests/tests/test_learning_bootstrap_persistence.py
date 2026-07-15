from __future__ import annotations

from atlas_knowledge_engine.json_source_registry import JsonSourceRegistry
from atlas_knowledge_engine.learning_bootstrap import build_default_learning_pipeline
from atlas_knowledge_engine.source_registry import SourceRecord


def test_default_pipeline_can_use_persistent_source_registry(tmp_path):
    path = tmp_path / "source-registry.json"
    pipeline = build_default_learning_pipeline(source_registry_path=path)

    assert isinstance(pipeline.source_registry, JsonSourceRegistry)
    pipeline.source_registry.register(
        SourceRecord(
            source_type="youtube",
            source_id="abc123",
            title="Persistent Video",
            content_hash="hash-1",
        )
    )

    restarted = build_default_learning_pipeline(source_registry_path=path)
    assert restarted.source_registry.get("youtube", "abc123").title == "Persistent Video"

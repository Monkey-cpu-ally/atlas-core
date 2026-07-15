import json
from pathlib import Path

import pytest

from atlas_knowledge_engine.youtube_cli import save_record
from atlas_knowledge_engine.youtube_ingestion import IngestionError


def sample_record() -> dict[str, object]:
    return {
        "source_id": "abc123",
        "transcript_hash": "hash-one",
        "title": "Example",
    }


def test_save_record_creates_json_file(tmp_path: Path) -> None:
    output = save_record(sample_record(), tmp_path)
    assert output == tmp_path / "abc123.json"
    assert json.loads(output.read_text(encoding="utf-8"))["title"] == "Example"


def test_save_record_rejects_exact_duplicate(tmp_path: Path) -> None:
    save_record(sample_record(), tmp_path)
    with pytest.raises(IngestionError, match="already stored"):
        save_record(sample_record(), tmp_path)


def test_save_record_updates_changed_transcript(tmp_path: Path) -> None:
    save_record(sample_record(), tmp_path)
    changed = sample_record()
    changed["transcript_hash"] = "hash-two"
    output = save_record(changed, tmp_path)
    assert json.loads(output.read_text(encoding="utf-8"))["transcript_hash"] == "hash-two"

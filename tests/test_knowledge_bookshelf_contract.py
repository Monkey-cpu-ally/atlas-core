import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "knowledge-division" / "existing-resource-library-v1.json"
BOOKSHELF = ROOT / "frontend" / "src" / "components" / "HUD" / "KnowledgeBookshelf.js"


def test_bookshelf_catalog_resources_are_real_and_cross_listable():
    payload = json.loads(CATALOG.read_text(encoding="utf-8"))
    resources = payload["resources"]

    assert resources, "Knowledge Bookshelf seed catalog must not be empty"
    assert payload["rules"]["preserve_original_authorship"] is True
    assert payload["rules"]["verify_license_before_local_copy"] is True

    ids = [row["id"] for row in resources]
    assert len(ids) == len(set(ids)), "resource IDs must be unique"

    for row in resources:
        assert row.get("title")
        assert row.get("provider")
        assert row.get("url", "").startswith("https://")
        assert row.get("subjects"), f"{row['id']} must belong to at least one ATLAS subject"
        assert row.get("status") == "verified"
        assert row.get("storage_policy")

    assert any(len(row["subjects"]) > 1 for row in resources), "catalog must preserve cross-listed resources"


def test_bookshelf_frontend_consumes_live_kbase_contract_and_subject_arrays():
    source = BOOKSHELF.read_text(encoding="utf-8")

    assert "/api/kbase/subjects" in source
    assert "/api/kbase/resources" in source
    assert "/api/research/orchestrate" in source
    assert "/api/chat/send" in source
    assert "resource?.subjects" in source
    assert "hasSubject(resource, subject)" in source
    assert "selected.status" in source
    assert "fake" not in source.lower()

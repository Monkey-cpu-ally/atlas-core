import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
CATALOG = ROOT / "knowledge-division" / "existing-resource-library-v1.json"
BOOKSHELF = ROOT / "frontend" / "src" / "components" / "HUD" / "KnowledgeBookshelf.js"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


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


@pytest.mark.asyncio
async def test_bookshelf_backend_routes_return_live_subject_and_resource_payloads():
    from routes.kbase import existing_resource_coverage, existing_resources, knowledge_bank_subjects

    subjects = await knowledge_bank_subjects()
    resources = await existing_resources()
    coverage = await existing_resource_coverage()

    assert subjects["count"] == 22
    assert len(subjects["subjects"]) == 22
    assert resources["count"] == len(resources["items"])
    assert resources["count"] > 0
    assert coverage["resource_count"] == resources["count"]
    assert set(coverage["subjects"]) == set(subjects["subjects"])

    sample = resources["items"][0]
    assert sample["status"] == "verified"
    assert sample["subjects"]
    assert sample["url"].startswith("https://")


@pytest.mark.asyncio
async def test_bookshelf_subject_filter_uses_cross_listed_catalog_membership():
    from routes.kbase import existing_resources

    all_rows = (await existing_resources())["items"]
    cross_listed = next(row for row in all_rows if len(row.get("subjects", [])) > 1)

    for subject in cross_listed["subjects"]:
        filtered = await existing_resources(subject=subject)
        returned_ids = {row["id"] for row in filtered["items"]}
        assert cross_listed["id"] in returned_ids

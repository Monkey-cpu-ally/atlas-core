"""Controlled proof that selected catalog resources become retrievable ATLAS knowledge.

This test uses fixed, public Knowledge Bank catalog URLs. For each source it:
1. calls the existing /api/kbase/ingest route,
2. verifies a KnowledgeRecord + Memory Bank row were created,
3. retrieves the distilled memory through /api/membank/search,
4. writes machine-readable runtime evidence keyed by the stable catalog resource ID,
5. runs the V3 quality auditor and verifies every proof resource becomes usable knowledge.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

BACKEND = os.environ.get("REACT_APP_BACKEND_URL") or os.environ.get(
    "BACKEND_URL", "http://127.0.0.1:8000"
)
API = f"{BACKEND.rstrip('/')}/api"
ROOT = Path(__file__).resolve().parents[2]
SUBJECT_ROOT = ROOT / "knowledge_bank/world_sources/subjects"
STATUS_PATH = SUBJECT_ROOT / "runtime_status_v1.json"
QUALITY_PATH = SUBJECT_ROOT / "quality_matrix_v3.json"
AUDITOR_PATH = SUBJECT_ROOT / "quality_audit_v3.py"

PROOF_RESOURCES = [
    {
        "id": "subjects:software_engineering_depth_v2.json#0",
        "title": "CS50x",
        "url": "https://cs50.harvard.edu/x/",
    },
    {
        "id": "subjects:depth/software_engineering_depth_v1.json#3",
        "title": "MIT Introduction to Algorithms",
        "url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/",
    },
    {
        "id": "subjects:software_engineering_depth_v2.json#3",
        "title": "MDN Web Docs",
        "url": "https://developer.mozilla.org/",
    },
    {
        "id": "subjects:software_engineering_depth_v2.json#4",
        "title": "PostgreSQL Documentation",
        "url": "https://www.postgresql.org/docs/",
    },
    {
        "id": "subjects:software_engineering_depth_v2.json#5",
        "title": "IETF RFC Index",
        "url": "https://www.rfc-editor.org/",
    },
    {
        "id": "subjects:depth/mathematics_depth_v1.json#4",
        "title": "Precalculus 2e",
        "url": "https://openstax.org/details/books/precalculus-2e",
    },
    {
        "id": "subjects:depth/mathematics_depth_v1.json#6",
        "title": "Linear Algebra",
        "url": "https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/",
    },
    {
        "id": "subjects:depth/mathematics_depth_v1.json#9",
        "title": "arXiv Mathematics",
        "url": "https://arxiv.org/archive/math",
    },
    {
        "id": "subjects:biology.json#0",
        "title": "Biology 2e",
        "url": "https://openstax.org/details/books/biology-2e",
    },
    {
        "id": "subjects:biology.json#8",
        "title": "PubMed Central",
        "url": "https://pmc.ncbi.nlm.nih.gov/",
    },
    {
        "id": "subjects:depth/physics_depth_v1.json#1",
        "title": "College Physics 2e",
        "url": "https://openstax.org/details/books/college-physics-2e",
    },
    {
        "id": "subjects:chemistry.json#0",
        "title": "Chemistry 2e",
        "url": "https://openstax.org/details/books/chemistry-2e",
    },
    {
        "id": "subjects:robotics_depth_v2.json#2",
        "title": "ROS 2 Documentation",
        "url": "https://docs.ros.org/",
    },
    {
        "id": "subjects:artificial_intelligence.json#12",
        "title": "Artificial Intelligence Risk Management Framework",
        "url": "https://www.nist.gov/itl/ai-risk-management-framework",
    },
    {
        "id": "subjects:electrical_engineering.json#0",
        "title": "Circuits and Electronics",
        "url": "https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/",
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _verification_metadata() -> dict:
    run_id = os.environ.get("GITHUB_RUN_ID")
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repository = os.environ.get("GITHUB_REPOSITORY")
    run_url = f"{server}/{repository}/actions/runs/{run_id}" if run_id and repository else None
    return {
        "workflow": os.environ.get("GITHUB_WORKFLOW", "local runtime proof"),
        "run_number": os.environ.get("GITHUB_RUN_NUMBER"),
        "run_url": run_url,
        "head_sha": os.environ.get("GITHUB_SHA"),
        "verified_at": _utc_now(),
        "result": "success" if not run_id else "pending-test-completion",
    }


def test_catalog_resources_ingest_and_retrieve():
    evidence = {}
    failures = []

    with httpx.Client(timeout=180.0) as client:
        for item in PROOF_RESOURCES:
            try:
                ingest = client.post(
                    f"{API}/kbase/ingest",
                    json={
                        "url": item["url"],
                        "extra_tags": ["catalog-runtime-proof-v1", item["id"]],
                    },
                )
                if ingest.status_code != 200:
                    raise AssertionError(f"ingest HTTP {ingest.status_code}: {ingest.text[:300]}")

                payload = ingest.json()
                record = payload.get("record") or {}
                memory_bank_id = payload.get("memory_bank_id")
                if not record.get("id") or not memory_bank_id:
                    raise AssertionError("ingest did not return record.id and memory_bank_id")

                search = client.get(
                    f"{API}/membank/search",
                    params={"q": item["title"], "top_k": 20, "min_score": 0.0},
                )
                if search.status_code != 200:
                    raise AssertionError(f"retrieval HTTP {search.status_code}: {search.text[:300]}")
                results = search.json().get("results") or []

                matched = next(
                    (
                        row for row in results
                        if item["url"] in (row.get("content") or "")
                        or row.get("id") == memory_bank_id
                    ),
                    None,
                )
                if not matched:
                    raise AssertionError("ingested source was not returned by Memory Bank search")

                evidence[item["id"]] = {
                    "ingested": True,
                    "retrieval_tested": True,
                    "citation_ready": True,
                    "source_url": item["url"],
                    "knowledge_record_id": record["id"],
                    "memory_bank_id": memory_bank_id,
                    "retrieval_memory_id": matched.get("id"),
                    "verified_at": _utc_now(),
                    "proof": "live /api/kbase/ingest -> /api/membank/search",
                }
            except Exception as exc:
                evidence[item["id"]] = {
                    "ingested": False,
                    "retrieval_tested": False,
                    "citation_ready": True,
                    "source_url": item["url"],
                    "verified_at": _utc_now(),
                    "error": str(exc)[:500],
                }
                failures.append(f"{item['id']}: {exc}")

    verification = _verification_metadata()
    verification["result"] = "success" if not failures else "failure"
    STATUS_PATH.write_text(
        json.dumps({
            "schema_version": "1.0",
            "verification": verification,
            "resources": evidence,
        }, indent=2) + "\n",
        encoding="utf-8",
    )

    assert not failures, "Catalog runtime proof failed:\n" + "\n".join(failures)

    subprocess.run([sys.executable, str(AUDITOR_PATH)], cwd=ROOT, check=True)
    quality = json.loads(QUALITY_PATH.read_text(encoding="utf-8"))
    summary = quality["summary"]

    expected = len(PROOF_RESOURCES)
    assert summary["runtime_status_resources"] == expected, summary
    assert summary["ingested_resources"] == expected, summary
    assert summary["retrieval_tested_resources"] == expected, summary
    assert summary["usable_resources"] == expected, summary
    assert summary["usable_knowledge_percent"] == round(expected / summary["resource_count"] * 100, 2), summary

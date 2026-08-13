"""Controlled V1 proof that five catalog resources become retrievable ATLAS knowledge.

This test uses five fixed, public Knowledge Bank catalog URLs. For each source it:
1. calls the existing /api/kbase/ingest route,
2. verifies a KnowledgeRecord + Memory Bank row were created,
3. retrieves the distilled memory through /api/membank/search,
4. writes machine-readable runtime evidence keyed by the stable catalog resource ID.

The evidence file is consumed by quality_audit_v3.py in CI; no manifest is allowed
to award itself ingestion/retrieval credit.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import httpx

BACKEND = os.environ.get("REACT_APP_BACKEND_URL") or os.environ.get(
    "BACKEND_URL", "http://127.0.0.1:8000"
)
API = f"{BACKEND.rstrip('/')}/api"
ROOT = Path(__file__).resolve().parents[2]
STATUS_PATH = ROOT / "knowledge_bank/world_sources/subjects/runtime_status_v1.json"

PROOF_RESOURCES = [
    {
        "id": "software_engineering_depth_v2.json#0",
        "title": "CS50x",
        "url": "https://cs50.harvard.edu/x/",
    },
    {
        "id": "software_engineering_depth_v2.json#1",
        "title": "MIT Introduction to Algorithms",
        "url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/",
    },
    {
        "id": "software_engineering_depth_v2.json#3",
        "title": "MDN Web Docs",
        "url": "https://developer.mozilla.org/",
    },
    {
        "id": "software_engineering_depth_v2.json#4",
        "title": "PostgreSQL Documentation",
        "url": "https://www.postgresql.org/docs/",
    },
    {
        "id": "software_engineering_depth_v2.json#5",
        "title": "IETF RFC Index",
        "url": "https://www.rfc-editor.org/",
    },
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def test_five_catalog_resources_ingest_and_retrieve():
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

                # Use catalog title as the retrieval query. The stored distilled body
                # includes the fetched title and metadata, so this verifies the real
                # Memory Bank search path rather than a direct Mongo lookup.
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
            except Exception as exc:  # collect all five diagnostics before failing
                evidence[item["id"]] = {
                    "ingested": False,
                    "retrieval_tested": False,
                    "citation_ready": True,
                    "source_url": item["url"],
                    "verified_at": _utc_now(),
                    "error": str(exc)[:500],
                }
                failures.append(f"{item['id']}: {exc}")

    STATUS_PATH.write_text(
        json.dumps({"schema_version": "1.0", "resources": evidence}, indent=2) + "\n",
        encoding="utf-8",
    )

    assert not failures, "Five-resource runtime proof failed:\n" + "\n".join(failures)

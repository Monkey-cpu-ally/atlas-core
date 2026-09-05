"""Deterministic CI/demo records for HUD live-data contract tests.

This module is deliberately test-mode only. It seeds a minimal record in the
real persistence collections used by HUD surfaces so GitHub Actions validates
live wiring instead of empty databases. Production environments are untouched.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient


def _enabled() -> bool:
    return os.environ.get("ATLAS_TEST_MODE", "").strip().lower() in {
        "1", "true", "yes", "on",
    }


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


async def seed_ci_demo_data() -> dict:
    """Idempotently seed the four HUD collections that need baseline data."""
    if not _enabled():
        return {"enabled": False, "seeded": 0}

    client = AsyncIOMotorClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
    db = client[os.environ.get("DB_NAME", "test_database")]
    now = _utc()
    seeded = 0

    records = [
        (
            "blueprint_forge",
            "atlas-ci-reference-blueprint",
            {
                "id": "atlas-ci-reference-blueprint",
                "queue_item_id": "atlas-ci-reference-queue",
                "knowledge_id": "atlas-ci-reference-knowledge",
                "hardware_concept": {"parts": [], "total_cost_usd": 0},
                "software_architecture": {"components": ["ATLAS Core"], "key_libraries": [], "languages": ["Python"]},
                "manufacturing_workflow": ["Validate live HUD wiring"],
                "prototype_suggestion": {"name": "ATLAS CI Reference", "weekend_build": True, "summary": "Deterministic CI reference blueprint."},
                "risks": [],
                "opportunities": ["Verify Blueprint HUD persistence"],
                "parts_count": 0,
                "components_count": 1,
                "steps_count": 1,
                "total_cost_usd": 0,
                "agent": "hermes",
                "evidence": {
                    "source": "atlas_ci_seed",
                    "confidence": 1.0,
                    "evidence_refs": [{"kind": "ci_contract", "id": "hud-live-data"}],
                    "date": now,
                    "verification_status": "automated",
                },
                "created_at": now,
            },
        ),
        (
            "research_missions",
            "atlas-ci-reference-mission",
            {
                "id": "atlas-ci-reference-mission",
                "title": "Verify ATLAS HUD live data",
                "domain": "software_engineering",
                "question": "Are HUD-backed research mission records reachable through the live API?",
                "status": "open",
                "priority": "low",
                "agent": "minerva",
                "evidence": {
                    "source": "atlas_ci_seed",
                    "confidence": 1.0,
                    "evidence_refs": [{"kind": "ci_contract", "id": "hud-live-data"}],
                    "date": now,
                    "verification_status": "automated",
                },
                "created_at": now,
                "updated_at": now,
            },
        ),
        (
            "self_improvements",
            "atlas-ci-reference-improvement",
            {
                "id": "atlas-ci-reference-improvement",
                "improvement_id": "atlas-ci-reference-improvement",
                "observed_pattern": "HUD live-data surfaces require deterministic CI baseline records.",
                "evidence": [{"type": "ci_contract", "id": "hud-live-data"}],
                "affected_system": "backend HUD persistence",
                "proposed_change": "Keep deterministic test-mode seed records available for live endpoint verification.",
                "category": "testing",
                "risk_level": "low",
                "confidence_score": 1.0,
                "approval_required": False,
                "owner_ai": "Council",
                "source": "atlas-ci-seed",
                "status": "pending",
                "decision_note": None,
                "update_plan": ["Run Backend CI", "Verify HUD endpoints return live records"],
                "rollback_plan": "Disable ATLAS_TEST_MODE or remove the CI seed service.",
                "created_at": now,
                "updated_at": now,
            },
        ),
        (
            "atlas_archive",
            "atlas-ci-reference-archive",
            {
                "id": "atlas-ci-reference-archive",
                "filename": "atlas-ci-reference.md",
                "entry_type": "document",
                "title": "ATLAS CI Reference Archive Entry",
                "summary": "Deterministic archive record proving the HUD archive is connected to live persistence.",
                "classified_core": "hermes",
                "source": "atlas_ci_seed",
                "ts": now,
            },
        ),
    ]

    for collection, record_id, doc in records:
        result = await db[collection].update_one(
            {"id": record_id},
            {"$setOnInsert": doc},
            upsert=True,
        )
        if result.upserted_id is not None:
            seeded += 1

    client.close()
    return {"enabled": True, "seeded": seeded}

"""
Blueprint Forge.

Converts a verified research_queue item into a structured build plan via
gpt-5.2. NOT a real engineering simulator (Weaver/Twin remain 🟡 SIMULATED).
This forges:
  * hardware concept (parts list, rough cost)
  * software architecture (components, languages, key libraries)
  * manufacturing workflow (steps)
  * prototype suggestion (one weekend buildable variant)

Persisted in `blueprint_forge` with an evidence envelope.
"""
from __future__ import annotations

import json
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient

from services.llm_provider import send as llm_send

logger = logging.getLogger("atlas.blueprint_forge")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _utc(): return datetime.now(timezone.utc).isoformat()


SYS = (
    "You convert a research finding into a concrete buildable plan.\n"
    "Reply with STRICT JSON only. Schema:\n"
    "{\n"
    '  "hardware_concept": {"parts": [{"name": str, "qty": int, "est_cost_usd": number}], "total_cost_usd": number},\n'
    '  "software_architecture": {"components": [str], "key_libraries": [str], "languages": [str]},\n'
    '  "manufacturing_workflow": [str, str, str, str],\n'
    '  "prototype_suggestion": {"name": str, "weekend_build": true, "summary": str},\n'
    '  "risks": [str],\n'
    '  "opportunities": [str]\n'
    "}"
)


_JSON = re.compile(r"\{.*\}", re.DOTALL)


def _safe_json(raw: str) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        m = _JSON.search(raw)
        if m:
            try: return json.loads(m.group(0))
            except Exception: return None
    return None


async def forge_from_queue(item_id: str) -> Dict[str, Any]:
    db = _db()
    item = await db["research_queue"].find_one({"id": item_id}, {"_id": 0})
    if not item:
        return {"ok": False, "error": "queue item not found", "id": item_id}
    if item.get("state") not in ("linked", "stored", "verified"):
        return {"ok": False,
                "error": f"state must be ≥ verified; got {item.get('state')}",
                "id": item_id}
    kb_id = item.get("knowledge_id")
    kb = await db["knowledge_records"].find_one({"id": kb_id}, {"_id": 0}) if kb_id else None
    concepts = (kb or {}).get("concepts") or []
    summary  = (kb or {}).get("summary")  or item.get("title", "")

    user_msg = (
        f"RESEARCH FINDING\n"
        f"Title: {item.get('title')}\n"
        f"Domain: {item.get('domain')}\n"
        f"Concepts: {', '.join(concepts[:10])}\n"
        f"Summary:\n{summary[:1500]}\n\n"
        f"Convert this into a hands-on build plan under $250, one weekend."
    )
    try:
        resp = await llm_send(item.get("agent") or "ajani", SYS, user_msg)
        data = _safe_json(resp.get("text") or "") or {}
    except Exception as exc:    # noqa: BLE001
        logger.warning("forge LLM failed: %s", exc)
        data = {}

    parts = (data.get("hardware_concept") or {}).get("parts") or []
    total_cost = (data.get("hardware_concept") or {}).get("total_cost_usd") or 0
    components = (data.get("software_architecture") or {}).get("components") or []
    steps = data.get("manufacturing_workflow") or []
    risks = data.get("risks") or []

    forge_id = uuid4().hex
    record = {
        "id": forge_id,
        "queue_item_id": item_id,
        "knowledge_id": kb_id,
        "hardware_concept": data.get("hardware_concept") or {},
        "software_architecture": data.get("software_architecture") or {},
        "manufacturing_workflow": steps,
        "prototype_suggestion": data.get("prototype_suggestion") or {},
        "risks": risks,
        "opportunities": data.get("opportunities") or [],
        "parts_count": len(parts),
        "components_count": len(components),
        "steps_count": len(steps),
        "total_cost_usd": total_cost,
        "agent": item.get("agent"),
        "evidence": {
            "source": "blueprint_forge_llm",
            "confidence": 0.5,
            "evidence_refs": [
                {"kind": "knowledge", "id": kb_id},
                {"kind": "queue", "id": item_id},
            ],
            "date": _utc(),
            "verification_status": "llm_simulated",
        },
        "created_at": _utc(),
    }
    await db["blueprint_forge"].insert_one(record)
    await db["research_queue"].update_one(
        {"id": item_id},
        {"$set": {"blueprint_id": forge_id, "updated_at": _utc()}},
    )
    return {"ok": True, **record}


async def list_blueprints(limit: int = 50):
    cur = _db()["blueprint_forge"].find({}, {"_id": 0}).sort("created_at", -1).limit(limit)
    return [d async for d in cur]

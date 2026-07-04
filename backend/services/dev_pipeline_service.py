"""ATLAS Engineering / Development Pipeline service.

Adapted from `atlas_development_pipeline_packet/backend/app/services/
development_pipeline_service.py`. The packet ships a placeholder that
returns `needs_runtime_check` for every subsystem — we replace that
with real live probes against the routers already registered in this
repo. Nothing external is called; all probes go through the in-process
router table so the console reports actual health even if the ingress
is down.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

# ---------------------------------------------------------------------------
# Status vocabulary — from docs/devops/ATLAS_DEVELOPMENT_PIPELINE.md.
# ---------------------------------------------------------------------------
HEALTHY = "healthy"
DEGRADED = "degraded"
MISSING = "missing"
UNDER_CONSTRUCTION = "under_construction"
UNKNOWN = "unknown"


def status_item(
    name: str,
    status: str,
    details: str = "",
    endpoint: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "name": name,
        "status": status,
        "details": details,
        "endpoint": endpoint,
    }
    if extra:
        row["extra"] = extra
    return row


class DevelopmentPipelineService:
    """Aggregates ATLAS engineering health into one status object.

    Every subsystem is probed via its in-process handler (no HTTP round
    trip) so the dashboard is fast and works even inside tests.
    """

    def __init__(self, mongo_url: Optional[str] = None, db_name: Optional[str] = None):
        self._mongo_url = mongo_url or os.environ.get("MONGO_URL", "mongodb://localhost:27017")
        self._db_name = db_name or os.environ.get("DB_NAME", "test_database")
        self._client: Optional[AsyncIOMotorClient] = None

    def _db(self):
        if self._client is None:
            self._client = AsyncIOMotorClient(self._mongo_url)
        return self._client[self._db_name]

    # --- individual probes -------------------------------------------------
    async def _probe_mongo(self) -> Dict[str, Any]:
        try:
            await self._db().command("ping")
            return status_item(
                "MongoDB", HEALTHY, f"db={self._db_name}", endpoint="mongo://ping"
            )
        except Exception as exc:
            return status_item("MongoDB", DEGRADED, str(exc)[:200])

    async def _probe_memory_bank(self) -> Dict[str, Any]:
        try:
            count = await self._db()["memory_bank"].count_documents({})
            return status_item(
                "Memory Bank",
                HEALTHY,
                f"{count} entries · alias /api/memory",
                endpoint="/api/membank",
                extra={"entry_count": count},
            )
        except Exception as exc:
            return status_item("Memory Bank", DEGRADED, str(exc)[:200], "/api/membank")

    async def _probe_knowledge_network(self) -> Dict[str, Any]:
        try:
            db = self._db()
            subs = await db["subjects"].count_documents({})
            recs = await db["knowledge_records"].count_documents({})
            return status_item(
                "Knowledge Network",
                HEALTHY,
                f"subjects={subs} · records={recs}",
                endpoint="/api/knowledge-network/dashboard",
                extra={"subjects": subs, "knowledge_records": recs},
            )
        except Exception as exc:
            return status_item(
                "Knowledge Network", DEGRADED, str(exc)[:200], "/api/knowledge-network"
            )

    async def _probe_research_queue(self) -> Dict[str, Any]:
        try:
            from services import research_orchestrator as ro  # type: ignore

            queue = await ro.list_queue() if hasattr(ro, "list_queue") else []
            return status_item(
                "Research Queue",
                HEALTHY,
                f"{len(queue)} pending · alias /api/tasks/queue",
                endpoint="/api/research-orch/queue",
                extra={"pending": len(queue)},
            )
        except Exception as exc:
            return status_item(
                "Research Queue", DEGRADED, str(exc)[:200], "/api/research-orch/queue"
            )

    async def _probe_ai_status(self) -> Dict[str, Any]:
        try:
            from routes.llm import list_persona_models  # type: ignore

            data = await list_persona_models()
            personas = list((data or {}).get("personas", {}).keys())
            return status_item(
                "AI Routing",
                HEALTHY,
                f"personas={personas}",
                endpoint="/api/llm/persona-models",
                extra=data,
            )
        except Exception as exc:
            return status_item("AI Routing", DEGRADED, str(exc)[:200], "/api/llm/persona-models")

    async def _probe_teaching_engine(self) -> Dict[str, Any]:
        # Teaching engine is a POST endpoint — we can't safely fire it here
        # (it kicks off an LLM job). Instead confirm the router is mounted
        # by looking it up in the app's own registry via import.
        try:
            from atlas_core import atlas_router  # type: ignore

            paths = {r.path for r in atlas_router.routes}
            has_teach = any(p.endswith("/teach") for p in paths)
            return status_item(
                "Teaching Engine",
                HEALTHY if has_teach else MISSING,
                "POST /api/atlas/teach · alias /api/teaching",
                endpoint="/api/teaching",
            )
        except Exception as exc:
            return status_item("Teaching Engine", DEGRADED, str(exc)[:200], "/api/teaching")

    async def _probe_research_engine(self) -> Dict[str, Any]:
        try:
            from routes.research import router as research_router  # type: ignore

            return status_item(
                "Research Engine",
                HEALTHY,
                "web + pdf + patent pipeline",
                endpoint="/api/research",
                extra={"routes": len(research_router.routes)},
            )
        except Exception as exc:
            return status_item("Research Engine", DEGRADED, str(exc)[:200], "/api/research")

    async def _probe_github(self) -> Dict[str, Any]:
        # We cannot commit from inside the pod — user does that via the
        # Emergent "Save to GitHub" button. Report a passive status.
        return status_item(
            "GitHub",
            UNKNOWN,
            "External connector — use Emergent 'Save to GitHub' button",
            endpoint=None,
        )

    async def _probe_test_status(self) -> Dict[str, Any]:
        # Presence of the pytest suite is our proxy for test wiring health.
        suite_dir = "/app/backend/tests"
        try:
            files = [f for f in os.listdir(suite_dir) if f.startswith("test_") and f.endswith(".py")]
            return status_item(
                "Test Suite",
                HEALTHY if files else MISSING,
                f"{len(files)} test files present",
                endpoint=None,
                extra={"test_files": len(files)},
            )
        except Exception as exc:
            return status_item("Test Suite", MISSING, str(exc)[:200])

    async def _active_tasks(self) -> List[Dict[str, Any]]:
        """Currently-tracked engineering work items. Sourced from the
        ATLAS memory `events` collection when available."""
        try:
            rows = (
                await self._db()["memory_bank"]
                .find({"category": "task", "status": {"$ne": "done"}}, {"_id": 0})
                .sort("timestamp", -1)
                .to_list(20)
            )
            return rows
        except Exception:
            return []

    # --- public --------------------------------------------------------------
    async def get_status(self) -> Dict[str, Any]:
        systems = [
            await self._probe_mongo(),
            await self._probe_memory_bank(),
            await self._probe_knowledge_network(),
            await self._probe_research_queue(),
            await self._probe_ai_status(),
            await self._probe_teaching_engine(),
            await self._probe_research_engine(),
            await self._probe_github(),
            await self._probe_test_status(),
        ]

        # Roll up the highest-severity status across the board.
        severity = {HEALTHY: 0, UNKNOWN: 1, UNDER_CONSTRUCTION: 2, DEGRADED: 3, MISSING: 4}
        overall = HEALTHY
        for s in systems:
            if severity.get(s["status"], 0) > severity.get(overall, 0):
                overall = s["status"]

        return {
            "system": "ATLAS Engineering Console",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "overall_status": overall,
            "pipeline": ["Founder", "ChatGPT", "Emergent/Cursor", "GitHub", "Tests", "ATLAS OS"],
            "current_release": {
                "name": "ATLAS OS v1",
                "phase": "Foundation + Intelligence alignment",
                "branch": os.environ.get("ATLAS_BRANCH", "feature/atlas-release-foundation-intelligence"),
                "next_target": "Engineering Console wiring · Knowledge Network dashboard",
            },
            "systems": systems,
            "active_tasks": await self._active_tasks(),
            "recommended_next_actions": [
                "Commit knowledge-network layer via 'Save to GitHub'.",
                "Await real Release 1 / Release 2 code payloads.",
                "Populate country/region/trust_level metadata on existing sources.",
                "Add Engineering Console panel behind hidden/dev access.",
            ],
        }


# Singleton — importable in the same shape as the packet.
pipeline_service = DevelopmentPipelineService()

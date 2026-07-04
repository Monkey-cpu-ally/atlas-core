"""Packet-aligned API aliases for EMERGENT_MASTER_PROMPT.md compliance.

This module exposes the endpoint prefixes expected by the ATLAS
"Release 1 / Release 2" hand-off packet without breaking the existing
routes that the HUD is already wired to. It works in two ways:

1. `mount_alias()` — clones existing APIRoute objects from a source
   router under a new prefix on the FastAPI app. Both the original path
   and the aliased path serve the same handler.

2. Two brand new lightweight routers:
     * `/api/health`        — liveness + service inventory
     * `/api/intelligence`  — aggregate persona / LLM introspection.

Nothing existing is renamed or removed.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute


# ---------------------------------------------------------------------------
# Boot timestamp — used by /api/health for uptime reporting.
# ---------------------------------------------------------------------------
_BOOT_TS = time.time()


# ---------------------------------------------------------------------------
# mount_alias — clone routes from a source router under a new prefix.
# ---------------------------------------------------------------------------
def mount_alias(
    app: FastAPI,
    source_router: APIRouter,
    from_prefix: str,
    to_prefix: str,
    tag: str = "Packet Aliases",
) -> int:
    """Clone every APIRoute in `source_router` whose path starts with
    `from_prefix` onto `app`, replacing that prefix with `to_prefix`.

    Returns the number of aliased routes for logging.
    """
    count = 0
    seen: set[tuple[str, frozenset[str]]] = set()
    for route in source_router.routes:
        if not isinstance(route, APIRoute):
            continue
        if not route.path.startswith(from_prefix):
            continue
        new_path = to_prefix + route.path[len(from_prefix):]
        key = (new_path, frozenset(route.methods or set()))
        if key in seen:
            continue
        seen.add(key)
        app.add_api_route(
            new_path,
            route.endpoint,
            methods=list(route.methods or ["GET"]),
            response_model=route.response_model,
            name=f"alias_{route.name}",
            tags=[tag],
            include_in_schema=True,
            summary=route.summary,
            description=route.description,
            dependencies=route.dependencies,
        )
        count += 1
    return count


# ---------------------------------------------------------------------------
# /api/health — packet-aligned liveness endpoint.
# ---------------------------------------------------------------------------
health_router = APIRouter(prefix="/api/health", tags=["Health"])


@health_router.get("")
@health_router.get("/")
async def health_root() -> Dict[str, Any]:
    """Return backend liveness + a coarse service inventory."""
    uptime_s = int(time.time() - _BOOT_TS)
    return {
        "status": "ok",
        "service": "atlas-backend",
        "uptime_seconds": uptime_s,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "systems": [
            "memory-bank",
            "knowledge-bank",
            "source-registry",
            "task-engine",
            "teaching-engine",
            "research-engine",
            "intelligence-router",
            "twins",
            "weaver",
            "robot",
            "nir",
        ],
    }


@health_router.get("/ping")
async def health_ping() -> Dict[str, str]:
    return {"pong": "ok"}


# ---------------------------------------------------------------------------
# /api/intelligence — aggregate LLM + persona introspection.
# ---------------------------------------------------------------------------
intelligence_router = APIRouter(prefix="/api/intelligence", tags=["Intelligence"])


@intelligence_router.get("/status")
async def intelligence_status() -> Dict[str, Any]:
    """Aggregate view of routing / persona / LLM configuration."""
    personas: List[Dict[str, str]] = []
    provider_info: Dict[str, Any] = {}

    try:  # persona registry
        from routes.persona import list_personas  # type: ignore

        personas_out = await list_personas()
        personas = [p.model_dump() if hasattr(p, "model_dump") else dict(p) for p in personas_out]
    except Exception as exc:  # pragma: no cover — introspection best-effort
        personas = [{"error": str(exc)}]

    try:  # multi-provider llm persona/model mapping
        from routes.llm import list_persona_models  # type: ignore

        provider_info = await list_persona_models()
    except Exception as exc:  # pragma: no cover
        provider_info = {"error": str(exc)}

    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "personas": personas,
        "providers": provider_info,
        "routes": {
            "memory": "/api/memory",
            "knowledge": "/api/knowledge",
            "sources": "/api/sources",
            "tasks": "/api/tasks",
            "teaching": "/api/teaching",
            "research": "/api/research",
            "intelligence": "/api/intelligence",
            "health": "/api/health",
        },
    }


@intelligence_router.get("/personas")
async def intelligence_personas() -> Dict[str, Any]:
    try:
        from routes.persona import list_personas  # type: ignore

        personas_out = await list_personas()
        return {
            "personas": [
                p.model_dump() if hasattr(p, "model_dump") else dict(p)
                for p in personas_out
            ]
        }
    except Exception as exc:
        return {"personas": [], "error": str(exc)}


@intelligence_router.get("/providers")
async def intelligence_providers() -> Dict[str, Any]:
    try:
        from routes.llm import list_persona_models  # type: ignore

        return await list_persona_models()
    except Exception as exc:
        return {"error": str(exc)}


# ---------------------------------------------------------------------------
# register_packet_aliases — one-shot wiring called from server.py.
# ---------------------------------------------------------------------------
def register_packet_aliases(app: FastAPI) -> Dict[str, int]:
    """Mount the two new routers and clone existing routers under the
    packet-aligned prefixes. Returns a small map of alias counts for
    logging."""
    # Import here (not at module top) so this file remains cheap to import
    # even if some downstream routers have side-effects at import time.
    from routes.memory import router as memory_router
    from routes.research_sources import router as research_sources_router
    from routes.research_orchestrator import router as research_orch_router
    from routes.subjects import router as subjects_router
    from routes.transcripts import router as transcripts_router
    from routes.knowledge_network import router as knowledge_network_router
    from routes.kbase import router as kbase_router
    from routes.youtube import router as youtube_router
    from routes.dev_pipeline import router as dev_pipeline_router
    from atlas_core import atlas_router as atlas_core_router

    app.include_router(health_router)
    app.include_router(intelligence_router)
    app.include_router(knowledge_network_router)
    app.include_router(dev_pipeline_router)

    counts: Dict[str, int] = {}
    counts["memory"] = mount_alias(app, memory_router, "/api/membank", "/api/memory")
    counts["sources"] = mount_alias(
        app, research_sources_router, "/api/research-sources", "/api/sources"
    )
    counts["tasks"] = mount_alias(
        app, research_orch_router, "/api/research-orch", "/api/tasks"
    )
    counts["teaching"] = mount_alias(
        app, atlas_core_router, "/atlas/teach", "/api/teaching"
    )
    counts["knowledge_subjects"] = mount_alias(
        app, subjects_router, "/api/subjects", "/api/knowledge/subjects-bank"
    )
    counts["knowledge_transcripts"] = mount_alias(
        app, transcripts_router, "/api/transcripts", "/api/knowledge/transcripts"
    )

    # --- Unified /api/knowledge-network/* deep aliases --------------------
    kn_prefix = "/api/knowledge-network"
    counts["kn_sources_deep"] = mount_alias(
        app, research_sources_router, "/api/research-sources", f"{kn_prefix}/research-sources"
    )
    counts["kn_kbase"] = mount_alias(
        app, kbase_router, "/api/kbase", f"{kn_prefix}/kbase"
    )
    counts["kn_youtube"] = mount_alias(
        app, youtube_router, "/api/youtube", f"{kn_prefix}/youtube"
    )
    counts["kn_subjects_deep"] = mount_alias(
        app, subjects_router, "/api/subjects", f"{kn_prefix}/subjects-registry"
    )
    # Memory Bank — only the /research write path is exposed under KN.
    counts["kn_membank_research"] = mount_alias(
        app, memory_router, "/api/membank/research", f"{kn_prefix}/membank/research"
    )
    return counts

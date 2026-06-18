"""Environments service — Phase D2.

Owns one MongoDB collection (`twin_environments`) and a thin assignment
API. Cross-checks twin specs against environment ambient conditions
before accepting a binding — if a twin requires O2 > 19 % and the
environment provides 5 %, we flag it.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from motor.motor_asyncio import AsyncIOMotorClient

from models.environment_models import (
    EnvironmentAssignmentResult,
    EnvironmentCategory,
    Obstacle,
    TwinEnvironment,
)
from services import memory_bank as mb

logger = logging.getLogger("atlas.environments")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _envs():
    return _db()["twin_environments"]


def _twins():
    return _db()["digital_twins"]


def _strip(d: Dict[str, Any]) -> Dict[str, Any]:
    d.pop("_id", None)
    return d


# --- Registry ---------------------------------------------------------------
async def register_environment(env: TwinEnvironment) -> Dict[str, Any]:
    doc = env.model_dump()
    await _envs().insert_one(doc.copy())
    await mb.auto_store(
        f"ENVIRONMENT registered · {env.name} ({env.category.value})\n"
        f"Bounds {env.bounds_m} m · gravity {env.gravity_m_s2} m/s²\n"
        f"Temp {env.temp_c_range[0]}–{env.temp_c_range[1]} °C · O2 {env.atmo_o2_pct} %",
        persona=env.owner_agent, category="project",
        source_type="twin_environment", source_id=env.id,
        tags=["environment", env.category.value] + list(env.tags or []),
    )
    return _strip(doc)


async def list_environments(category: Optional[str] = None) -> List[Dict[str, Any]]:
    q: Dict[str, Any] = {}
    if category:
        q["category"] = category
    cur = _envs().find(q, {"_id": 0}).sort("created_at", -1)
    return [d async for d in cur]


async def get_environment(env_id: str) -> Optional[Dict[str, Any]]:
    return await _envs().find_one({"id": env_id}, {"_id": 0})


async def delete_environment(env_id: str) -> int:
    # Unbind any twins first
    twins = await _twins().find(
        {"bound_environment_id": env_id}, {"id": 1}
    ).to_list(length=200)
    for t in twins:
        await _twins().update_one(
            {"id": t["id"]}, {"$unset": {"bound_environment_id": ""}},
        )
    r = await _envs().delete_one({"id": env_id})
    return r.deleted_count


# --- Twin <-> Environment binding ------------------------------------------
async def _check_compatibility(
    twin: Dict[str, Any], env: Dict[str, Any],
) -> List[str]:
    """Light, explainable checks. NEVER raises — returns a list of human-
    readable issues that the architect / Council can rule on."""
    issues: List[str] = []
    spec = twin.get("spec") or {}
    needs = (spec.get("needs") or {}) if isinstance(spec, dict) else {}

    # Atmospheric O2 vs need
    if "min_o2_pct" in needs:
        min_o2 = float(needs["min_o2_pct"])
        avail_o2 = float(env.get("atmo_o2_pct") or 0)
        if avail_o2 < min_o2:
            issues.append(
                f"O2 mismatch · twin requires ≥ {min_o2}%, env provides {avail_o2}%"
            )

    # Operating temperature
    if "temp_c_range" in needs:
        t_min, t_max = needs["temp_c_range"]
        e_min, e_max = env.get("temp_c_range", [None, None])
        if e_min is not None and (e_min < t_min or e_max > t_max):
            issues.append(
                f"Temperature mismatch · twin operates {t_min}–{t_max} °C, "
                f"env runs {e_min}–{e_max} °C"
            )

    # Gravity (e.g. drone tuned for Earth in lunar env)
    if "gravity_m_s2" in needs:
        g_need = float(needs["gravity_m_s2"])
        g_env = float(env.get("gravity_m_s2") or 9.81)
        if abs(g_need - g_env) / max(g_need, 0.01) > 0.10:    # > 10 % mismatch
            issues.append(
                f"Gravity mismatch · twin tuned for {g_need} m/s², env at {g_env} m/s²"
            )

    # Spatial bounds vs twin footprint
    if "footprint_m" in spec:
        fp = spec["footprint_m"]                          # [x, y, z]
        bounds = env.get("bounds_m") or [0, 0, 0]
        if any(fp[i] > bounds[i] for i in range(min(3, len(fp), len(bounds)))):
            issues.append(
                f"Footprint overflow · twin {fp} m doesn't fit in env {bounds} m"
            )

    return issues


async def bind_twin(
    twin_id: str, environment_id: str, *, force: bool = False,
) -> EnvironmentAssignmentResult:
    twin = await _twins().find_one({"id": twin_id}, {"_id": 0})
    env = await get_environment(environment_id)
    if not twin or not env:
        return EnvironmentAssignmentResult(
            ok=False, twin_id=twin_id, environment_id=environment_id,
            compatibility_issues=["twin or environment not found"],
        )

    issues = await _check_compatibility(twin, env)
    if issues and not force:
        return EnvironmentAssignmentResult(
            ok=False, twin_id=twin_id, environment_id=environment_id,
            compatibility_issues=issues,
        )

    # Update both sides
    await _twins().update_one(
        {"id": twin_id},
        {"$set": {"bound_environment_id": environment_id}},
    )
    if twin_id not in (env.get("twins_assigned") or []):
        await _envs().update_one(
            {"id": environment_id},
            {"$addToSet": {"twins_assigned": twin_id}},
        )

    await mb.auto_store(
        f"TWIN bound to ENVIRONMENT · twin={twin.get('name', twin_id)} → "
        f"env={env.get('name', environment_id)}"
        + (f" (forced over {len(issues)} issues)" if issues else ""),
        persona=twin.get("owner_agent", "ajani"), category="project",
        source_type="twin_environment_binding",
        source_id=f"{twin_id}:{environment_id}",
        tags=["environment", "binding"] + (["forced"] if issues else []),
    )
    return EnvironmentAssignmentResult(
        ok=True, twin_id=twin_id, environment_id=environment_id,
        compatibility_issues=issues,    # surfaced even on forced bind
    )


async def unbind_twin(twin_id: str) -> Dict[str, Any]:
    twin = await _twins().find_one({"id": twin_id}, {"_id": 0})
    if not twin:
        return {"ok": False, "reason": "twin not found"}
    env_id = twin.get("bound_environment_id")
    if not env_id:
        return {"ok": True, "twin_id": twin_id, "noop": True}
    await _twins().update_one(
        {"id": twin_id}, {"$unset": {"bound_environment_id": ""}},
    )
    await _envs().update_one(
        {"id": env_id}, {"$pull": {"twins_assigned": twin_id}},
    )
    return {"ok": True, "twin_id": twin_id, "unbound_from": env_id}


# --- Seed a few realistic environments -------------------------------------
SEED_ENVIRONMENTS: List[Dict[str, Any]] = [
    {
        "name": "Atlas Lab A",
        "category": EnvironmentCategory.INDOOR_LAB,
        "description": "Indoor workspace for prototype assembly and bench testing.",
        "bounds_m": (8.0, 6.0, 3.0),
        "temp_c_range": (20.0, 24.0),
        "humidity_pct_range": (35.0, 55.0),
        "ambient_lux_range": (500.0, 1200.0),
        "obstacles": [
            Obstacle(name="workbench", min_xyz=(0, 0, 0), max_xyz=(3, 0.8, 0.9), material="steel"),
            Obstacle(name="server-rack", min_xyz=(6, 5, 0), max_xyz=(8, 6, 2), material="aluminium"),
        ],
        "tags": ["primary", "atlas-hq"],
    },
    {
        "name": "Outdoor Test Field",
        "category": EnvironmentCategory.OUTDOOR_TERRAIN,
        "description": "Open grass field, 30 × 30 m. Drone & rover trials.",
        "bounds_m": (30.0, 30.0, 50.0),
        "temp_c_range": (-5.0, 35.0),
        "humidity_pct_range": (20.0, 95.0),
        "wind_m_s_range": (0.0, 8.0),
        "ambient_lux_range": (1000.0, 100000.0),
        "tags": ["primary", "outdoor"],
    },
    {
        "name": "Aerial Low Airspace",
        "category": EnvironmentCategory.AERIAL_LOW,
        "description": "0–500 m AGL, suburban density. Drone flight envelope.",
        "bounds_m": (1000.0, 1000.0, 500.0),
        "temp_c_range": (-10.0, 30.0),
        "wind_m_s_range": (0.0, 15.0),
        "tags": ["aerial"],
    },
    {
        "name": "Aquatic Surface (Lake Test)",
        "category": EnvironmentCategory.AQUATIC_SURFACE,
        "description": "Calm fresh-water lake, < 2 m depth. ASV trials.",
        "bounds_m": (200.0, 200.0, 2.0),
        "temp_c_range": (4.0, 25.0),
        "humidity_pct_range": (75.0, 100.0),
        "tags": ["aquatic"],
    },
    {
        "name": "Simulated Lunar Sandbox",
        "category": EnvironmentCategory.LUNAR,
        "description": "Virtual lunar surface — used for purely simulated rover trials.",
        "bounds_m": (1000.0, 1000.0, 10.0),
        "gravity_m_s2": 1.62,
        "temp_c_range": (-173.0, 127.0),
        "humidity_pct_range": (0.0, 0.0),
        "pressure_kpa": 0.0,
        "atmo_o2_pct": 0.0,
        "atmo_co2_ppm": 0.0,
        "wind_m_s_range": (0.0, 0.0),
        "tags": ["simulated", "off-world"],
    },
]


async def seed_if_needed() -> int:
    inserted = 0
    for spec in SEED_ENVIRONMENTS:
        if await _envs().find_one({"name": spec["name"]}):
            continue
        env = TwinEnvironment(**spec)
        await register_environment(env)
        inserted += 1
    return inserted

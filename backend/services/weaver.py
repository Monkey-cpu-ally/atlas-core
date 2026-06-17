"""
Weaver orchestrator — Phase 6.

Pipeline:
  1. parse blueprint        → ExtractedPart[] + BlueprintRelation[]
  2. enrich via parts_db    → library hits + confidence
  3. spawn a Digital Twin   → reuses Phase-5 registry + simulators
  4. build_plan(...)        → assembly order from Phase-5 ASSEMBLY sim
                              + tools/difficulty heuristics
  5. manufacturing_plan(...) → COST + TIMELINE sims rolled up
  6. failure_prediction(...) → FAILURE sim + missing-parts diff
  7. council deliberation   → reuses Phase-5 twin deliberation
  8. memory wiring          → project + blueprint memories via Phase-2 mb

Saves the full result document into `weaver_plans` so the architect can
retrieve plans later. Each plan is anchored to a twin_id; the twin is
where the heavy lifting (simulation history, council, memory) lives.
"""
import logging
import os
from typing import Any, Dict, List, Optional
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient

from models.weaver_models import (
    AssemblyStep,
    BlueprintInput,
    BuildPlan,
    CouncilOutcome,
    Difficulty,
    ExtractedPart,
    FailurePrediction,
    ManufacturingPlan,
    PartCategory,
    WeaverPlan,
)
from models.twin_models import (
    Component,
    Dependency,
    DigitalTwin,
    SimulationKind,
    TwinCategory,
    TwinState,
)
from services import blueprint_parser, digital_twin as dt, memory_bank as mb, parts_db

logger = logging.getLogger("atlas.weaver")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _plans():
    return _db()["weaver_plans"]


# --- Heuristics -------------------------------------------------------------
_TOOL_HINTS: Dict[PartCategory, List[str]] = {
    PartCategory.FASTENER:   ["Hex key set M2-M6", "Screwdriver set"],
    PartCategory.ELECTRONIC: ["Soldering iron", "Multimeter"],
    PartCategory.SENSOR:     ["Soldering iron", "Multimeter"],
    PartCategory.ACTUATOR:   ["Hex key set M2-M6", "Multimeter"],
    PartCategory.MATERIAL:   ["3D printer 200x200", "Cutting tool"],
    PartCategory.COMPONENT:  ["Hex key set M2-M6"],
    PartCategory.CONSUMABLE: [],
    PartCategory.TOOL:       [],
}


def _category_minutes(cat: PartCategory) -> float:
    return {
        PartCategory.FASTENER:   1.5,
        PartCategory.MATERIAL:   8.0,
        PartCategory.ELECTRONIC: 12.0,
        PartCategory.SENSOR:     8.0,
        PartCategory.ACTUATOR:   10.0,
        PartCategory.COMPONENT:  6.0,
        PartCategory.CONSUMABLE: 1.0,
        PartCategory.TOOL:       0.0,    # tools are not assembled
    }.get(cat, 5.0)


def _difficulty_from(total_minutes: float, has_electronics: bool,
                     has_machining: bool) -> Difficulty:
    if total_minutes < 60 and not has_electronics:
        return Difficulty.TRIVIAL
    if total_minutes < 240 and not has_machining:
        return Difficulty.EASY
    if total_minutes < 960:
        return Difficulty.MEDIUM
    if total_minutes < 2880:
        return Difficulty.HARD
    return Difficulty.EXPERT


# --- Twin spawning ----------------------------------------------------------
def _category_for_twin(parts: List[ExtractedPart]) -> TwinCategory:
    """Infer a sensible TwinCategory from the part mix."""
    cats = [p.category for p in parts]
    if any(c == PartCategory.ACTUATOR for c in cats):
        return TwinCategory.ROBOT
    if any(c == PartCategory.SENSOR for c in cats):
        return TwinCategory.DEVICE
    if any(c == PartCategory.ELECTRONIC for c in cats):
        return TwinCategory.DEVICE
    return TwinCategory.DEVICE


async def _spawn_twin(
    title: str, description: Optional[str], owner_agent: str,
    related_project_id: Optional[str],
    parts: List[ExtractedPart], relations,
    library_by_id: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Create a DigitalTwin from the extracted parts, pulling library cost
    and lead time when available."""
    components: List[Component] = []
    id_by_name: Dict[str, str] = {}
    for p in parts:
        comp_id = uuid4().hex[:10]
        id_by_name[p.name.lower()] = comp_id
        lib = library_by_id.get(p.library_part_id or "") if p.library_part_id else None
        components.append(Component(
            id=comp_id,
            name=p.name,
            quantity=p.quantity,
            unit=p.unit,
            material=(lib or {}).get("material"),
            cost_per_unit=(lib or {}).get("default_cost"),
            lead_time_days=(lib or {}).get("default_lead_time_days"),
        ))
    deps: List[Dependency] = []
    for r in (relations or []):
        a = id_by_name.get(str(r.from_part).lower())
        b = id_by_name.get(str(r.to_part).lower())
        if a and b and a != b:
            deps.append(Dependency(from_component=a, to_component=b,
                                   kind=r.relation or "connects_to"))
    twin = DigitalTwin(
        name=title,
        category=_category_for_twin(parts),
        owner_agent=owner_agent,
        related_project_id=related_project_id,
        description=description,
        tags=["weaver"],
        state=TwinState(components=components, dependencies=deps),
    )
    return await dt.register_twin(twin)


# --- Build plan -------------------------------------------------------------
def _build_plan(
    parts: List[ExtractedPart], assembly_sim_timeline: List[Dict[str, Any]],
) -> BuildPlan:
    by_name = {p.name.lower(): p for p in parts}
    tools: List[str] = []
    seen_tools = set()
    steps: List[AssemblyStep] = []
    total_minutes = 0.0
    for entry in assembly_sim_timeline or []:
        comp_name = entry.get("component", "")
        p = by_name.get(comp_name.lower())
        if not p:
            continue
        tool_list = _TOOL_HINTS.get(p.category, [])
        for t in tool_list:
            if t not in seen_tools:
                tools.append(t)
                seen_tools.add(t)
        minutes = _category_minutes(p.category) * max(p.quantity, 1.0)
        cautions: List[str] = []
        if p.category in (PartCategory.ELECTRONIC, PartCategory.SENSOR):
            cautions.append("Check polarity before soldering.")
        if p.category == PartCategory.ACTUATOR:
            cautions.append("Confirm torque + free shaft before powering up.")
        steps.append(AssemblyStep(
            step=int(entry.get("step", len(steps) + 1)),
            description=f"Install {comp_name} ({int(p.quantity)} {p.unit})",
            component_ids=[],   # the planner doesn't have twin ids in scope
            tools_required=tool_list,
            estimated_minutes=minutes,
            cautions=cautions,
        ))
        total_minutes += minutes
    has_electronics = any(
        p.category in (PartCategory.ELECTRONIC, PartCategory.SENSOR, PartCategory.ACTUATOR)
        for p in parts
    )
    has_machining = any(
        p.category == PartCategory.MATERIAL for p in parts
    )
    return BuildPlan(
        assembly_order=steps,
        tools_required=tools,
        materials_required=[
            {"name": p.name, "quantity": p.quantity, "unit": p.unit}
            for p in parts if p.category == PartCategory.MATERIAL
        ],
        difficulty=_difficulty_from(total_minutes, has_electronics, has_machining),
        total_estimated_minutes=round(total_minutes, 1),
    )


def _manufacturing_plan(
    cost_sim: Dict[str, Any], timeline_sim: Dict[str, Any], parts: List[ExtractedPart],
    library_by_id: Dict[str, Dict[str, Any]],
) -> ManufacturingPlan:
    metrics_cost = (cost_sim or {}).get("metrics", {})
    metrics_time = (timeline_sim or {}).get("metrics", {})
    bom = (cost_sim or {}).get("bom") or []
    # find longest-lead part
    longest_lead, longest_lead_part = 0.0, None
    for p in parts:
        if p.library_part_id and p.library_part_id in library_by_id:
            lib = library_by_id[p.library_part_id]
            lt = float(lib.get("default_lead_time_days") or 0.0)
            if lt > longest_lead:
                longest_lead = lt
                longest_lead_part = p.name
    return ManufacturingPlan(
        materials_cost=float(metrics_cost.get("materials_cost", 0.0)),
        labour_cost=float(metrics_cost.get("labour_estimate", 0.0)),
        total_cost=float(metrics_cost.get("total_estimate", 0.0)),
        critical_path_days=float(metrics_time.get("critical_path_days", 0.0)),
        longest_lead_part=longest_lead_part,
        bom=bom,
        resource_notes=(cost_sim or {}).get("warnings") or [],
    )


def _failure_prediction(
    failure_sim: Dict[str, Any], parts: List[ExtractedPart],
) -> FailurePrediction:
    missing = [p.name for p in parts if not p.library_part_id]
    weak: List[str] = list((failure_sim or {}).get("warnings") or [])
    spofs = [w for w in weak if "single-point" in w.lower() or "spof" in w.lower()]
    fail = (failure_sim or {}).get("failures") or []
    score_metric = float((failure_sim or {}).get("score", 1.0))
    # risk_score is the inverse of the sim score, plus a missing-parts penalty.
    risk = (1.0 - score_metric) + 0.05 * len(missing)
    risk = max(0.0, min(1.0, round(risk, 3)))
    notes: List[str] = []
    if missing:
        notes.append(
            f"{len(missing)} part(s) are NOT in the library; defaults assumed."
        )
    if fail:
        notes.append(f"Hard failure(s) reported: {len(fail)}")
    return FailurePrediction(
        risk_score=risk,
        missing_parts=missing,
        weak_designs=weak,
        single_points_of_failure=spofs,
        notes=notes,
    )


# --- Public pipeline --------------------------------------------------------
async def plan_from_blueprint(
    *, title: str, description: Optional[str], owner_agent: str,
    related_project_id: Optional[str], blueprint: BlueprintInput,
    deliberate: bool = True,
) -> WeaverPlan:
    # 1) parse the blueprint
    parts, relations = await blueprint_parser.parse(blueprint)
    if not parts:
        raise ValueError("Blueprint produced no parts; nothing to plan.")
    # 2) library enrichment
    parts = await blueprint_parser.match_against_library(parts)
    library_by_id: Dict[str, Dict[str, Any]] = {}
    for p in parts:
        if p.library_part_id:
            lib = await parts_db.get_part(p.library_part_id)
            if lib:
                library_by_id[p.library_part_id] = lib
    # 3) spawn the digital twin (Phase 5 registry)
    twin_doc = await _spawn_twin(
        title=title, description=description, owner_agent=owner_agent,
        related_project_id=related_project_id,
        parts=parts, relations=relations, library_by_id=library_by_id,
    )
    twin_id = twin_doc["id"]
    # 4) run the Phase-5 sims we need for the build/manufacturing/failure plans
    asm_sim = (await dt.run_and_persist_simulation(twin_id, SimulationKind.ASSEMBLY)).model_dump()
    cost_sim = (await dt.run_and_persist_simulation(twin_id, SimulationKind.COST)).model_dump()
    time_sim = (await dt.run_and_persist_simulation(twin_id, SimulationKind.TIMELINE)).model_dump()
    fail_sim = (await dt.run_and_persist_simulation(twin_id, SimulationKind.FAILURE)).model_dump()
    # 5) compose plans
    build = _build_plan(parts, asm_sim.get("timeline") or [])
    manuf = _manufacturing_plan(cost_sim, time_sim, parts, library_by_id)
    failp = _failure_prediction(fail_sim, parts)
    # 6) council deliberation on the failure sim (highest-signal one)
    council_outcome: Optional[CouncilOutcome] = None
    if deliberate:
        delib = await dt.deliberate(twin_id, simulation_id=fail_sim.get("id"))
        if delib:
            council_outcome = CouncilOutcome(
                verdict=delib.verdict,
                final_text=delib.final_text,
                voices=[v.model_dump() for v in delib.voices],
            )
    # 7) persist + memory wiring
    plan = WeaverPlan(
        title=title, description=description, owner_agent=owner_agent,
        related_project_id=related_project_id,
        blueprint=blueprint,
        parts_extracted=parts,
        twin_id=twin_id,
        build_plan=build,
        manufacturing_plan=manuf,
        failure_prediction=failp,
        council=council_outcome,
    )
    await _plans().insert_one(plan.model_dump())
    summary = (
        f"WEAVER PLAN · {title}\n"
        f"twin_id={twin_id} · parts={len(parts)} · "
        f"difficulty={build.difficulty.value} · risk={failp.risk_score} · "
        f"cost≈{manuf.total_cost} · critical_path≈{manuf.critical_path_days}d"
    )
    await mb.auto_store(
        summary, persona=owner_agent, category="blueprint",
        source_type="weaver", source_id=plan.id,
        tags=["weaver", twin_doc.get("category", "device")],
    )
    return plan


async def get_plan(plan_id: str) -> Optional[Dict[str, Any]]:
    return await _plans().find_one({"id": plan_id}, {"_id": 0})


async def list_plans(
    *, owner_agent: Optional[str] = None, project_id: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    filt: Dict[str, Any] = {}
    if owner_agent:
        filt["owner_agent"] = owner_agent
    if project_id:
        filt["related_project_id"] = project_id
    cur = _plans().find(filt, {"_id": 0}).sort("created_at", -1).limit(limit)
    return [d async for d in cur]


async def delete_plan(plan_id: str, *, drop_twin: bool = False) -> bool:
    plan = await _plans().find_one({"id": plan_id})
    if not plan:
        return False
    await _plans().delete_one({"id": plan_id})
    if drop_twin and plan.get("twin_id"):
        await dt.delete_twin(plan["twin_id"])
    return True

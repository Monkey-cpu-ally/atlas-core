"""
Digital Twin service — Phase 5.

Owns the three MongoDB collections that back the twin engine:
  * digital_twins         — registry rows (one per twin)
  * twin_simulations      — every simulation result (history kept)
  * twin_deliberations    — council voices + final verdict per twin/sim

State revisions are kept inline on the twin doc (one current state) — the
architect can read prior revisions from the simulation rows that snapshot
`revision` at run time.

This service is hardware-agnostic by design. Real-world I/O, robot control,
and physics integration land in Phase 7 (Robot Control Layer); Weaver
(Phase 6) consumes the same registry through `integrations`.
"""
import logging
import os
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient
from services import memory_bank as mb
from models.twin_models import (
    CouncilDeliberation,
    DeliberationVoice,
    DigitalTwin,
    SimulationKind,
    SimulationResult,
    TwinCategory,
    TwinState,
    TwinStatus,
)
from services.twin_simulator import simulate as run_simulation

logger = logging.getLogger("atlas.digital_twin")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _twins():
    return _db()["digital_twins"]


def _sims():
    return _db()["twin_simulations"]


def _delibs():
    return _db()["twin_deliberations"]


# --- Registry ---------------------------------------------------------------
async def register_twin(twin: DigitalTwin) -> Dict[str, Any]:
    doc = twin.model_dump()
    await _twins().insert_one(doc.copy())
    # Permanent project memory — anchoring this twin in long-term recall.
    await mb.auto_store(
        f"TWIN registered · {twin.name} ({twin.category.value})\n"
        f"Owner: {twin.owner_agent} · Project: {twin.related_project_id or '—'}\n"
        f"{twin.description or ''}",
        persona=twin.owner_agent,
        category="project",
        source_type="twin",
        source_id=twin.id,
        tags=[twin.category.value, "twin"] + (twin.tags or []),
    )
    return _strip(doc)


async def get_twin(twin_id: str) -> Optional[Dict[str, Any]]:
    doc = await _twins().find_one({"id": twin_id}, {"_id": 0})
    return doc


async def list_twins(
    *,
    category: Optional[str] = None,
    owner_agent: Optional[str] = None,
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    filt: Dict[str, Any] = {}
    if category:
        filt["category"] = category
    if owner_agent:
        filt["owner_agent"] = owner_agent
    if project_id:
        filt["related_project_id"] = project_id
    if status:
        filt["state.status"] = status
    cur = _twins().find(filt, {"_id": 0}).sort("updated_at", -1).limit(limit)
    return [d async for d in cur]


async def update_state(twin_id: str, new_state: TwinState) -> Optional[Dict[str, Any]]:
    twin = await _twins().find_one({"id": twin_id})
    if not twin:
        return None
    prev_rev = int(((twin.get("state") or {}).get("revision")) or 0)
    payload = new_state.model_dump()
    payload["revision"] = prev_rev + 1
    payload["updated_at"] = _now()
    await _twins().update_one(
        {"id": twin_id},
        {"$set": {"state": payload, "updated_at": payload["updated_at"]}},
    )
    return await get_twin(twin_id)


async def delete_twin(twin_id: str) -> bool:
    res = await _twins().delete_one({"id": twin_id})
    if res.deleted_count:
        # Cascade: drop sims + deliberations
        await _sims().delete_many({"twin_id": twin_id})
        await _delibs().delete_many({"twin_id": twin_id})
        return True
    return False


# --- Simulation -------------------------------------------------------------
async def run_and_persist_simulation(
    twin_id: str, kind: SimulationKind,
) -> Optional[SimulationResult]:
    twin_doc = await _twins().find_one({"id": twin_id}, {"_id": 0})
    if not twin_doc:
        return None
    twin = DigitalTwin(**twin_doc)
    result = run_simulation(twin, kind)
    await _sims().insert_one(result.model_dump())
    await _twins().update_one(
        {"id": twin_id},
        {"$set": {
            "last_simulation_id": result.id,
            "state.status": TwinStatus.SIMULATED.value,
            "updated_at": _now(),
        }},
    )
    # Memory wiring:
    #   * a permanent project memory describing the sim
    #   * a research-category "success-memory" or "failure-memory" depending on result
    body = (
        f"TWIN SIM · {twin.name} · {kind.value}\n"
        f"score={result.score:.2f} ok={result.ok}\n"
        f"findings:\n- " + "\n- ".join(result.findings[:6])
        + (
            "\n\nfailures:\n- " + "\n- ".join(result.failures[:6])
            if result.failures else ""
        )
    )
    await mb.auto_store(
        body, persona=twin.owner_agent, category="project",
        source_type="twin_sim", source_id=result.id,
        tags=[twin.category.value, kind.value, "twin"],
    )
    success_tag = "success-memory" if result.ok else "failure-memory"
    await mb.auto_store(
        f"{success_tag} · {twin.name} · {kind.value}\n" + body,
        persona=twin.owner_agent, category="research",
        source_type="twin_sim", source_id=result.id,
        tags=[twin.category.value, kind.value, success_tag, "twin"],
    )
    return result


async def list_simulations(twin_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    cur = _sims().find({"twin_id": twin_id}, {"_id": 0}).sort("created_at", -1).limit(limit)
    return [d async for d in cur]


async def get_simulation(sim_id: str) -> Optional[Dict[str, Any]]:
    return await _sims().find_one({"id": sim_id}, {"_id": 0})


# --- Council deliberation ---------------------------------------------------
PERSONA_ROLES: Dict[str, Dict[str, str]] = {
    "ajani": {
        "role": "engineering",
        "system": (
            "You are Ajani, Zulu warrior-engineer. Given a digital twin and "
            "its latest simulation result, write 3-4 short paragraphs on "
            "(a) engineering soundness, (b) manufacturing risks, "
            "(c) what would you build first, (d) one ENGINEERING_FLAG if any. "
            "Be specific. If everything looks good, say so clearly."
        ),
    },
    "minerva": {
        "role": "science",
        "system": (
            "You are Minerva, Greek goddess of wisdom and science. Given a digital twin "
            "and its simulation, write 3-4 short paragraphs on "
            "(a) environmental impact, (b) underlying physical principles, "
            "(c) one educational explanation a curious learner would benefit from, "
            "(d) one SCIENCE_FLAG if a key assumption deserves scrutiny."
        ),
    },
    "hermes": {
        "role": "validation",
        "system": (
            "You are Hermes, Maasai pattern hunter and validator. Given a twin + sim, "
            "write 3-4 short paragraphs on (a) internal consistency, "
            "(b) optimisation opportunities, (c) any pattern you have seen fail before "
            "in similar projects, (d) one VALIDATION_FLAG if anything looks off."
        ),
    },
}


async def deliberate(
    twin_id: str,
    *,
    simulation_id: Optional[str] = None,
) -> Optional[CouncilDeliberation]:
    twin_doc = await _twins().find_one({"id": twin_id}, {"_id": 0})
    if not twin_doc:
        return None
    twin = DigitalTwin(**twin_doc)

    sim_doc: Optional[Dict[str, Any]] = None
    if simulation_id:
        sim_doc = await get_simulation(simulation_id)
    elif twin_doc.get("last_simulation_id"):
        sim_doc = await get_simulation(twin_doc["last_simulation_id"])

    context = _build_context(twin, sim_doc)

    from services.llm_provider import send as llm_send
    voices: List[DeliberationVoice] = []
    for persona, cfg in PERSONA_ROLES.items():
        try:
            res = await llm_send(persona, cfg["system"], context,
                                 session_id=f"twin-delib-{twin_id}-{persona}")
            text = (res.get("text") or "").strip()
        except Exception as exc:    # noqa: BLE001
            logger.warning("twin deliberation %s failed: %s", persona, exc)
            text = f"(unable to reach {persona}: {exc})"
        flags = _extract_flags(text)
        voices.append(DeliberationVoice(persona=persona, role=cfg["role"], text=text, flags=flags))

    # Council verdict: simple aggregator. If any persona raised a *_FLAG
    # the council recommends revision; otherwise approve.
    flag_count = sum(len(v.flags) for v in voices)
    if not all(v.text and not v.text.startswith("(unable") for v in voices):
        verdict = "pending"
        final_text = (
            "Council could not assemble all three voices — at least one persona was unreachable. "
            "Re-run the deliberation once the LLM provider is healthy."
        )
    elif flag_count == 0:
        verdict = "approve"
        final_text = (
            f"Council approves twin '{twin.name}' for the next stage. "
            "All three voices found the simulation consistent with their domain checks."
        )
    elif flag_count >= 3:
        verdict = "reject"
        final_text = (
            f"Council rejects twin '{twin.name}' as currently specified. "
            f"Multiple ({flag_count}) flags raised across engineering/science/validation. "
            "Revise the state and re-simulate before re-deliberating."
        )
    else:
        verdict = "revise"
        final_text = (
            f"Council recommends revising twin '{twin.name}'. "
            f"{flag_count} flag(s) raised — address them and re-run the relevant simulation."
        )
    voices.append(DeliberationVoice(persona="council", role="verdict", text=final_text, flags=[]))

    delib = CouncilDeliberation(
        twin_id=twin_id, simulation_id=(sim_doc or {}).get("id"),
        voices=voices, verdict=verdict, final_text=final_text,
    )
    await _delibs().insert_one(delib.model_dump())
    await _twins().update_one(
        {"id": twin_id},
        {"$set": {
            "last_deliberation_id": delib.id,
            "state.status": (
                TwinStatus.APPROVED.value if verdict == "approve" else TwinStatus.SIMULATED.value
            ),
            "updated_at": _now(),
        }},
    )

    # Permanent council memory + readable deliberation in research memory
    council_body = (
        f"COUNCIL · TWIN {twin.name}\nverdict={verdict}\n\n"
        + "\n\n".join(f"[{v.persona.upper()} · {v.role}] {v.text}" for v in voices)
    )
    await mb.auto_store(council_body, persona="council", category="council",
                        source_type="twin_deliberation", source_id=delib.id,
                        tags=[twin.category.value, "twin", verdict])
    return delib


# --- Helpers ---------------------------------------------------------------
def _build_context(twin: DigitalTwin, sim: Optional[Dict[str, Any]]) -> str:
    parts = [
        f"TWIN: {twin.name} ({twin.category.value})",
        f"OWNER: {twin.owner_agent}",
        f"DESCRIPTION: {twin.description or '—'}",
        f"REV: {twin.state.revision}",
        f"COMPONENTS ({len(twin.state.components)}): "
        + ", ".join(f"{c.name}×{c.quantity}{c.unit}" for c in twin.state.components[:12]),
        f"DEPENDENCIES: {len(twin.state.dependencies)}",
    ]
    if twin.state.energy:
        parts.append(
            f"ENERGY: peak={twin.state.energy.peak_w}W "
            f"avg={twin.state.energy.average_w}W "
            f"daily={twin.state.energy.daily_wh}Wh "
            f"source={twin.state.energy.source}"
        )
    if twin.state.dimensions:
        parts.append(
            f"DIMENSIONS: L={twin.state.dimensions.length_m}m "
            f"W={twin.state.dimensions.width_m}m "
            f"H={twin.state.dimensions.height_m}m"
        )
    if sim:
        parts.append(
            f"\nSIM ({sim.get('kind')}): ok={sim.get('ok')} score={sim.get('score')}\n"
            f"findings:\n- " + "\n- ".join((sim.get("findings") or [])[:8])
            + (
                "\nfailures:\n- " + "\n- ".join((sim.get("failures") or [])[:6])
                if sim.get("failures") else ""
            )
        )
    parts.append("\nWrite your assessment now.")
    return "\n".join(parts)


def _extract_flags(text: str) -> List[str]:
    flags = []
    for tag in ("ENGINEERING_FLAG", "SCIENCE_FLAG", "VALIDATION_FLAG"):
        if tag in (text or ""):
            flags.append(tag)
    return flags


def _strip(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Mongo `_id` never reaches the API."""
    return {k: v for k, v in doc.items() if k != "_id"}


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()

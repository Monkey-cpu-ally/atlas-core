"""
Sandbox routes — save/replay configurations, mastery-curve runs, and
AI-suggested slider tweaks for the InteractiveSandbox in the HUD.

All endpoints are prefixed /api/sandbox/* so the K8s ingress routes them
to the FastAPI backend.
"""
import json
import logging
import os
import re
from datetime import datetime, timezone, date
from typing import Any, Dict, List, Optional
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

load_dotenv()

logger = logging.getLogger("atlas.sandbox")

router = APIRouter(prefix="/api/sandbox", tags=["Sandbox"])

# --- MongoDB ----------------------------------------------------------------
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "atlas_core")
_client = AsyncIOMotorClient(MONGO_URL)
db = _client[DB_NAME]
runs_col = db["sandbox_runs"]
saved_col = db["sandbox_saved"]

# Persona system prompts for the AI Suggest endpoint.
PERSONA_VOICES = {
    "ajani": (
        "You are Ajani, Zulu warrior-engineer. Calm, direct, structural. "
        "When suggesting a slider tweak, name ONE control to change and a "
        "specific new value, with a short reason rooted in physics or engineering."
    ),
    "minerva": (
        "You are Minerva, Yoruba wisdom keeper. Warm, narrative. When suggesting "
        "a slider tweak, name ONE control to change with a specific value, and "
        "explain it in terms of life, balance, and who is affected."
    ),
    "hermes": (
        "You are Hermes, Maasai pattern hunter. Precise, sometimes funny. When "
        "suggesting a slider tweak, name ONE control and a specific value, then "
        "explain the pattern or edge case in one tight line."
    ),
}

SUGGEST_SYSTEM = (
    "Output ONLY a JSON object with this exact shape, no prose, no fences:\n"
    "{\n"
    '  "control": "<one of the control keys exactly as provided>",\n'
    '  "value": <integer within the control min..max range>,\n'
    '  "reason": "<one or two short sentences in the persona voice>"\n'
    "}\n"
    "Pick the single change with the biggest expected lift in the Atlas Score "
    "that does NOT push the design into the failure modes provided."
)


class RunRecord(BaseModel):
    lab_key: str
    values: Dict[str, float]
    score: int = Field(ge=0, le=100)
    output: Optional[float] = None
    stability: Optional[float] = None
    failure: bool = False


class SavedConfig(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    lab_key: str
    values: Dict[str, float]


class SuggestRequest(BaseModel):
    lab_key: str
    title: str
    persona: str = "ajani"
    controls: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    failure_modes: List[str]
    mission: Optional[str] = None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today_str() -> str:
    return date.today().isoformat()


def _strip_id(doc: dict) -> dict:
    doc.pop("_id", None)
    return doc


def _extract_json_object(text: str) -> dict:
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise HTTPException(502, "AI did not return JSON")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise HTTPException(502, f"AI returned malformed JSON: {exc}") from exc


def _ci_suggestion(req: SuggestRequest, persona: str) -> dict:
    """Deterministic ATLAS_TEST_MODE adapter for the structured sandbox contract.

    This is explicitly test-only and selects from the caller-provided controls;
    it is never presented as a cloud-model response.
    """
    if not req.controls:
        raise HTTPException(422, "at least one control is required")
    # Prefer moving a control that is currently outside a stated-safe operating
    # region; otherwise move the first control one step toward its default.
    target = req.controls[0]
    for control in req.controls:
        current = control.get("current")
        default = control.get("default")
        if current is not None and default is not None and current != default:
            target = control
            break
    lo, hi = float(target["min"]), float(target["max"])
    desired = target.get("default", target.get("current", lo))
    value = int(round(max(lo, min(hi, float(desired)))))
    return {
        "control": str(target.get("key", "")),
        "value": value,
        "reason": "CI contract check: move this control toward its declared safe default.",
        "persona": persona,
        "model": "atlas-deterministic-ci-v1",
        "provider": "test",
        "timestamp": _utc_now_iso(),
    }


@router.post("/runs")
async def record_run(run: RunRecord):
    if run.score < 35:
        return {"recorded": False, "reason": "score below threshold"}
    day = _today_str()
    doc = {
        "id": str(uuid4()), "lab_key": run.lab_key, "values": run.values,
        "score": run.score, "output": run.output, "stability": run.stability,
        "failure": run.failure, "day": day, "created_at": _utc_now_iso(),
    }
    await runs_col.insert_one(doc.copy())
    cursor = runs_col.find({"lab_key": run.lab_key, "day": day}, {"_id": 1, "score": 1}).sort("score", -1)
    todays = await cursor.to_list(length=200)
    keep_ids = {d["_id"] for d in todays[:3]}
    drop_ids = [d["_id"] for d in todays if d["_id"] not in keep_ids]
    if drop_ids:
        await runs_col.delete_many({"_id": {"$in": drop_ids}})
    return {"recorded": True, "kept_today": min(len(todays), 3), "day": day}


@router.get("/runs/{lab_key}")
async def list_runs(lab_key: str, limit: int = Query(30, ge=1, le=180)):
    cursor = runs_col.find({"lab_key": lab_key}, {"_id": 0}).sort("created_at", -1).limit(limit)
    rows = await cursor.to_list(length=limit)
    rows.reverse()
    return {"lab_key": lab_key, "count": len(rows), "runs": rows}


@router.post("/saved")
async def save_config(cfg: SavedConfig):
    doc = {"id": str(uuid4()), "name": cfg.name.strip(), "lab_key": cfg.lab_key,
           "values": cfg.values, "created_at": _utc_now_iso()}
    await saved_col.insert_one(doc.copy())
    doc.pop("_id", None)
    return doc


@router.get("/saved/{lab_key}")
async def list_saved(lab_key: str, limit: int = Query(20, ge=1, le=100)):
    cursor = saved_col.find({"lab_key": lab_key}, {"_id": 0}).sort("created_at", -1).limit(limit)
    rows = await cursor.to_list(length=limit)
    return {"lab_key": lab_key, "count": len(rows), "configs": rows}


@router.delete("/saved/{config_id}")
async def delete_saved(config_id: str):
    res = await saved_col.delete_one({"id": config_id})
    if res.deleted_count == 0:
        raise HTTPException(404, "saved config not found")
    return {"deleted": config_id}


@router.post("/suggest")
async def suggest_tweak(req: SuggestRequest):
    """Ask the canonical persona LLM provider for one validated slider change."""
    persona_input = (req.persona or "ajani").lower()
    provider_persona = persona_input if persona_input in PERSONA_VOICES else "ajani"
    voice = PERSONA_VOICES[provider_persona]

    valid_keys = [c.get("key") for c in req.controls]
    if not valid_keys:
        raise HTTPException(422, "at least one control is required")

    if os.environ.get("ATLAS_TEST_MODE") == "1":
        return _ci_suggestion(req, persona_input)

    control_lines = [
        f"- {c.get('key')} ({c.get('label')}): current={c.get('current')}{c.get('unit','')}, "
        f"range={c.get('min')}..{c.get('max')}, default={c.get('default')}"
        for c in req.controls
    ]
    fail_lines = "\n".join(f"- {f}" for f in req.failure_modes) or "(none provided)"
    user_text = (
        f"LAB: {req.title} ({req.lab_key})\n"
        + (f"MISSION: {req.mission}\n" if req.mission else "")
        + "CONTROLS:\n" + "\n".join(control_lines) + "\n\n"
        + f"CURRENT METRICS: score={req.metrics.get('score')}, output={req.metrics.get('output')}, "
        f"stability={req.metrics.get('stability')}, failure={req.metrics.get('failure')}\n\n"
        + f"FAILURE MODES (must not trigger):\n{fail_lines}\n\n"
        + "What is the ONE most impactful tweak? Return the JSON object now."
    )
    system_msg = voice + "\n\n" + SUGGEST_SYSTEM

    from services.llm_provider import send as llm_send
    try:
        result = await llm_send(
            provider_persona,
            system_msg,
            user_text,
            model_override="claude-sonnet-4-5-20250929",
            session_id=f"sandbox-suggest-{provider_persona}-{uuid4().hex[:12]}",
        )
        raw = result.get("text") or ""
    except Exception as exc:
        logger.warning("AI suggest unavailable: %s", exc)
        raise HTTPException(503, "AI suggestion service unavailable") from exc

    suggestion = _extract_json_object(raw)
    ctrl = str(suggestion.get("control", "")).strip()
    if ctrl not in valid_keys:
        raise HTTPException(502, f"AI picked unknown control '{ctrl}'")
    target_ctrl = next(c for c in req.controls if c.get("key") == ctrl)
    try:
        val = float(suggestion.get("value"))
    except (TypeError, ValueError) as exc:
        raise HTTPException(502, f"AI returned non-numeric value: {exc}") from exc
    val = int(round(max(float(target_ctrl["min"]), min(float(target_ctrl["max"]), val))))

    return {
        "control": ctrl,
        "value": val,
        "reason": str(suggestion.get("reason", "")).strip(),
        "persona": persona_input,
        "model": result.get("model_used") or "unknown",
        "provider": result.get("provider_used") or "unknown",
        "timestamp": _utc_now_iso(),
    }

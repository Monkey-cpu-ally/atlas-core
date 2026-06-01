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
from emergentintegrations.llm.chat import LlmChat, UserMessage
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
runs_col = db["sandbox_runs"]      # mastery-curve history
saved_col = db["sandbox_saved"]    # named, pinned configurations

# --- LLM --------------------------------------------------------------------
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")

# Persona system prompts for the AI Suggest endpoint — kept tight so the
# response is always a single JSON object with control + value + reason.
PERSONA_VOICES = {
    "ajani": (
        "You are Ajani, Zulu warrior-engineer. Calm, direct, structural. "
        "When suggesting a slider tweak, name ONE control to change and a "
        "specific new value, with a short reason rooted in physics or "
        "engineering. African accent in word choice, never robotic."
    ),
    "minerva": (
        "You are Minerva, Yoruba wisdom keeper. Warm, narrative. When "
        "suggesting a slider tweak, name ONE control to change with a "
        "specific value, and explain it in terms of life, balance, and who "
        "is affected. Use a proverb when natural, never robotic."
    ),
    "hermes": (
        "You are Hermes, Maasai pattern hunter. Precise, sometimes funny. "
        "When suggesting a slider tweak, name ONE control and a specific "
        "value, then explain the pattern or edge case in one tight line. "
        "Never robotic."
    ),
}

SUGGEST_SYSTEM = (
    "Output ONLY a JSON object with this exact shape, no prose, no fences:\n"
    "{\n"
    '  "control": "<one of the control keys exactly as provided>",\n'
    '  "value": <integer within the control min..max range>,\n'
    '  "reason": "<one or two short sentences in the persona\'s voice>"\n'
    "}\n"
    "Pick the single change with the biggest expected lift in the Atlas "
    "Score that does NOT push the design into the failure modes provided. "
    "If the design is already passing, suggest the change that most "
    "strengthens stability or mastery."
)


# --- Pydantic models --------------------------------------------------------
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
    controls: List[Dict[str, Any]]      # [{key,label,min,max,unit,default,current}]
    metrics: Dict[str, Any]             # {score, output, stability, failure}
    failure_modes: List[str]            # human-readable list per lab
    mission: Optional[str] = None


# --- Helpers ----------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# 1) Mastery curve — auto-recorded runs (top-3 per lab per day)
# ---------------------------------------------------------------------------
@router.post("/runs")
async def record_run(run: RunRecord):
    """Persist a sandbox run for the mastery curve.

    Policy: only the top-3 scoring runs per (lab_key, calendar day) are
    retained. This produces a meaningful progression curve without flooding
    the collection with every slider tick.
    """
    if run.score < 35:
        # Below "Aware" — don't pollute the curve with throw-aways.
        return {"recorded": False, "reason": "score below threshold"}

    day = _today_str()
    doc = {
        "id": str(uuid4()),
        "lab_key": run.lab_key,
        "values": run.values,
        "score": run.score,
        "output": run.output,
        "stability": run.stability,
        "failure": run.failure,
        "day": day,
        "created_at": _utc_now_iso(),
    }

    await runs_col.insert_one(doc.copy())

    # Trim today's bucket back to the top 3 by score.
    cursor = runs_col.find(
        {"lab_key": run.lab_key, "day": day},
        {"_id": 1, "score": 1},
    ).sort("score", -1)
    todays = await cursor.to_list(length=200)
    keep_ids = {d["_id"] for d in todays[:3]}
    drop_ids = [d["_id"] for d in todays if d["_id"] not in keep_ids]
    if drop_ids:
        await runs_col.delete_many({"_id": {"$in": drop_ids}})

    return {"recorded": True, "kept_today": min(len(todays), 3), "day": day}


@router.get("/runs/{lab_key}")
async def list_runs(lab_key: str, limit: int = Query(30, ge=1, le=180)):
    """Return up-to `limit` recent runs for a lab, newest first.

    Used by the frontend to render the mastery sparkline. Results are
    grouped client-side by day if desired.
    """
    cursor = runs_col.find({"lab_key": lab_key}, {"_id": 0}).sort("created_at", -1).limit(limit)
    rows = await cursor.to_list(length=limit)
    # Re-sort chronological so the sparkline draws left→right.
    rows.reverse()
    return {"lab_key": lab_key, "count": len(rows), "runs": rows}


# ---------------------------------------------------------------------------
# 2) Saved / pinned configurations
# ---------------------------------------------------------------------------
@router.post("/saved")
async def save_config(cfg: SavedConfig):
    doc = {
        "id": str(uuid4()),
        "name": cfg.name.strip(),
        "lab_key": cfg.lab_key,
        "values": cfg.values,
        "created_at": _utc_now_iso(),
    }
    await saved_col.insert_one(doc.copy())
    doc.pop("_id", None)  # belt + suspenders for Motor's mutation
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


# ---------------------------------------------------------------------------
# 3) AI-suggested slider tweak
# ---------------------------------------------------------------------------
@router.post("/suggest")
async def suggest_tweak(req: SuggestRequest):
    """Ask the lead persona for one specific slider change to improve the
    current design. Returns {control, value, reason} as JSON."""
    if not EMERGENT_LLM_KEY:
        raise HTTPException(503, "AI services offline (missing EMERGENT_LLM_KEY)")

    persona = (req.persona or "ajani").lower()
    voice = PERSONA_VOICES.get(persona, PERSONA_VOICES["ajani"])

    # Build a compact, deterministic prompt so the LLM has the full lab state.
    control_lines = []
    valid_keys = []
    for c in req.controls:
        valid_keys.append(c.get("key"))
        control_lines.append(
            f"- {c.get('key')} ({c.get('label')}): "
            f"current={c.get('current')}{c.get('unit','')}, "
            f"range={c.get('min')}..{c.get('max')}, default={c.get('default')}"
        )
    fail_lines = "\n".join(f"- {f}" for f in req.failure_modes) or "(none provided)"

    user_text = (
        f"LAB: {req.title} ({req.lab_key})\n"
        + (f"MISSION: {req.mission}\n" if req.mission else "")
        + "CONTROLS:\n" + "\n".join(control_lines) + "\n\n"
        + f"CURRENT METRICS: score={req.metrics.get('score')}, "
        f"output={req.metrics.get('output')}, stability={req.metrics.get('stability')}, "
        f"failure={req.metrics.get('failure')}\n\n"
        + f"FAILURE MODES (must not trigger):\n{fail_lines}\n\n"
        + "What is the ONE most impactful tweak? Return the JSON object now."
    )

    system_msg = voice + "\n\n" + SUGGEST_SYSTEM
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"sandbox_suggest_{persona}_{_utc_now_iso()}",
        system_message=system_msg,
    ).with_model("anthropic", "claude-sonnet-4-5-20250929")

    try:
        raw = await chat.send_message(UserMessage(text=user_text))
    except Exception as exc:
        logger.warning("AI suggest failed: %s", exc)
        raise HTTPException(502, f"AI suggest failed: {exc}") from exc

    suggestion = _extract_json_object(raw)

    # Validate the LLM's output before sending it back to the UI.
    ctrl = str(suggestion.get("control", "")).strip()
    if ctrl not in valid_keys:
        raise HTTPException(502, f"AI picked unknown control '{ctrl}'")

    # Clamp value into the control's declared range.
    target_ctrl = next(c for c in req.controls if c.get("key") == ctrl)
    try:
        val = float(suggestion.get("value"))
    except (TypeError, ValueError) as exc:
        raise HTTPException(502, f"AI returned non-numeric value: {exc}") from exc
    val = max(float(target_ctrl["min"]), min(float(target_ctrl["max"]), val))
    # Snap to integer step (matches Slider step=1 in the UI).
    val = int(round(val))

    return {
        "control": ctrl,
        "value": val,
        "reason": str(suggestion.get("reason", "")).strip(),
        "persona": persona,
        "model": "claude-sonnet-4-5-20250929",
        "timestamp": _utc_now_iso(),
    }

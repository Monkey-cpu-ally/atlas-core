"""ATLAS Core v1 — FastAPI entrypoint.

Exposes the full cognitive stack under `/atlas/...` routes. Two ways to run:

  Standalone::

      cd /app
      python -m uvicorn atlas_core.app.main:app --port 8002 --reload

  Mounted on another FastAPI app::

      from atlas_core import atlas_router
      app.include_router(atlas_router, prefix="/api")
      # ↑ routes will then live at /api/atlas/...

The HUD frontend is not touched by this module.
"""
from __future__ import annotations

import logging
import os
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ..archive_engine import scan_bytes, entry_to_dict
from ..blueprint_engine import design
from ..council import assemble, route
from ..cores import CORES, get_core
from ..memory import memory
from ..shield_core import (
    IdentityDriftError,
    detect_identity_attack,
    identity_status,
    is_permitted,
    quarantine_upload,
    sanitize_text,
    scrub_identity_attack,
    set_permission,
    status as shield_status,
)
from ..teaching_engine import teach

load_dotenv()
logger = logging.getLogger("atlas")
logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
atlas_router = APIRouter(prefix="/atlas", tags=["ATLAS Core v1"])


# ----- request/response models ---------------------------------------------
class ThinkRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[str] = None


class CouncilRequest(BaseModel):
    question: str
    context: Optional[str] = None
    include_critique: bool = True


class TeachRequest(BaseModel):
    topic: str
    core: Optional[str] = None
    bands: Optional[List[str]] = None
    context: Optional[str] = None


class BlueprintRequest(BaseModel):
    concept: str
    with_plan: bool = True
    synthesizer: str = "hermes"


class PermissionRequest(BaseModel):
    capability: str
    allowed: bool


# ----- helpers -------------------------------------------------------------
def _harden_user_input(text: str) -> str:
    """Apply both shield-level and identity-level scrubs to user text."""
    return scrub_identity_attack(sanitize_text(text))


# ----- system status -------------------------------------------------------
@atlas_router.get("/status")
async def status_endpoint():
    """One-shot health snapshot of all subsystems."""
    return {
        "version": "1.0.0",
        "cores": {
            k: {
                "code_name": c.identity.code_name,
                "name": c.identity.name,
                "domain": c.identity.domain,
                "color": c.identity.voice_color,
            }
            for k, c in CORES.items()
        },
        "shield": shield_status(),
        "identity_anchor": identity_status(),
        "memory": {
            "archive_entries": len(memory.list_archive()),
            "recent_events": len(memory.recent_events(limit=1000)),
        },
        "llm_key_configured": bool(os.environ.get("EMERGENT_LLM_KEY")),
    }


# ----- cores ---------------------------------------------------------------
@atlas_router.post("/cores/{core_key}/think")
async def think(core_key: str, req: ThinkRequest):
    if not is_permitted("write_memory"):
        raise HTTPException(403, "write_memory permission denied")
    try:
        core = get_core(core_key)
    except KeyError as exc:
        raise HTTPException(404, str(exc))

    session = req.session_id or f"hud_{core_key}"
    user_msg = _harden_user_input(req.message)
    if not user_msg.strip():
        raise HTTPException(400, "message is empty after sanitization")

    attack_detected = detect_identity_attack(req.message)
    if attack_detected:
        memory.log_event("identity_attack_blocked", {
            "core": core_key, "session": session, "raw": req.message[:200],
        })

    memory.append_message(session, "user", user_msg)
    try:
        answer = await core.think(user_msg, session_id=session, context=req.context)
    except IdentityDriftError as exc:
        raise HTTPException(503, f"Core refused to respond: {exc}")
    memory.append_message(session, "assistant", answer)
    memory.log_event("think", {"core": core_key, "session": session})
    return {
        "core": core_key,
        "session_id": session,
        "answer": answer,
        "identity_attack_blocked": attack_detected,
    }


@atlas_router.get("/cores/{core_key}/history")
async def history(core_key: str, session_id: Optional[str] = None):
    if core_key not in CORES:
        raise HTTPException(404, "unknown core")
    sid = session_id or f"hud_{core_key}"
    return {"session_id": sid, "messages": memory.get_history(sid)}


# ----- council -------------------------------------------------------------
@atlas_router.post("/council/route")
async def council_route(req: CouncilRequest):
    question = _harden_user_input(req.question)
    if not question.strip():
        raise HTTPException(400, "question is empty after sanitization")
    try:
        result = await assemble(
            question,
            context=req.context,
            include_critique=req.include_critique,
        )
    except IdentityDriftError as exc:
        raise HTTPException(503, f"Council refused to assemble: {exc}")
    memory.log_event("council", {"decision": result["decision"]})
    return result


@atlas_router.post("/council/preview")
async def council_preview(req: CouncilRequest):
    """Cheap version — return just the routing decision without any LLM calls."""
    decision = route(_harden_user_input(req.question))
    return {
        "lead": decision.lead,
        "support": decision.support,
        "critic": decision.critic,
        "rationale": decision.rationale,
        "scores": decision.scores,
    }


# ----- teaching ------------------------------------------------------------
@atlas_router.post("/teach")
async def teaching(req: TeachRequest):
    topic = _harden_user_input(req.topic)
    if not topic.strip():
        raise HTTPException(400, "topic is empty")
    try:
        return await teach(
            topic, core=req.core, bands=req.bands, context=req.context
        )
    except IdentityDriftError as exc:
        raise HTTPException(503, f"Teaching engine refused: {exc}")


# ----- blueprint -----------------------------------------------------------
@atlas_router.post("/blueprint")
async def blueprint(req: BlueprintRequest):
    concept = _harden_user_input(req.concept)
    if not concept.strip():
        raise HTTPException(400, "concept is empty")
    try:
        return await design(
            concept,
            with_plan=req.with_plan,
            synthesizer=req.synthesizer,
        )
    except IdentityDriftError as exc:
        raise HTTPException(503, f"Blueprint engine refused: {exc}")


# ----- archive --------------------------------------------------------------
@atlas_router.post("/archive/upload")
async def archive_upload(file: UploadFile = File(...)):
    if not is_permitted("upload_files"):
        raise HTTPException(403, "upload_files permission denied")
    data = await file.read()
    report = quarantine_upload(file.filename or "", len(data))
    if not report.allowed:
        memory.log_event("quarantine_reject", {
            "filename": file.filename, "reason": report.reason,
        })
        raise HTTPException(400, f"Upload rejected by shield: {report.reason}")

    try:
        entries = await scan_bytes(file.filename, data)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        logger.exception("archive scan failed")
        raise HTTPException(500, f"archive scan failed: {exc}")

    payloads = []
    for entry in entries:
        d = entry_to_dict(entry)
        memory.add_archive_entry(d)
        payloads.append(d)
    memory.log_event("archive_upload", {
        "filename": file.filename, "entries": len(payloads),
    })
    return {"filename": file.filename, "entries": payloads}


@atlas_router.get("/archive/list")
async def archive_list(core: Optional[str] = None):
    return {"entries": memory.list_archive(core=core)}


# ----- shield ---------------------------------------------------------------
@atlas_router.get("/shield/status")
async def shield_status_endpoint():
    return {**shield_status(), "identity_anchor": identity_status()}


@atlas_router.post("/shield/permission")
async def shield_set_permission(req: PermissionRequest):
    set_permission(req.capability, req.allowed)
    memory.log_event("permission_change", {
        "capability": req.capability, "allowed": req.allowed,
    })
    return {
        "capability": req.capability,
        "allowed": req.allowed,
        "all": shield_status()["permissions"],
    }


# ----- events --------------------------------------------------------------
@atlas_router.get("/events")
async def list_events(limit: int = 50):
    return {"events": memory.recent_events(limit=limit)}


# ---------------------------------------------------------------------------
# Standalone app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="ATLAS Core v1",
    description="Modular cognitive backend: 3 cores, council, teaching, blueprint, archive, shield.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(atlas_router)


@app.get("/")
async def root():
    return {"message": "ATLAS Core v1 — alive", "docs": "/docs"}

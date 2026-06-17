"""
Persona Chat REST surface — Phase 8a.

POST   /api/persona/{persona}/chat           → ChatResponse
GET    /api/persona/{persona}/sessions       → list ChatSession
GET    /api/persona/sessions/{session_id}    → {session, messages}
DELETE /api/persona/sessions/{session_id}    → {ok}
GET    /api/persona/list                     → list PersonaInfo

`persona` ∈ {ajani, minerva, hermes, council}. Anything else returns 400.

Note: this endpoint is not role-gated (unlike /api/robot) — the architect
is the only operator and chatting with personas is read-mostly. We may
add an `X-Atlas-Role` gate later for multi-user deployments.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from models.persona_models import (
    ChatRequest, ChatResponse, Persona, PersonaInfo,
)
import services.persona_chat as svc

router = APIRouter(prefix="/api/persona", tags=["Persona"])

_VALID = {"ajani", "minerva", "hermes", "council"}


def _validate(persona: str) -> Persona:
    p = (persona or "").lower()
    if p not in _VALID:
        raise HTTPException(400, f"unknown persona '{persona}'; expected one of {sorted(_VALID)}")
    return p   # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------
@router.get("/list", response_model=List[PersonaInfo])
async def list_personas():
    """Return the persona registry. HUD persona panels use this to render
    chips without hard-coding identity / colour / domain."""
    return svc.list_personas()


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------
@router.post("/{persona}/chat", response_model=ChatResponse)
async def post_chat(persona: str, req: ChatRequest):
    p = _validate(persona)
    try:
        return await svc.chat_any(p, req)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------
@router.get("/{persona}/sessions")
async def list_persona_sessions(persona: str, limit: int = Query(50, ge=1, le=200)):
    p = _validate(persona)
    return {"items": await svc.list_sessions(persona=p, limit=limit)}


@router.get("/sessions")
async def list_all_sessions(limit: int = Query(50, ge=1, le=200)):
    """All sessions across personas, newest first."""
    return {"items": await svc.list_sessions(persona=None, limit=limit)}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    sess = await svc.get_session(session_id)
    if not sess:
        raise HTTPException(404, "session not found")
    msgs = await svc.get_messages(session_id)
    return {"session": sess, "messages": msgs}


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    ok = await svc.delete_session(session_id)
    if not ok:
        raise HTTPException(404, "session not found")
    return {"ok": True, "session_id": session_id}

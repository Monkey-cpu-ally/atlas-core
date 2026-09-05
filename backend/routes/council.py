"""
Council route — topic routing + tri-AI deliberation.

Uses routing.topic_router.route_topic to pick a lead, then either:
  /api/council/route       — returns the routed AI and reasoning
  /api/council/deliberate  — fans out to all three AIs in turn and
                              returns ordered responses, suitable for the
                              COUNCIL HUD tile.
"""
import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from routing.topic_router import AI_DISPLAY, route_topic

logger = logging.getLogger("atlas.council")
router = APIRouter(prefix="/api/council", tags=["Council"])

PERSONA_SYSTEM = {
    "ajani":   ("You are Ajani, Zulu warrior-engineer. Speak in 2-3 short paragraphs. "
                "Focus on physics, energy flow, and what can be built. African cadence."),
    "minerva": ("You are Minerva, Yoruba wisdom keeper. Speak in 2-3 short paragraphs. "
                "Focus on living systems, ethics, who is affected. Use a proverb naturally."),
    "hermes":  ("You are Hermes, Maasai pattern hunter. Speak in 2-3 short paragraphs. "
                "Focus on patterns, edge cases, what the data says. Precise, occasionally witty."),
}


class RouteRequest(BaseModel):
    topic: str


class DeliberateRequest(BaseModel):
    topic: str
    order: Optional[List[str]] = None


@router.post("/route")
async def route(req: RouteRequest):
    ai_id, kw = route_topic(req.topic)
    return {
        "topic": req.topic,
        "routed_to": ai_id,
        "matched_keyword": kw,
        "display": AI_DISPLAY[ai_id],
        "is_council": ai_id == "council",
    }


async def _ask(persona: str, topic: str) -> str:
    """Ask one persona through the canonical multi-provider LLM layer."""
    from services.llm_provider import send as llm_send

    result = await llm_send(
        persona,
        PERSONA_SYSTEM[persona],
        f"Topic: {topic}\n\nWeigh in.",
        session_id=f"council-{persona}-{uuid4().hex[:12]}",
    )
    text = result.get("text")
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError(f"empty LLM response for {persona}")
    return text


@router.post("/deliberate")
async def deliberate(req: DeliberateRequest):
    """All requested AIs answer through the canonical provider.

    Provider availability is decided by services.llm_provider rather than by
    this route. This keeps local providers and the explicit CI-only provider
    usable without pretending EMERGENT_LLM_KEY is configured.
    """
    if not req.topic.strip():
        raise HTTPException(400, "topic is required")

    order = req.order or ["ajani", "minerva", "hermes"]
    order = [a.lower() for a in order if a.lower() in PERSONA_SYSTEM]
    if not order:
        raise HTTPException(400, "no valid AI in `order`")

    lead, kw = route_topic(req.topic)
    voices = []
    for persona in order:
        try:
            text = await _ask(persona, req.topic)
        except Exception as exc:
            logger.warning("Council deliberation failed for %s: %s", persona, exc)
            raise HTTPException(503, f"AI services unavailable for {persona}") from exc
        voices.append({
            "persona": persona,
            "display": AI_DISPLAY[persona],
            "text": text,
            "is_lead": persona == lead,
        })

    try:
        from services import memory_bank as _mb
        deliberation_body = (
            f"COUNCIL · {req.topic}\n\n"
            + "\n\n".join(f"[{v['persona'].upper()}] {v['text']}" for v in voices)
        )
        await _mb.auto_store(
            deliberation_body,
            persona=lead if lead and lead != "council" else "council",
            category="council",
            source_type="council",
            tags=[req.topic],
        )
    except Exception as exc:
        logger.warning("Council memory store failed: %s", exc)

    return {
        "topic": req.topic,
        "lead": lead if lead != "council" else None,
        "matched_keyword": kw,
        "voices": voices,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

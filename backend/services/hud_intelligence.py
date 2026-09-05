"""Feature-gated HUD Intelligence V1 coordinator."""
from __future__ import annotations

import os
from typing import Any, Dict, Optional
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from models.hud_intelligence_models import (
    HudConfidence, HudError, HudEvidence, HudIntelligenceRequest,
    HudIntelligenceResponse, HudMemoryResult, HudProviderAudit,
)
from models.persona_models import ChatRequest
import services.persona_chat as persona_chat

_client: Optional[AsyncIOMotorClient] = None


def feature_enabled() -> bool:
    return os.getenv("ATLAS_HUD_INTELLIGENCE_V1", "false").strip().lower() in {
        "1", "true", "yes", "on",
    }


def _runs():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    return _client[os.environ["DB_NAME"]]["hud_intelligence_runs_v1"]


async def ensure_indexes() -> None:
    await _runs().create_index("request_id", unique=True)
    await _runs().create_index("run_id", unique=True)


def _public_document(response: HudIntelligenceResponse) -> Dict[str, Any]:
    return response.model_dump(mode="json")


async def _cached(request_id: str) -> Optional[HudIntelligenceResponse]:
    row = await _runs().find_one({"request_id": request_id}, {"_id": 0, "response": 1})
    if row and row.get("response"):
        return HudIntelligenceResponse(**row["response"])
    return None


async def _finish(response: HudIntelligenceResponse) -> None:
    await _runs().update_one(
        {"request_id": response.request_id},
        {
            "$set": {"status": response.status, "response": _public_document(response)},
            "$push": {"events": {"status": response.status}},
        },
    )


async def execute(req: HudIntelligenceRequest) -> HudIntelligenceResponse:
    cached = await _cached(req.request_id)
    retrying = bool(
        cached and cached.status == "failed" and cached.error and cached.error.retryable
    )
    if cached and not retrying:
        return cached

    run_id = cached.run_id if retrying and cached else uuid4().hex
    queued = HudIntelligenceResponse(
        request_id=req.request_id, run_id=run_id, status="queued",
        persona=req.persona, learning_level=req.learning_level,
    )
    if retrying:
        await _runs().update_one(
            {"request_id": req.request_id},
            {"$set": {"status": "queued", "response": _public_document(queued)},
             "$push": {"events": {"status": "queued", "detail": "retry"}}},
        )
    else:
        try:
            await _runs().insert_one({
                "request_id": req.request_id, "run_id": run_id, "status": "queued",
                "persona": req.persona, "intent": req.intent,
                "surface": req.client_context.surface,
                "learning_level": req.learning_level,
                "events": [{"status": "queued"}], "response": _public_document(queued),
            })
        except DuplicateKeyError:
            replay = await _cached(req.request_id)
            if replay:
                return replay
            raise

    if req.intent in {"teach", "explain_resource"}:
        response = queued.model_copy(update={
            "status": "partial",
            "error": HudError(
                code="intent_not_migrated",
                message="This learning surface has not migrated to HUD Intelligence V1 yet.",
                retryable=False,
            ),
        })
    else:
        try:
            chat = await persona_chat.chat_any(req.persona, ChatRequest(
                message=req.message, session_id=req.session_id, project_id=req.project_id,
            ))
        except Exception:
            response = queued.model_copy(update={
                "status": "failed",
                "error": HudError(
                    code="persona_service_unavailable",
                    message="The selected ATLAS intelligence service is temporarily unavailable.",
                    retryable=True,
                ),
            })
            await _finish(response)
            return response
        evidence = [
            HudEvidence(record_id=value, kind="memory", title="Persona memory")
            for value in chat.cited_memory_ids
        ] + [
            HudEvidence(record_id=value, kind="knowledge", title="Knowledge record")
            for value in chat.cited_knowledge_ids
        ]
        if chat.cited_knowledge_ids and chat.cited_memory_ids:
            confidence = HudConfidence(
                label="medium", basis=["persona memory and shared knowledge were retrieved"]
            )
        elif evidence:
            confidence = HudConfidence(
                label="low", basis=["only one grounded context type was retrieved"]
            )
        else:
            confidence = HudConfidence(
                label="unknown", basis=["no grounded records were returned"]
            )
        response = HudIntelligenceResponse(
            request_id=req.request_id, run_id=run_id, status="complete",
            session_id=chat.session_id, message_id=chat.message_id,
            persona=req.persona, learning_level=req.learning_level,
            answer=chat.reply, council_voices=chat.council_voices,
            evidence=evidence, confidence=confidence,
            retrieval_mode="hashed_fallback" if chat.cited_memory_ids else (
                "lexical" if chat.cited_knowledge_ids else "none"
            ),
            memory=HudMemoryResult(turn_saved=True),
            provider=HudProviderAudit(
                name=chat.provider_used, model=chat.model_used,
                fallback_reason=chat.fallback_reason,
            ),
        )
    await _finish(response)
    return response


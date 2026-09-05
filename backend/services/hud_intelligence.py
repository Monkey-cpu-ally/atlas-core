"""Feature-gated HUD Intelligence V1 coordinator."""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

from atlas_core.teaching_engine.contract import teaching_contract
from models.hud_intelligence_models import (
    HudConfidence, HudError, HudEvidence, HudIntelligenceRequest,
    HudIntelligenceResponse, HudMemoryResult, HudNextStep, HudProviderAudit,
)
from models.persona_models import ChatRequest
from services.existing_resource_library import get_resource
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


def _resource_rows(resource_ids: List[str]) -> tuple[List[Dict[str, Any]], List[str]]:
    rows: List[Dict[str, Any]] = []
    missing: List[str] = []
    for resource_id in resource_ids:
        row = get_resource(resource_id)
        if row:
            rows.append(row)
        else:
            missing.append(resource_id)
    return rows, missing


def _resource_evidence(rows: List[Dict[str, Any]]) -> List[HudEvidence]:
    return [
        HudEvidence(
            record_id=str(row.get("id", "")),
            kind="resource",
            title=str(row.get("title") or row.get("id") or "Knowledge resource"),
            verification_status="verified" if row.get("verified") is True else "provisional",
            source_url=row.get("url") or row.get("source_url"),
        )
        for row in rows
    ]


def _message_for_intent(req: HudIntelligenceRequest, resources: List[Dict[str, Any]]) -> str:
    if req.intent == "teach":
        return (
            f"{teaching_contract(req.learning_level, req.persona)}\n\n"
            "Teach the user's request using the existing grounded persona memory and Knowledge Bank. "
            "Do not claim evidence that was not retrieved.\n\n"
            f"USER REQUEST:\n{req.message}"
        )
    if req.intent == "explain_resource":
        catalog_lines = []
        for row in resources:
            catalog_lines.append(
                " | ".join(filter(None, [
                    f"id={row.get('id')}",
                    f"title={row.get('title')}",
                    f"provider={row.get('provider')}",
                    f"type={row.get('resource_type')}",
                    f"subjects={','.join(row.get('subjects', []))}",
                    f"url={row.get('url') or row.get('source_url') or ''}",
                ]))
            )
        catalog = "\n".join(catalog_lines)
        return (
            "Explain the selected Knowledge Bank catalog resource(s) for the user. "
            "The catalog metadata below proves the resources exist, but it does NOT prove that full resource text was ingested. "
            "Use normal grounded persona memory/Knowledge Bank retrieval for substantive claims, and clearly distinguish catalog metadata from retrieved knowledge.\n\n"
            f"CATALOG METADATA:\n{catalog}\n\nUSER REQUEST:\n{req.message}"
        )
    return req.message


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

    resources, missing_resource_ids = _resource_rows(req.resource_ids)
    if req.intent == "explain_resource" and not req.resource_ids:
        response = queued.model_copy(update={
            "status": "partial",
            "error": HudError(
                code="resource_required",
                message="explain_resource requires at least one Knowledge Bank resource_id.",
                retryable=False,
            ),
        })
        await _finish(response)
        return response
    if missing_resource_ids:
        response = queued.model_copy(update={
            "status": "partial",
            "evidence": _resource_evidence(resources),
            "error": HudError(
                code="resource_not_found",
                message="One or more requested Knowledge Bank resources were not found: "
                        + ", ".join(missing_resource_ids),
                retryable=False,
            ),
        })
        await _finish(response)
        return response

    try:
        chat = await persona_chat.chat_any(req.persona, ChatRequest(
            message=_message_for_intent(req, resources),
            session_id=req.session_id,
            project_id=req.project_id,
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

    evidence = _resource_evidence(resources) + [
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
    elif chat.cited_knowledge_ids or chat.cited_memory_ids:
        confidence = HudConfidence(
            label="low", basis=["only one grounded context type was retrieved"]
        )
    elif resources:
        confidence = HudConfidence(
            label="low", basis=["resource catalog metadata was verified, but no grounded knowledge record was returned"]
        )
    else:
        confidence = HudConfidence(
            label="unknown", basis=["no grounded records were returned"]
        )

    retrieval_mode = "hashed_fallback" if chat.cited_memory_ids else (
        "lexical" if chat.cited_knowledge_ids or resources else "none"
    )
    next_step = None
    if req.intent == "teach":
        next_step = HudNextStep(
            label="Continue this lesson", intent="teach", requires_confirmation=True,
        )
    elif req.intent == "explain_resource":
        next_step = HudNextStep(
            label="Teach me from this resource", intent="teach", requires_confirmation=True,
        )

    response = HudIntelligenceResponse(
        request_id=req.request_id, run_id=run_id, status="complete",
        session_id=chat.session_id, message_id=chat.message_id,
        persona=req.persona, learning_level=req.learning_level,
        answer=chat.reply, council_voices=chat.council_voices,
        evidence=evidence, confidence=confidence,
        retrieval_mode=retrieval_mode,
        memory=HudMemoryResult(turn_saved=True),
        next_step=next_step,
        provider=HudProviderAudit(
            name=chat.provider_used, model=chat.model_used,
            fallback_reason=chat.fallback_reason,
        ),
    )
    await _finish(response)
    return response

"""Legacy chat compatibility routes.

`/api/chat` is retained for existing HUD/clients, but all persona execution,
memory retrieval, knowledge grounding, LLM selection, and persistence now flow
through the canonical `services.persona_chat` runtime.
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models.persona_models import ChatRequest as PersonaChatRequest
import services.persona_chat as persona_chat

router = APIRouter(prefix="/api/chat", tags=["Chat"])

_VALID_PERSONAS = {"ajani", "minerva", "hermes", "council"}


class ChatRequest(BaseModel):
    persona: str = "ajani"
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    persona: str
    response: str
    conversation_id: str
    timestamp: str


def _persona(value: str) -> str:
    persona = (value or "ajani").lower()
    # Historical clients used "trinity" for the three-persona council.
    if persona == "trinity":
        persona = "council"
    if persona not in _VALID_PERSONAS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown persona: {value}. Available: {sorted(_VALID_PERSONAS)}",
        )
    return persona


def _legacy_response(result) -> ChatResponse:
    return ChatResponse(
        persona=result.persona,
        response=result.reply,
        conversation_id=result.session_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.post("/send", response_model=ChatResponse)
async def send_message(req: ChatRequest):
    """Compatibility facade over the canonical persona chat pipeline."""
    persona = _persona(req.persona)
    try:
        result = await persona_chat.chat_any(
            persona,
            PersonaChatRequest(message=req.message, session_id=req.conversation_id),
        )
        return _legacy_response(result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        # Preserve truthful failure semantics; never fabricate a persona reply.
        raise HTTPException(status_code=503, detail=f"Canonical persona runtime unavailable: {exc}") from exc


@router.get("/conversations")
async def list_conversations(persona: Optional[str] = None, limit: int = 20):
    """Expose canonical persona sessions through the legacy envelope."""
    selected = _persona(persona) if persona else None
    sessions = await persona_chat.list_sessions(persona=selected, limit=limit)
    return {
        "conversations": [
            {
                "conversation_id": session.get("id"),
                "persona": session.get("persona"),
                "created_at": session.get("created_at"),
                "updated_at": session.get("updated_at"),
                "message_count": session.get("message_count", 0),
                "title": session.get("title"),
                "project_id": session.get("project_id"),
            }
            for session in sessions
        ]
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    session = await persona_chat.get_session(conversation_id)
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = await persona_chat.get_messages(conversation_id)
    return {
        "conversation": {
            "conversation_id": session.get("id"),
            "persona": session.get("persona"),
            "created_at": session.get("created_at"),
            "updated_at": session.get("updated_at"),
            "message_count": session.get("message_count", 0),
            "title": session.get("title"),
            "project_id": session.get("project_id"),
        },
        "messages": [
            {
                "conversation_id": message.get("session_id"),
                "role": message.get("role"),
                "content": message.get("content"),
                "persona": message.get("persona"),
                "timestamp": message.get("created_at"),
                "message_id": message.get("id"),
                "cited_memory_ids": message.get("cited_memory_ids", []),
                "cited_knowledge_ids": message.get("cited_knowledge_ids", []),
                "provider_used": message.get("provider_used"),
                "model_used": message.get("model_used"),
            }
            for message in messages
        ],
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    if not await persona_chat.delete_session(conversation_id):
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"success": True, "deleted": conversation_id}


@router.post("/trinity")
async def trinity_counsel(question: str):
    """Legacy Trinity endpoint mapped to the canonical ATLAS Council."""
    try:
        result = await persona_chat.chat_any(
            "council",
            PersonaChatRequest(message=question),
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Canonical council runtime unavailable: {exc}") from exc
    return {
        "question": question,
        "discussion": result.reply,
        "conversation_id": result.session_id,
        "council_voices": [voice.model_dump() for voice in result.council_voices],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

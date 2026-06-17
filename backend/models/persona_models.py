"""
Persona Chat — data models (Phase 8a).

A persona chat session is a multi-turn conversation with one of the four
ATLAS personas (ajani · minerva · hermes · council). Each turn is grounded
in:
  - the persona's tagged Memory Bank entries (long-term),
  - the most-relevant Knowledge Bank records (research/citations),
  - prior turns in this session (short-term).

Persisted in two collections:
  * `persona_sessions` — header per conversation
  * `persona_messages` — append-only per turn

This is the foundation the HUD persona panels + voice integration will sit
on top of. The chat surface deliberately mirrors the OpenAI/Anthropic
message shape so we can swap providers via `llm_provider.send()` with no
schema friction.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

# Canonical persona slugs. Trinity is reserved for a future merged persona.
Persona = Literal["ajani", "minerva", "hermes", "council"]

# Roles in the chat history. 'system' is internal (assembled per-turn from
# the persona's voice + grounded memory) and is NOT persisted as a message —
# we only persist what the human said and what the persona said.
ChatRole = Literal["user", "assistant"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return uuid4().hex


# ---------------------------------------------------------------------------
# Persisted documents
# ---------------------------------------------------------------------------
class ChatMessage(BaseModel):
    id: str = Field(default_factory=_uuid)
    session_id: str
    persona: Persona
    role: ChatRole
    content: str
    # Audit: which memories / knowledge records the assistant grounded itself in
    cited_memory_ids: List[str] = Field(default_factory=list)
    cited_knowledge_ids: List[str] = Field(default_factory=list)
    # Provider audit (filled only on assistant messages)
    provider_used: Optional[str] = None
    model_used: Optional[str] = None
    fallback_reason: Optional[str] = None
    # Optional FK into memory_bank if the assistant turn was written there
    memory_bank_id: Optional[str] = None
    created_at: str = Field(default_factory=_now)


class ChatSession(BaseModel):
    id: str = Field(default_factory=_uuid)
    persona: Persona
    title: str                          # auto-derived from the first user turn
    project_id: Optional[str] = None    # if set, persona pulls project memories
    created_at: str = Field(default_factory=_now)
    updated_at: str = Field(default_factory=_now)
    message_count: int = 0


# ---------------------------------------------------------------------------
# Request / response envelopes (REST surface)
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    session_id: Optional[str] = None
    project_id: Optional[str] = None
    # Defaults are tuned for the architect's typical use (3 most-relevant
    # memories + 3 most-relevant knowledge records). Bumping these increases
    # context cost (and token spend) linearly.
    memory_top_k: int = Field(default=3, ge=0, le=10)
    knowledge_top_k: int = Field(default=3, ge=0, le=10)
    # If set, override the persona's default LLM model for this turn only.
    model_override: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    persona: Persona
    reply: str
    # Mirrors of the persisted message (so the HUD doesn't need a second round-trip)
    message_id: str
    cited_memory_ids: List[str]
    cited_knowledge_ids: List[str]
    provider_used: Optional[str]
    model_used: Optional[str]
    fallback_reason: Optional[str]
    # For council chat, the per-persona sub-voices fold in here so the HUD
    # can display them as expandable rows. Empty for single-persona chats.
    council_voices: List["CouncilSubVoice"] = Field(default_factory=list)


class CouncilSubVoice(BaseModel):
    persona: Persona
    text: str
    provider_used: Optional[str] = None
    model_used: Optional[str] = None


class PersonaInfo(BaseModel):
    """Returned by `GET /api/persona/list` so the HUD can render persona
    chips without hard-coding their identity / colour / domain."""
    slug: Persona
    name: str
    domain: str
    one_liner: str
    color: str
    voice_prompt: str


# Forward-ref fix for the nested type
ChatResponse.model_rebuild()

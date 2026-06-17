"""
Persona Chat orchestrator — Phase 8a.

Pipeline per turn (single persona):

    1. Session lookup or create
    2. Retrieve persona-tagged Memory Bank entries (cosine similarity to msg)
    3. Retrieve relevant Knowledge Bank records (regex search by msg)
    4. Pull last N messages of this session for short-term context
    5. Build the system prompt = persona_voice + grounded context
    6. llm_provider.send(persona, system, user)
    7. Persist user turn + assistant turn into persona_messages
    8. Mirror assistant turn into Memory Bank (category=agent, persona=<persona>)
       so future turns can recall this conversation.

Council chat:
    Runs steps 1-4, then 5-6 in PARALLEL for ajani/minerva/hermes,
    then a final synthesis call with persona='council' that sees all
    three sub-voices. Each sub-voice is returned to the caller for HUD
    display and stored in Memory Bank as category=council/permanent.

Persistence:
    * persona_sessions     — one doc per conversation (title, project_id, counts)
    * persona_messages     — append-only per turn (user + assistant)
    * memory_bank          — assistant turns mirrored here for future recall

This module owns NO routes. The HTTP surface is `routes/persona.py`.
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from motor.motor_asyncio import AsyncIOMotorClient

import services.llm_provider as llmp
import services.memory_bank as mb
import services.knowledge_ingestion as kbase
from models.persona_models import (
    ChatMessage, ChatRequest, ChatResponse, ChatSession,
    CouncilSubVoice, Persona, PersonaInfo, _now,
)

logger = logging.getLogger("atlas.persona_chat")

# ---------------------------------------------------------------------------
# Persona registry — single source of truth for voice + colour + domain.
# Shared with `knowledge_distiller.py` (text identical) so the same Ajani
# distilling a paper "sounds" like the Ajani you're chatting with.
# ---------------------------------------------------------------------------
PERSONAS: Dict[Persona, PersonaInfo] = {
    "ajani":   PersonaInfo(
        slug="ajani",
        name="Ajani",
        domain="Engineering · Robotics · Manufacturing",
        one_liner="Zulu warrior-engineer. Builds and tests. Loves what fails.",
        color="#E89B5F",
        voice_prompt=(
            "You are Ajani, Zulu warrior-engineer. You think in mechanisms, "
            "tolerances, supply chains, and failure modes. When the architect "
            "asks you something, anchor your answer in WHAT CAN BE BUILT and "
            "WHAT WILL FAIL. You speak with calm confidence, you avoid jargon "
            "unless precision demands it, and you never fake certainty."
        ),
    ),
    "minerva": PersonaInfo(
        slug="minerva",
        name="Minerva",
        domain="Science · Biology · Chemistry · Research",
        one_liner="Greek scholar of nature. Tests what is TRUE and REPRODUCIBLE.",
        color="#9CD3FF",
        voice_prompt=(
            "You are Minerva, Greek goddess of wisdom and science. You think "
            "in principles, evidence quality, and consequences. When the "
            "architect asks you something, anchor your answer in WHAT IS TRUE, "
            "WHAT IS REPRODUCIBLE, and WHAT THE EVIDENCE ACTUALLY SHOWS. "
            "Cite sources when they appear in your grounded context. Flag "
            "low-confidence claims explicitly."
        ),
    ),
    "hermes":  PersonaInfo(
        slug="hermes",
        name="Hermes",
        domain="Logic · Math · Optimisation · Software · Validation",
        one_liner="Maasai pattern hunter. Finds contradictions, optimises trade-offs.",
        color="#B388FF",
        voice_prompt=(
            "You are Hermes, Maasai pattern hunter and messenger of clarity. "
            "You think in patterns, contradictions, invariants and trade-offs. "
            "When the architect asks you something, anchor your answer in "
            "WHAT IS LOGICAL, WHAT IS OPTIMAL, and WHAT BREAKS UNDER STRESS. "
            "Be short. Be sharp. Surface assumptions explicitly."
        ),
    ),
    "council": PersonaInfo(
        slug="council",
        name="Council",
        domain="Cross-disciplinary synthesis",
        one_liner="Atlas Council: Ajani + Minerva + Hermes together.",
        color="#F4EFE4",
        voice_prompt=(
            "You are the ATLAS Council. You receive separate voices from "
            "Ajani (engineering), Minerva (science) and Hermes (logic), and "
            "you synthesise them into ONE answer for the architect. Weight "
            "the voices by relevance to the question. If they disagree, say "
            "so plainly and explain why. Never paper over a contradiction. "
            "Keep the synthesis tight — the architect does not need a "
            "meeting summary, they need a decision."
        ),
    ),
}


# ---------------------------------------------------------------------------
# Mongo handles (lazy, env-only — fail fast if MONGO_URL is missing)
# ---------------------------------------------------------------------------
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    return _client[os.environ['DB_NAME']]


def _sessions():
    return _db()["persona_sessions"]


def _messages():
    return _db()["persona_messages"]


# ---------------------------------------------------------------------------
# Context retrieval — the "grounded" part of the prompt
# ---------------------------------------------------------------------------
async def _fetch_persona_memories(persona: Persona, query: str, top_k: int) -> List[Dict[str, Any]]:
    """Pull this persona's most relevant Memory Bank entries.

    Uses cosine similarity via `memory_bank.search_memory`. We deliberately
    omit a category filter so the persona pulls from BOTH long-term lessons
    (category=agent) AND recent chat turns mirrored back (category=agent).
    """
    if top_k <= 0:
        return []
    try:
        rows = await mb.search_memory(query, persona=persona, top_k=top_k, min_score=0.10)
    except Exception as exc:    # noqa: BLE001
        logger.warning("memory search failed for persona=%s: %s", persona, exc)
        return []
    return rows


_STOPWORDS = {
    "the", "and", "for", "with", "what", "when", "where", "why", "how",
    "this", "that", "these", "those", "are", "was", "were", "have", "has",
    "had", "do", "does", "did", "can", "could", "should", "would", "you",
    "your", "yours", "we", "they", "them", "our", "their", "but", "not",
    "tell", "give", "say", "ask", "please", "briefly", "summarise",
    "summarize", "explain", "about", "into", "from", "than", "then",
    "very", "just", "really", "kind", "of", "in", "on", "at", "to", "by",
    "or", "as", "is", "be", "it", "an", "a", "i", "me", "my", "mine",
}


def _keywords(text: str, max_tokens: int = 6) -> List[str]:
    """Pull the few distinctive tokens out of a natural-language prompt.
    Used to query the Knowledge Bank (whose search is a regex substring,
    not a real text index — so a multi-sentence prompt would otherwise
    match nothing). Lowercased, stop-words dropped, length ≥ 4."""
    import re as _re
    raw = _re.findall(r"[A-Za-z][A-Za-z0-9_\-]{3,}", text or "")
    seen: set[str] = set()
    out: List[str] = []
    for tok in raw:
        low = tok.lower()
        if low in _STOPWORDS or low in seen:
            continue
        seen.add(low)
        out.append(low)
        if len(out) >= max_tokens:
            break
    return out


async def _fetch_knowledge(query: str, persona: Persona, top_k: int) -> List[Dict[str, Any]]:
    """Pull the most relevant Knowledge Bank records.

    Knowledge Bank uses a regex/text index — fast but coarse. We bias toward
    records this persona is tagged on (`related_agents` contains the persona)
    and fall back to a global search when the per-persona slice is empty.

    The user's natural-language message is tokenised first; we run one
    kbase.search per top keyword and merge results (dedup-by-id, preserving
    persona-filtered hits first). Without this, a multi-sentence prompt
    would never match an ingested record.
    """
    if top_k <= 0:
        return []
    tokens = _keywords(query) or [query.strip()[:40]]
    seen: set[str] = set()
    merged: List[Dict[str, Any]] = []
    try:
        # Two passes: persona-filtered first, then global fallback if empty.
        for use_persona_filter in (True, False):
            if merged and use_persona_filter is False:
                break  # already have hits — skip global pass
            for tok in tokens:
                rows = await kbase.search(
                    q=tok,
                    agent=persona if use_persona_filter else None,
                    limit=top_k,
                )
                for r in rows:
                    rid = r.get("id")
                    if rid and rid not in seen:
                        seen.add(rid)
                        merged.append(r)
                        if len(merged) >= top_k:
                            return merged
        return merged
    except Exception as exc:    # noqa: BLE001
        logger.warning("knowledge search failed for persona=%s: %s", persona, exc)
        return merged


async def _recent_turns(session_id: str, limit: int = 6) -> List[Dict[str, Any]]:
    """Last N messages, oldest-first. limit ≤ 6 keeps context cheap."""
    cur = _messages().find({"session_id": session_id}, {"_id": 0}) \
        .sort("created_at", -1).limit(limit)
    rows = [r async for r in cur]
    return list(reversed(rows))


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------
def _format_memories(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "  (none yet — this is the first relevant insight on this topic.)"
    lines = []
    for r in rows[:5]:
        # search_memory returns the row + `score`. Show snippet only.
        snip = (r.get("content") or "")[:240].strip()
        tags = ", ".join((r.get("tags") or [])[:5])
        score = r.get("score")
        score_s = f" · sim={score:.2f}" if isinstance(score, (int, float)) else ""
        lines.append(f"  • [{tags}]{score_s} {snip}")
    return "\n".join(lines)


def _format_knowledge(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "  (no matching ingested sources yet.)"
    lines = []
    for r in rows[:5]:
        title = (r.get("title") or "untitled")[:120]
        summary = (r.get("summary") or "")[:200]
        url = r.get("source_url") or ""
        lines.append(f"  • {title} — {summary}  [{url}]")
    return "\n".join(lines)


def _format_history(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return ""
    lines = ["\nRECENT CONVERSATION (oldest first):"]
    for r in rows:
        speaker = "ARCHITECT" if r["role"] == "user" else r["persona"].upper()
        lines.append(f"  {speaker}: {(r.get('content') or '')[:600]}")
    return "\n".join(lines)


def _build_system(persona: Persona, memories: List[Dict[str, Any]],
                  knowledge: List[Dict[str, Any]], history: List[Dict[str, Any]]) -> str:
    info = PERSONAS[persona]
    return (
        f"{info.voice_prompt}\n\n"
        "You have access to two grounded sources of context. Use them when "
        "they are relevant; do NOT mention this context block — just speak "
        "naturally as the persona.\n\n"
        f"YOUR DOMAIN MEMORIES (most relevant first):\n{_format_memories(memories)}\n\n"
        f"INGESTED KNOWLEDGE (most relevant first):\n{_format_knowledge(knowledge)}\n"
        f"{_format_history(history)}\n\n"
        "Now answer the architect's next message. Stay in voice."
    )


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------
async def _get_or_create_session(
    persona: Persona, session_id: Optional[str], project_id: Optional[str],
    seed_message: str,
) -> ChatSession:
    if session_id:
        doc = await _sessions().find_one({"id": session_id}, {"_id": 0})
        if doc:
            return ChatSession(**doc)
    # New session — derive a title from the first user message (max 80 chars)
    title = (seed_message or "untitled").strip().splitlines()[0][:80]
    sess = ChatSession(persona=persona, title=title, project_id=project_id)
    await _sessions().insert_one(sess.model_dump())
    return sess


async def _touch_session(session_id: str, *, add_messages: int) -> None:
    await _sessions().update_one(
        {"id": session_id},
        {"$set": {"updated_at": _now()}, "$inc": {"message_count": add_messages}},
    )


# ---------------------------------------------------------------------------
# Single-persona chat
# ---------------------------------------------------------------------------
async def chat(persona: Persona, req: ChatRequest) -> ChatResponse:
    persona = persona.lower()    # type: ignore[assignment]
    if persona not in PERSONAS:
        raise ValueError(f"unknown persona: {persona!r}")

    # 1. Session
    session = await _get_or_create_session(persona, req.session_id, req.project_id, req.message)

    # 2-4. Context (parallel)
    memories_t = asyncio.create_task(
        _fetch_persona_memories(persona, req.message, req.memory_top_k)
    )
    knowledge_t = asyncio.create_task(
        _fetch_knowledge(req.message, persona, req.knowledge_top_k)
    )
    history_t = asyncio.create_task(_recent_turns(session.id, limit=6))
    memories, knowledge, history = await asyncio.gather(memories_t, knowledge_t, history_t)

    # 5. Persist USER turn first so even an LLM failure leaves a record.
    user_msg = ChatMessage(
        session_id=session.id, persona=persona, role="user", content=req.message,
    )
    await _messages().insert_one(user_msg.model_dump())

    # 6. LLM call
    system = _build_system(persona, memories, knowledge, history)
    try:
        res = await llmp.send(
            persona, system, req.message,
            session_id=session.id,
            model_override=req.model_override,
        )
    except Exception as exc:    # noqa: BLE001
        logger.exception("persona chat LLM call failed: %s", exc)
        # Persist a placeholder assistant turn so the UI can show the error.
        err_msg = ChatMessage(
            session_id=session.id, persona=persona, role="assistant",
            content=f"(LLM error: {exc})",
        )
        await _messages().insert_one(err_msg.model_dump())
        await _touch_session(session.id, add_messages=2)
        return ChatResponse(
            session_id=session.id, persona=persona,
            reply=err_msg.content, message_id=err_msg.id,
            cited_memory_ids=[], cited_knowledge_ids=[],
            provider_used=None, model_used=None, fallback_reason="llm_error",
        )

    reply = (res.get("text") or "").strip()
    cited_mem = [m.get("id") for m in memories if m.get("id")]
    cited_kbase = [k.get("id") for k in knowledge if k.get("id")]

    # 7. Persist ASSISTANT turn
    asst_msg = ChatMessage(
        session_id=session.id, persona=persona, role="assistant",
        content=reply,
        cited_memory_ids=cited_mem,
        cited_knowledge_ids=cited_kbase,
        provider_used=res.get("provider_used"),
        model_used=res.get("model_used"),
        fallback_reason=res.get("fallback_reason"),
    )

    # 8. Mirror assistant turn into Memory Bank (so the persona can recall its
    #    own past replies on this topic). Category=agent → PERMANENT.
    mem = await mb.auto_store(
        f"[{persona} chat reply]\nQ: {req.message[:400]}\nA: {reply[:800]}",
        persona=persona, category="agent",
        source_type="persona_chat", source_id=asst_msg.id,
        tags=["persona_chat", persona, session.id],
    )
    if mem:
        asst_msg.memory_bank_id = mem.get("id")

    await _messages().insert_one(asst_msg.model_dump())
    await _touch_session(session.id, add_messages=2)

    return ChatResponse(
        session_id=session.id, persona=persona,
        reply=reply, message_id=asst_msg.id,
        cited_memory_ids=cited_mem, cited_knowledge_ids=cited_kbase,
        provider_used=res.get("provider_used"),
        model_used=res.get("model_used"),
        fallback_reason=res.get("fallback_reason"),
    )


# ---------------------------------------------------------------------------
# Council chat — fan-out + synthesis
# ---------------------------------------------------------------------------
async def _one_voice(persona: Persona, message: str, memories: List[Dict[str, Any]],
                     knowledge: List[Dict[str, Any]]) -> Tuple[Persona, Dict[str, Any]]:
    """One sub-voice for the council. Skips persistence — the council
    response is the persisted artefact; sub-voices are mirrored into
    Memory Bank as category=council/permanent for audit."""
    system = _build_system(persona, memories, knowledge, history=[])
    try:
        res = await llmp.send(
            persona, system, message,
            session_id=f"council-sub-{persona}",
        )
        return persona, res
    except Exception as exc:    # noqa: BLE001
        logger.warning("council sub-voice %s failed: %s", persona, exc)
        return persona, {"text": f"(no response — {exc})", "provider_used": None, "model_used": None}


async def _council_chat(req: ChatRequest) -> ChatResponse:
    session = await _get_or_create_session("council", req.session_id, req.project_id, req.message)

    # All three personas pull THEIR memories in parallel.
    contexts = await asyncio.gather(
        _fetch_persona_memories("ajani",   req.message, req.memory_top_k),
        _fetch_persona_memories("minerva", req.message, req.memory_top_k),
        _fetch_persona_memories("hermes",  req.message, req.memory_top_k),
        _fetch_knowledge(req.message, "council", req.knowledge_top_k),
    )
    ajani_mem, minerva_mem, hermes_mem, kbase_rows = contexts

    # Persist USER turn now (in case anything below fails)
    user_msg = ChatMessage(
        session_id=session.id, persona="council", role="user", content=req.message,
    )
    await _messages().insert_one(user_msg.model_dump())

    # Three sub-voices in parallel
    sub_results = await asyncio.gather(
        _one_voice("ajani",   req.message, ajani_mem,   kbase_rows),
        _one_voice("minerva", req.message, minerva_mem, kbase_rows),
        _one_voice("hermes",  req.message, hermes_mem,  kbase_rows),
    )
    sub_voices: List[CouncilSubVoice] = []
    fold_lines = []
    for persona_slug, res in sub_results:
        text = (res.get("text") or "").strip()
        sub_voices.append(CouncilSubVoice(
            persona=persona_slug,
            text=text,
            provider_used=res.get("provider_used"),
            model_used=res.get("model_used"),
        ))
        fold_lines.append(f"--- {persona_slug.upper()} ---\n{text}")

    # Council synthesis prompt: includes the three sub-voices verbatim
    council_system = (
        PERSONAS["council"].voice_prompt + "\n\n"
        "You will now read three voices on the architect's question and "
        "synthesise ONE final answer.\n\n"
        + "\n\n".join(fold_lines) + "\n\n"
        "Architect's question follows. Give the final synthesis."
    )
    try:
        synth = await llmp.send(
            "council", council_system, req.message,
            session_id=session.id,
        )
        reply = (synth.get("text") or "").strip()
        provider_used = synth.get("provider_used")
        model_used = synth.get("model_used")
        fallback_reason = synth.get("fallback_reason")
    except Exception as exc:    # noqa: BLE001
        logger.exception("council synthesis failed: %s", exc)
        reply = "\n\n".join(f"{v.persona.upper()}: {v.text}" for v in sub_voices)
        provider_used = None
        model_used = None
        fallback_reason = "council_synth_failed"

    cited_mem = [m.get("id") for m in (ajani_mem + minerva_mem + hermes_mem) if m.get("id")]
    cited_kbase = [k.get("id") for k in kbase_rows if k.get("id")]

    asst_msg = ChatMessage(
        session_id=session.id, persona="council", role="assistant",
        content=reply,
        cited_memory_ids=cited_mem,
        cited_knowledge_ids=cited_kbase,
        provider_used=provider_used,
        model_used=model_used,
        fallback_reason=fallback_reason,
    )

    # Mirror the council synthesis into council/permanent memory. Each
    # sub-voice gets its own agent-tagged memory so individual persona
    # chats can recall it later.
    council_mem = await mb.auto_store(
        f"[council chat]\nQ: {req.message[:400]}\nA: {reply[:800]}",
        persona="council", category="council",
        source_type="persona_chat", source_id=asst_msg.id,
        tags=["persona_chat", "council", session.id],
    )
    if council_mem:
        asst_msg.memory_bank_id = council_mem.get("id")
    for v in sub_voices:
        await mb.auto_store(
            f"[{v.persona} sub-voice during council on '{req.message[:200]}']\n{v.text[:800]}",
            persona=v.persona, category="agent",
            source_type="persona_chat", source_id=asst_msg.id,
            tags=["persona_chat", v.persona, "council_subvoice", session.id],
        )

    await _messages().insert_one(asst_msg.model_dump())
    await _touch_session(session.id, add_messages=2)

    return ChatResponse(
        session_id=session.id, persona="council",
        reply=reply, message_id=asst_msg.id,
        cited_memory_ids=cited_mem, cited_knowledge_ids=cited_kbase,
        provider_used=provider_used, model_used=model_used,
        fallback_reason=fallback_reason,
        council_voices=sub_voices,
    )


async def chat_any(persona: Persona, req: ChatRequest) -> ChatResponse:
    """Dispatcher — picks single-persona or council fan-out."""
    persona = persona.lower()    # type: ignore[assignment]
    if persona == "council":
        return await _council_chat(req)
    if persona not in PERSONAS:
        raise ValueError(f"unknown persona: {persona!r}")
    return await chat(persona, req)


# ---------------------------------------------------------------------------
# Session / message read APIs
# ---------------------------------------------------------------------------
async def list_sessions(persona: Optional[Persona] = None, limit: int = 50) -> List[Dict[str, Any]]:
    filt: Dict[str, Any] = {}
    if persona:
        filt["persona"] = persona
    cur = _sessions().find(filt, {"_id": 0}).sort("updated_at", -1).limit(limit)
    return [r async for r in cur]


async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    return await _sessions().find_one({"id": session_id}, {"_id": 0})


async def get_messages(session_id: str, limit: int = 200) -> List[Dict[str, Any]]:
    cur = _messages().find({"session_id": session_id}, {"_id": 0}) \
        .sort("created_at", 1).limit(limit)
    return [r async for r in cur]


async def delete_session(session_id: str) -> bool:
    """Hard-delete a session + its messages. The mirrored Memory Bank
    entries are intentionally LEFT BEHIND — the persona keeps what it
    learned even if the chat log is wiped."""
    r1 = await _sessions().delete_one({"id": session_id})
    if r1.deleted_count == 0:
        return False
    await _messages().delete_many({"session_id": session_id})
    return True


def list_personas() -> List[PersonaInfo]:
    return list(PERSONAS.values())

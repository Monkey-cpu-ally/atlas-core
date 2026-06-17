"""
Memory Bank routes — Phase 2.

Public API:
  POST /api/membank/store          — store a memory (auto-embedded)
  GET  /api/membank/search?q=...   — cosine search w/ freshness decay
  GET  /api/membank/list           — list recent memories
  POST /api/membank/reinforce/{id} — bump freshness when reused
  DELETE /api/membank/{id}         — remove a memory
  POST /api/membank/graph/triple   — add a graph triple
  GET  /api/membank/graph/list     — list triples
  GET  /api/membank/graph/around   — neighbourhood around a node
  GET  /api/membank/embed-settings — current embedding provider per persona
  PUT  /api/membank/embed-settings — update embedding provider per persona

Note: this lives at /api/membank/* (not /api/memory/*) so it doesn't
collide with the existing `/api/memory/feed` event-stream endpoint in
hud_surfaces.py. The HUD MemoryPanel keeps its semantics; this is the
new long-term store.
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services import memory_bank as mb

router = APIRouter(prefix="/api/membank", tags=["Memory Bank"])


# --- Memory ------------------------------------------------------------------
class StoreRequest(BaseModel):
    content: str = Field(min_length=3, max_length=8000)
    persona: str = Field(default="council")
    category: str = Field(default="manual")
    source_type: str = Field(default="manual")
    source_id: Optional[str] = None
    tags: Optional[List[str]] = None
    pinned: Optional[bool] = None


@router.post("/store")
async def store(req: StoreRequest):
    try:
        doc = await mb.store_memory(
            req.content,
            persona=req.persona,
            category=req.category,
            source_type=req.source_type,
            source_id=req.source_id,
            tags=req.tags,
            pinned=req.pinned,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except Exception as exc:
        raise HTTPException(502, f"store failed: {exc}") from exc
    return doc


@router.get("/search")
async def search(
    q: str = Query(min_length=2),
    persona: Optional[str] = None,
    category: Optional[str] = None,
    top_k: int = Query(10, ge=1, le=50),
    min_score: float = Query(0.30, ge=0.0, le=1.0),
):
    results = await mb.search_memory(
        q, persona=persona, category=category, top_k=top_k, min_score=min_score,
    )
    return {"q": q, "count": len(results), "results": results}


@router.get("/list")
async def list_endpoint(
    persona: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(40, ge=1, le=200),
    include_decayed: bool = False,
):
    rows = await mb.list_memories(
        persona=persona, category=category, limit=limit, include_decayed=include_decayed,
    )
    return {"count": len(rows), "items": rows}


@router.get("/categories")
async def categories():
    """Return the supported memory categories and which decay."""
    return {
        "permanent": sorted(mb.PERMANENT_CATEGORIES),
        "decaying": sorted(mb.DECAY_CATEGORIES),
        "all": sorted(mb.KNOWN_CATEGORIES),
    }


@router.get("/by-tag")
async def by_tag(
    tag: str = Query(min_length=1),
    persona: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
):
    """Exact-tag lookup — bypasses cosine similarity. Used by tests and
    by any caller that knows the literal tag they're looking for (e.g.
    'persona_chat', a session id, an emergency_stop audit marker)."""
    filt = {"tags": tag.lower() if tag.islower() else tag}
    if persona:
        filt["persona"] = persona.lower()
    if category:
        filt["category"] = category.lower()
    cur = mb._memory().find(filt, {"_id": 0, "embedding": 0}) \
        .sort("created_at", -1).limit(limit)
    rows = [r async for r in cur]
    return {"count": len(rows), "items": rows}


# --- User memory shortcut (permanent, architect notes) ---------------------
class UserMemoryRequest(BaseModel):
    content: str = Field(min_length=3, max_length=8000)
    tags: Optional[List[str]] = None


@router.post("/user")
async def store_user_memory(req: UserMemoryRequest):
    """Permanent user memory — the architect's own notes, preferences,
    standing instructions. Always pinned, always category='user'."""
    doc = await mb.store_memory(
        req.content,
        persona="council",
        category="user",
        source_type="user",
        tags=req.tags or [],
    )
    return doc


@router.get("/user")
async def list_user_memory(limit: int = Query(50, ge=1, le=200)):
    rows = await mb.list_memories(category="user", limit=limit, include_decayed=True)
    return {"count": len(rows), "items": rows}


# --- Research memory shortcut (reinforcement decay) ------------------------
class ResearchMemoryRequest(BaseModel):
    content: str = Field(min_length=3, max_length=8000)
    persona: str = Field(default="hermes")
    source_id: Optional[str] = None
    tags: Optional[List[str]] = None


@router.post("/research")
async def store_research_memory(req: ResearchMemoryRequest):
    """Research memory — anything fetched/analysed via the Phase 3
    research pipeline. Decays unless reinforced (re-cited)."""
    doc = await mb.store_memory(
        req.content,
        persona=req.persona,
        category="research",
        source_type="research",
        source_id=req.source_id,
        tags=req.tags or [],
    )
    return doc


@router.post("/reinforce/{memory_id}")
async def reinforce(memory_id: str):
    doc = await mb.reinforce(memory_id)
    if not doc:
        raise HTTPException(404, "memory not found")
    return doc


@router.delete("/{memory_id}")
async def delete(memory_id: str):
    ok = await mb.delete_memory(memory_id)
    if not ok:
        raise HTTPException(404, "memory not found")
    return {"deleted": memory_id}


# --- Graph -------------------------------------------------------------------
class TripleRequest(BaseModel):
    from_node: str = Field(min_length=1, max_length=200)
    to_node: str = Field(min_length=1, max_length=200)
    relation: str = Field(min_length=1, max_length=80)
    source_id: Optional[str] = None
    weight: float = Field(1.0, ge=0.01, le=10.0)


@router.post("/graph/triple")
async def add_triple(req: TripleRequest):
    return await mb.add_triple(
        from_node=req.from_node,
        to_node=req.to_node,
        relation=req.relation,
        source_id=req.source_id,
        weight=req.weight,
    )


@router.get("/graph/list")
async def list_triples(
    node: Optional[str] = None,
    relation: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500),
):
    rows = await mb.list_triples(node=node, relation=relation, limit=limit)
    return {"count": len(rows), "items": rows}


@router.get("/graph/around")
async def around(
    node: str = Query(min_length=1),
    depth: int = Query(1, ge=1, le=3),
    limit_per_layer: int = Query(12, ge=1, le=40),
):
    return await mb.neighborhood(node, depth=depth, limit_per_layer=limit_per_layer)


# --- Embedding-provider settings (per persona) ------------------------------
@router.get("/embed-settings")
async def embed_settings():
    out: Dict[str, Dict[str, str]] = {}
    for persona in mb.DEFAULT_EMBED_SETTINGS:
        provider, model = await mb.get_embed_settings(persona)
        out[persona] = {"provider": provider, "model": model}
    return {
        "personas": out,
        "providers_available": ["hash", "ollama", "emergent"],
        "notes": (
            "Default: 'hash' — dependency-free deterministic feature-hash embedding "
            "stored in MongoDB. Switch a persona to 'ollama' for semantic embeddings "
            "via a local Ollama server. 'emergent' requires a real OPENAI_API_KEY — "
            "the Emergent universal LLM key does NOT cover the embeddings endpoint."
        ),
    }


class EmbedSettingsUpdate(BaseModel):
    updates: Dict[str, Dict[str, str]] = Field(..., min_length=1)


@router.put("/embed-settings")
async def update_embed_settings(req: EmbedSettingsUpdate):
    res = await mb.set_embed_settings(req.updates)
    if res.get("updated", 0) == 0:
        raise HTTPException(400, "no valid updates (provider must be hash, ollama, or emergent)")
    return res

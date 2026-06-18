"""
Memory Bank — Phase 2.

Vector + graph memory for ATLAS, layered on top of MongoDB. Keeps
everything in one place (no separate vector DB infrastructure):

  * memory_bank          — content rows with an embedding,
                            persona, category, source, freshness/decay
  * graph_triples         — {from, to, relation, source_id, weight}
                            light entity-relation memory
  * atlas_settings        — persona embedding-provider preferences

Embedding providers per persona (Phase 2):
  * 'hash'      — DEFAULT: dependency-free deterministic feature-hash
                  (lexical+ngram). Works offline, never fails, no API key.
  * 'ollama'    — Ollama `nomic-embed-text` (semantic; requires Ollama running)
  * 'emergent'  — OpenAI embeddings via a real OpenAI key in OPENAI_API_KEY
                  (the Emergent universal LLM key does NOT cover embeddings)
"""
import hashlib
import logging
import math
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

import httpx
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from openai import AsyncOpenAI

load_dotenv()
logger = logging.getLogger("atlas.memory_bank")

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

EMBED_DIM = 384  # compact, fast cosine; matches all-MiniLM and the hash backend
DEFAULT_EMBED_PROVIDER = "hash"
DEFAULT_EMBED_MODEL = "atlas-hash-v1"
DEFAULT_OLLAMA_EMBED = "nomic-embed-text"
DEFAULT_OPENAI_EMBED = "text-embedding-3-small"

# Freshness curve: every day reduces freshness by `DECAY_PER_DAY`; each
# re-citation adds `REINFORCEMENT_BUMP` back. Pinned memories ignore decay.
DECAY_PER_DAY = 0.05
REINFORCEMENT_BUMP = 0.20
MIN_FRESHNESS = 0.05  # never falls completely to zero

# --- Memory categories (Phase 2) -------------------------------------------
# Permanent categories never decay (pinned=True at insert time).
# Decaying categories follow the freshness curve and can be re-surfaced
# only when re-cited / reinforced.
PERMANENT_CATEGORIES = {"user", "project", "blueprint", "council", "agent"}
DECAY_CATEGORIES = {"research", "lesson", "intake", "chat", "temporary", "manual", "sandbox"}
KNOWN_CATEGORIES = PERMANENT_CATEGORIES | DECAY_CATEGORIES


# --- Mongo handles -----------------------------------------------------------
_client: Optional[AsyncIOMotorClient] = None
_oa_client: Optional[AsyncOpenAI] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _memory():
    return _db()["memory_bank"]


def _graph():
    return _db()["graph_triples"]


def _settings():
    return _db()["atlas_settings"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _emergent_client() -> AsyncOpenAI:
    """Real OpenAI client for embeddings — uses OPENAI_API_KEY only.

    The Emergent universal LLM key DOES NOT cover the /v1/embeddings
    endpoint (chat completions only). If the architect wants semantic
    OpenAI embeddings they must drop a real OpenAI key in OPENAI_API_KEY.
    """
    global _oa_client
    if _oa_client is None:
        key = OPENAI_API_KEY or EMERGENT_LLM_KEY    # graceful but will 401 if no real key
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        _oa_client = AsyncOpenAI(api_key=key, base_url=base_url)
    return _oa_client


# --- Persona embedding routing ----------------------------------------------
DEFAULT_EMBED_SETTINGS = {
    "ajani":   {"provider": DEFAULT_EMBED_PROVIDER, "model": DEFAULT_EMBED_MODEL},
    "minerva": {"provider": DEFAULT_EMBED_PROVIDER, "model": DEFAULT_EMBED_MODEL},
    "hermes":  {"provider": DEFAULT_EMBED_PROVIDER, "model": DEFAULT_EMBED_MODEL},
    "council": {"provider": DEFAULT_EMBED_PROVIDER, "model": DEFAULT_EMBED_MODEL},
    "default": {"provider": DEFAULT_EMBED_PROVIDER, "model": DEFAULT_EMBED_MODEL},
}


async def get_embed_settings(persona: str) -> Tuple[str, str]:
    persona = (persona or "default").lower()
    doc = await _settings().find_one({"_id": "embedding_models"}, {"_id": 0})
    cfg = (doc or {}).get(persona) or DEFAULT_EMBED_SETTINGS.get(persona) or DEFAULT_EMBED_SETTINGS["default"]
    return cfg["provider"], cfg["model"]


async def set_embed_settings(updates: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    valid = {"hash", "emergent", "ollama", "st"}
    clean: Dict[str, Dict[str, str]] = {}
    for persona, cfg in updates.items():
        if not isinstance(cfg, dict):
            continue
        p = persona.lower()
        provider = str(cfg.get("provider", DEFAULT_EMBED_PROVIDER)).lower()
        if provider not in valid:
            continue
        model = str(cfg.get("model", DEFAULT_EMBED_MODEL))
        clean[p] = {"provider": provider, "model": model}
    if not clean:
        return {"updated": 0}
    await _settings().update_one(
        {"_id": "embedding_models"},
        {"$set": {k: v for k, v in clean.items()}},
        upsert=True,
    )
    return {"updated": len(clean), "personas": clean}


# --- Embedding generators ----------------------------------------------------
_WORD_RE = re.compile(r"[a-z0-9]+")


def _embed_hash(text: str) -> List[float]:
    """Deterministic feature-hash embedding — no external dependencies.

    Combines word-level and character-3-gram features hashed into a
    fixed EMBED_DIM bucket, then L2-normalised. Cosine of two hash
    embeddings approximates lexical + n-gram overlap, which is more
    than enough for memory recall in the ~few-thousand-rows regime.
    """
    vec = [0.0] * EMBED_DIM
    if not text:
        return vec
    lower = text.lower()
    # word features
    words = _WORD_RE.findall(lower)
    for w in words:
        h = int(hashlib.blake2b(w.encode(), digest_size=4).hexdigest(), 16)
        sign = 1.0 if (h & 1) else -1.0
        vec[h % EMBED_DIM] += sign
    # char-3gram features (captures roots, partial matches, mistypes)
    padded = f"  {lower}  "
    for i in range(len(padded) - 2):
        g = padded[i:i + 3]
        h = int(hashlib.blake2b(g.encode(), digest_size=4).hexdigest(), 16)
        sign = 1.0 if (h & 2) else -1.0
        vec[h % EMBED_DIM] += sign * 0.3        # tri-grams weighted less than words
    # L2 normalise so cosine == dot
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


async def _embed_emergent(text: str, model: str) -> List[float]:
    if not OPENAI_API_KEY:
        raise EmbedError("OPENAI_API_KEY not set — Emergent universal key does not cover embeddings")
    client = _emergent_client()
    resp = await client.embeddings.create(model=model or DEFAULT_OPENAI_EMBED, input=text[:8000])
    return resp.data[0].embedding


async def _embed_ollama(text: str, model: str) -> List[float]:
    url = f"{OLLAMA_HOST.rstrip('/')}/api/embeddings"
    payload = {"model": model or DEFAULT_OLLAMA_EMBED, "prompt": text[:8000]}
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
        except httpx.RequestError as exc:
            raise EmbedUnreachable(f"Ollama embeddings unreachable: {exc}") from exc
    vec = data.get("embedding") or []
    if not vec:
        raise EmbedError("Ollama returned empty embedding")
    return vec


# --- Sentence-Transformers (local, CPU) ------------------------------------
# Loaded lazily once, kept in-process. Returns 384-dim L2-normalised vectors
# from `all-MiniLM-L6-v2` (same EMBED_DIM as the hash backend so existing
# rows + new ST rows remain cosine-comparable on dim).
_ST_MODEL = None
_ST_LOAD_LOCK = None
DEFAULT_ST_EMBED = "sentence-transformers/all-MiniLM-L6-v2"


def _ensure_st_model(model_name: str):
    """Load the sentence-transformer model lazily. Heavy import is local
    so the rest of memory_bank doesn't pay the cost at module import."""
    global _ST_MODEL
    if _ST_MODEL is not None:
        return _ST_MODEL
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise EmbedError(f"sentence-transformers not installed: {exc}") from exc
    logger.info("Loading sentence-transformer model: %s", model_name)
    _ST_MODEL = SentenceTransformer(model_name or DEFAULT_ST_EMBED, device="cpu")
    logger.info("ST model ready: dim=%s", _ST_MODEL.get_sentence_embedding_dimension())
    return _ST_MODEL


async def _embed_st(text: str, model: str) -> List[float]:
    import asyncio as _asyncio

    def _run():
        m = _ensure_st_model(model or DEFAULT_ST_EMBED)
        vec = m.encode(text[:8000], normalize_embeddings=True)
        return [float(x) for x in vec.tolist()]
    return await _asyncio.to_thread(_run)


class EmbedUnreachable(Exception): pass    # noqa: E701
class EmbedError(Exception): pass          # noqa: E701


async def embed(text: str, persona: str = "default") -> Tuple[List[float], Dict[str, Any]]:
    """Return (embedding_vector, meta) for `text` using the persona's
    preferred embedder. Falls back to the local hash embedder on any
    upstream failure so the pipeline can never block on embeddings."""
    provider, model = await get_embed_settings(persona)
    meta: Dict[str, Any] = {"persona": persona, "provider_requested": provider, "model": model}
    try:
        if provider == "ollama":
            vec = await _embed_ollama(text, model)
            meta["provider_used"] = "ollama"
        elif provider == "emergent":
            vec = await _embed_emergent(text, model)
            meta["provider_used"] = "emergent"
        elif provider == "st":
            vec = await _embed_st(text, model)
            meta["provider_used"] = "st"
            meta["model"] = model or DEFAULT_ST_EMBED
        else:
            vec = _embed_hash(text)
            meta["provider_used"] = "hash"
            meta["model"] = DEFAULT_EMBED_MODEL
    except (EmbedUnreachable, EmbedError, Exception) as exc:    # noqa: BLE001
        if provider == "hash":
            raise
        logger.warning("Embed fallback to hash: %s", exc)
        meta["fallback_reason"] = str(exc)[:200]
        vec = _embed_hash(text)
        meta["provider_used"] = "hash"
        meta["model"] = DEFAULT_EMBED_MODEL
    return vec, meta


# --- Vector math -------------------------------------------------------------
def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0 or nb == 0:
        return 0.0
    return dot / (math.sqrt(na) * math.sqrt(nb))


# --- Memory CRUD -------------------------------------------------------------
async def store_memory(
    content: str,
    *,
    persona: str = "council",
    category: str = "manual",          # see PERMANENT_CATEGORIES / DECAY_CATEGORIES
    source_type: str = "manual",     # 'manual' | 'lesson' | 'intake' | 'sandbox' | 'chat'
    source_id: Optional[str] = None,
    tags: Optional[List[str]] = None,
    pinned: Optional[bool] = None,
) -> Dict[str, Any]:
    if not content or len(content.strip()) < 3:
        raise ValueError("content too short")
    cat = (category or "manual").lower()
    if cat not in KNOWN_CATEGORIES:
        cat = "manual"
    # Permanent categories are auto-pinned unless caller explicitly opts out.
    if pinned is None:
        pinned = cat in PERMANENT_CATEGORIES
    vec, embed_meta = await embed(content, persona=persona)
    doc = {
        "id": str(uuid4()),
        "content": content,
        "persona": persona.lower(),
        "category": cat,
        "permanent": cat in PERMANENT_CATEGORIES,
        "source_type": source_type,
        "source_id": source_id,
        "tags": tags or [],
        "pinned": bool(pinned),
        "freshness": 1.0,
        "reinforce_count": 0,
        "created_at": _utc_now(),
        "last_referenced": _utc_now(),
        "embedding": vec,
        "embed_meta": embed_meta,
    }
    await _memory().insert_one(doc.copy())
    return {k: v for k, v in doc.items() if k != "embedding"}    # don't echo the 1536-d vector


async def auto_store(
    content: str,
    *,
    persona: str = "council",
    category: str = "temporary",
    source_type: str = "manual",
    source_id: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """Fire-and-forget store used by intake/learning/council hooks.

    Wraps store_memory in a try/except so a failed embedding call never
    aborts the parent pipeline. Returns the stored row (minus the
    embedding) on success, None on failure."""
    if not content or len(content.strip()) < 3:
        return None
    try:
        return await store_memory(
            content,
            persona=persona,
            category=category,
            source_type=source_type,
            source_id=source_id,
            tags=tags,
        )
    except Exception as exc:    # noqa: BLE001 — intentional fire-and-forget
        logger.warning("memory_bank.auto_store failed (category=%s): %s", category, exc)
        return None


async def _decay_score(memory_doc: Dict[str, Any]) -> float:
    """Return current freshness adjusted for age — applied in-query, never written
    back unless the memory is reinforced. Pinned memories stay at 1.0."""
    if memory_doc.get("pinned"):
        return 1.0
    base = float(memory_doc.get("freshness", 1.0))
    try:
        ref = datetime.fromisoformat(memory_doc.get("last_referenced", _utc_now()))
    except ValueError:
        return base
    age_days = (datetime.now(timezone.utc) - ref).total_seconds() / 86400.0
    return max(MIN_FRESHNESS, base - DECAY_PER_DAY * age_days)


async def search_memory(
    query: str,
    *,
    persona: Optional[str] = None,
    category: Optional[str] = None,
    top_k: int = 10,
    min_score: float = 0.30,
) -> List[Dict[str, Any]]:
    """Cosine-similarity search. We compute scores in Python — fine up to
    a few thousand memories. When the architect scales past that, swap
    this for Mongo Atlas Vector Search (same field name, same dim)."""
    qvec, _ = await embed(query, persona=persona or "default")
    filt: Dict[str, Any] = {}
    if persona:
        filt["persona"] = persona.lower()
    if category:
        filt["category"] = category.lower()
    cursor = _memory().find(filt, {"_id": 0})
    rows = await cursor.to_list(length=2000)
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for row in rows:
        emb = row.get("embedding") or []
        sim = _cosine(qvec, emb)
        # Combine similarity with current freshness so stale memories
        # surface less unless they're pinned.
        fresh = await _decay_score(row)
        score = 0.85 * sim + 0.15 * fresh
        if score >= min_score:
            row.pop("embedding", None)        # don't return raw vectors
            row["sim"] = round(sim, 4)
            row["freshness_now"] = round(fresh, 4)
            row["score"] = round(score, 4)
            scored.append((score, row))
    scored.sort(key=lambda t: t[0], reverse=True)
    return [r for _, r in scored[:top_k]]


async def reinforce(memory_id: str) -> Optional[Dict[str, Any]]:
    """Bump the freshness counter — call this when a memory is re-cited
    by the council, surfaced in a lesson, or pinned in a chat."""
    doc = await _memory().find_one({"id": memory_id}, {"_id": 0, "embedding": 0})
    if not doc:
        return None
    new_freshness = min(1.0, float(doc.get("freshness", 1.0)) + REINFORCEMENT_BUMP)
    update = {
        "freshness": new_freshness,
        "reinforce_count": int(doc.get("reinforce_count", 0)) + 1,
        "last_referenced": _utc_now(),
    }
    await _memory().update_one({"id": memory_id}, {"$set": update})
    doc.update(update)
    return doc


async def list_memories(
    persona: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 40,
    include_decayed: bool = False,
) -> List[Dict[str, Any]]:
    filt: Dict[str, Any] = {}
    if persona:
        filt["persona"] = persona.lower()
    if category:
        filt["category"] = category.lower()
    cursor = _memory().find(filt, {"_id": 0, "embedding": 0}).sort("last_referenced", -1).limit(limit)
    rows = await cursor.to_list(length=limit)
    out = []
    for row in rows:
        fresh = await _decay_score(row)
        if not include_decayed and fresh <= MIN_FRESHNESS:
            continue
        row["freshness_now"] = round(fresh, 4)
        out.append(row)
    return out


async def delete_memory(memory_id: str) -> bool:
    res = await _memory().delete_one({"id": memory_id})
    return res.deleted_count > 0


# --- Graph memory ------------------------------------------------------------
async def add_triple(
    *,
    from_node: str,
    to_node: str,
    relation: str,
    source_id: Optional[str] = None,
    weight: float = 1.0,
) -> Dict[str, Any]:
    """Light entity-relation triple. We upsert on (from, to, relation)
    so repeated learnings reinforce the same edge instead of duplicating."""
    key = {
        "from_node": from_node.strip(),
        "to_node": to_node.strip(),
        "relation": relation.strip().lower(),
    }
    set_ops = {**key, "source_id": source_id, "updated_at": _utc_now()}
    await _graph().update_one(
        key,
        {"$set": set_ops, "$inc": {"weight": weight, "hits": 1}},
        upsert=True,
    )
    doc = await _graph().find_one(key, {"_id": 0})
    return doc or {**set_ops, "weight": weight, "hits": 1}


async def list_triples(
    node: Optional[str] = None,
    relation: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    filt: Dict[str, Any] = {}
    if node:
        filt["$or"] = [{"from_node": node}, {"to_node": node}]
    if relation:
        filt["relation"] = relation.lower()
    cursor = _graph().find(filt, {"_id": 0}).sort("weight", -1).limit(limit)
    return await cursor.to_list(length=limit)


async def neighborhood(
    node: str,
    depth: int = 1,
    limit_per_layer: int = 12,
    min_weight: float = 0.0,
) -> Dict[str, Any]:
    """BFS up to `depth` hops away from `node`. Returns a compact view
    suitable for a UI graph render: {nodes:[], edges:[]}.

    `min_weight` filters out low-confidence edges (default 0.0 → include
    every edge). Useful for HUD graph viz where you only want the
    strongest associations.
    """
    seen_nodes = {node}
    edges_out: List[Dict[str, Any]] = []
    frontier = {node}
    for _ in range(max(1, depth)):
        if not frontier:
            break
        filt: Dict[str, Any] = {
            "$or": [
                {"from_node": {"$in": list(frontier)}},
                {"to_node":   {"$in": list(frontier)}},
            ],
        }
        if min_weight > 0:
            filt["weight"] = {"$gte": float(min_weight)}
        cursor = _graph().find(
            filt, {"_id": 0},
        ).sort("weight", -1).limit(limit_per_layer * len(frontier))
        layer = await cursor.to_list(length=limit_per_layer * len(frontier))
        next_frontier = set()
        for e in layer:
            edges_out.append(e)
            for endpoint in (e["from_node"], e["to_node"]):
                if endpoint not in seen_nodes:
                    seen_nodes.add(endpoint)
                    next_frontier.add(endpoint)
        frontier = next_frontier
    return {
        "root": node,
        "depth": depth,
        "min_weight": float(min_weight),
        "nodes": sorted(seen_nodes),
        "edges": edges_out,
    }

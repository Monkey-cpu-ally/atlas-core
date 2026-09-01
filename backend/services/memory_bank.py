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

try:
    from openai import AsyncOpenAI
except ImportError:  # openai<1 compatibility for older/local environments
    AsyncOpenAI = None

load_dotenv()
logger = logging.getLogger("atlas.memory_bank")

EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

EMBED_DIM = 384
DEFAULT_EMBED_PROVIDER = "hash"
DEFAULT_EMBED_MODEL = "atlas-hash-v1"
DEFAULT_OLLAMA_EMBED = "nomic-embed-text"
DEFAULT_OPENAI_EMBED = "text-embedding-3-small"

DECAY_PER_DAY = 0.05
REINFORCEMENT_BUMP = 0.20
MIN_FRESHNESS = 0.05

PERMANENT_CATEGORIES = {"user", "project", "blueprint", "council", "agent"}
DECAY_CATEGORIES = {"research", "lesson", "intake", "chat", "temporary", "manual", "sandbox"}
KNOWN_CATEGORIES = PERMANENT_CATEGORIES | DECAY_CATEGORIES

_client: Optional[AsyncIOMotorClient] = None
_oa_client = None


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


def _emergent_client():
    """Create the modern OpenAI embeddings client when available."""
    global _oa_client
    if AsyncOpenAI is None:
        raise EmbedError("Installed openai package does not provide AsyncOpenAI")
    if _oa_client is None:
        key = OPENAI_API_KEY or EMERGENT_LLM_KEY
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        _oa_client = AsyncOpenAI(api_key=key, base_url=base_url)
    return _oa_client


DEFAULT_EMBED_SETTINGS = {
    "ajani": {"provider": DEFAULT_EMBED_PROVIDER, "model": DEFAULT_EMBED_MODEL},
    "minerva": {"provider": DEFAULT_EMBED_PROVIDER, "model": DEFAULT_EMBED_MODEL},
    "hermes": {"provider": DEFAULT_EMBED_PROVIDER, "model": DEFAULT_EMBED_MODEL},
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


_WORD_RE = re.compile(r"[a-z0-9]+")


def _embed_hash(text: str) -> List[float]:
    vec = [0.0] * EMBED_DIM
    if not text:
        return vec
    lower = text.lower()
    words = _WORD_RE.findall(lower)
    for w in words:
        h = int(hashlib.blake2b(w.encode(), digest_size=4).hexdigest(), 16)
        sign = 1.0 if (h & 1) else -1.0
        vec[h % EMBED_DIM] += sign
    padded = f"  {lower}  "
    for i in range(len(padded) - 2):
        g = padded[i:i + 3]
        h = int(hashlib.blake2b(g.encode(), digest_size=4).hexdigest(), 16)
        sign = 1.0 if (h & 2) else -1.0
        vec[h % EMBED_DIM] += sign * 0.3
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


async def _embed_emergent(text: str, model: str) -> List[float]:
    if not OPENAI_API_KEY:
        raise EmbedError("OPENAI_API_KEY not set — Emergent universal key does not cover embeddings")
    if AsyncOpenAI is not None:
        client = _emergent_client()
        resp = await client.embeddings.create(model=model or DEFAULT_OPENAI_EMBED, input=text[:8000])
        return resp.data[0].embedding

    # Compatibility path for openai<1. This keeps module import/startup working
    # in older environments while still performing a real provider call.
    import openai

    openai.api_key = OPENAI_API_KEY
    response = await openai.Embedding.acreate(model=model or DEFAULT_OPENAI_EMBED, input=text[:8000])
    return response["data"][0]["embedding"]


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


_ST_MODEL = None
_ST_LOAD_LOCK = None
DEFAULT_ST_EMBED = "sentence-transformers/all-MiniLM-L6-v2"


def _ensure_st_model(model_name: str):
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


class EmbedUnreachable(Exception):
    pass


class EmbedError(Exception):
    pass


async def embed(text: str, persona: str = "default") -> Tuple[List[float], Dict[str, Any]]:
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
    except (EmbedUnreachable, EmbedError, Exception) as exc:
        logger.warning("Embedding provider %s failed (%s); falling back to hash", provider, exc)
        vec = _embed_hash(text)
        meta["provider_used"] = "hash"
        meta["fallback_reason"] = str(exc)
    return vec, meta


async def add_memory(
    content: str,
    persona: str = "default",
    category: str = "research",
    source: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    category = category if category in KNOWN_CATEGORIES else "research"
    vec, embed_meta = await embed(content, persona)
    now = _utc_now()
    doc = {
        "_id": str(uuid4()),
        "content": content,
        "persona": persona.lower(),
        "category": category,
        "source": source,
        "metadata": metadata or {},
        "embedding": vec,
        "embedding_meta": embed_meta,
        "freshness": 1.0,
        "pinned": category in PERMANENT_CATEGORIES,
        "created_at": now,
        "updated_at": now,
        "last_reinforced_at": now,
    }
    await _memory().insert_one(doc)
    return {k: v for k, v in doc.items() if k != "embedding"}


async def search_memory(query: str, persona: str = "default", limit: int = 8) -> List[Dict[str, Any]]:
    qvec, _ = await embed(query, persona)
    cursor = _memory().find({"persona": {"$in": [persona.lower(), "default", "shared"]}})
    rows = await cursor.to_list(length=2000)
    scored = []
    for row in rows:
        vec = row.get("embedding") or []
        if len(vec) != len(qvec):
            continue
        similarity = sum(a * b for a, b in zip(qvec, vec))
        score = similarity * float(row.get("freshness", 1.0))
        item = {k: v for k, v in row.items() if k != "embedding"}
        item["similarity"] = similarity
        item["score"] = score
        scored.append(item)
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[: max(1, min(limit, 100))]


async def reinforce_memory(memory_id: str) -> bool:
    row = await _memory().find_one({"_id": memory_id})
    if not row:
        return False
    freshness = min(1.0, float(row.get("freshness", 1.0)) + REINFORCEMENT_BUMP)
    await _memory().update_one(
        {"_id": memory_id},
        {"$set": {"freshness": freshness, "last_reinforced_at": _utc_now(), "updated_at": _utc_now()}},
    )
    return True


async def add_graph_triple(
    from_entity: str,
    to_entity: str,
    relation: str,
    source_id: Optional[str] = None,
    weight: float = 1.0,
) -> Dict[str, Any]:
    doc = {
        "_id": str(uuid4()),
        "from": from_entity,
        "to": to_entity,
        "relation": relation,
        "source_id": source_id,
        "weight": float(weight),
        "created_at": _utc_now(),
    }
    await _graph().insert_one(doc)
    return doc


async def graph_neighbors(entity: str, limit: int = 50) -> List[Dict[str, Any]]:
    cursor = _graph().find({"$or": [{"from": entity}, {"to": entity}]}).limit(max(1, min(limit, 500)))
    return await cursor.to_list(length=max(1, min(limit, 500)))


async def decay_memories() -> Dict[str, int]:
    rows = await _memory().find({"pinned": {"$ne": True}}).to_list(length=10000)
    updated = 0
    now = datetime.now(timezone.utc)
    for row in rows:
        stamp = row.get("last_reinforced_at") or row.get("updated_at") or row.get("created_at")
        try:
            then = datetime.fromisoformat(stamp)
            if then.tzinfo is None:
                then = then.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            continue
        days = max(0.0, (now - then).total_seconds() / 86400.0)
        freshness = max(MIN_FRESHNESS, 1.0 - days * DECAY_PER_DAY)
        await _memory().update_one({"_id": row["_id"]}, {"$set": {"freshness": freshness}})
        updated += 1
    return {"updated": updated}

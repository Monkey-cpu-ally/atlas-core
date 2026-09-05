"""
Memory Bank — Phase 2.

Persistent vector + graph memory for ATLAS. The public API preserves the
original Phase 2 memory contracts while keeping OpenAI SDK compatibility.
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
except ImportError:
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
DEFAULT_ST_EMBED = "sentence-transformers/all-MiniLM-L6-v2"
DECAY_PER_DAY = 0.05
REINFORCEMENT_BUMP = 0.20
MIN_FRESHNESS = 0.05

PERMANENT_CATEGORIES = {"user", "project", "blueprint", "council", "agent"}
DECAY_CATEGORIES = {"research", "lesson", "intake", "chat", "temporary", "manual", "sandbox"}
KNOWN_CATEGORIES = PERMANENT_CATEGORIES | DECAY_CATEGORIES

_client: Optional[AsyncIOMotorClient] = None
_oa_client = None
_ST_MODEL = None


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


class EmbedUnreachable(Exception):
    pass


class EmbedError(Exception):
    pass


def _emergent_client():
    global _oa_client
    if AsyncOpenAI is None:
        raise EmbedError("Installed openai package does not provide AsyncOpenAI")
    if _oa_client is None:
        if not OPENAI_API_KEY:
            raise EmbedError("OPENAI_API_KEY not set")
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        _oa_client = AsyncOpenAI(api_key=OPENAI_API_KEY, base_url=base_url)
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
        provider = str(cfg.get("provider", DEFAULT_EMBED_PROVIDER)).lower()
        if provider not in valid:
            continue
        clean[persona.lower()] = {"provider": provider, "model": str(cfg.get("model", DEFAULT_EMBED_MODEL))}
    if not clean:
        return {"updated": 0}
    await _settings().update_one({"_id": "embedding_models"}, {"$set": clean}, upsert=True)
    return {"updated": len(clean), "personas": clean}


_WORD_RE = re.compile(r"[a-z0-9]+")


def _embed_hash(text: str) -> List[float]:
    vec = [0.0] * EMBED_DIM
    if not text:
        return vec
    lower = text.lower()
    for word in _WORD_RE.findall(lower):
        h = int(hashlib.blake2b(word.encode(), digest_size=4).hexdigest(), 16)
        vec[h % EMBED_DIM] += 1.0 if h & 1 else -1.0
    padded = f"  {lower}  "
    for i in range(len(padded) - 2):
        h = int(hashlib.blake2b(padded[i:i + 3].encode(), digest_size=4).hexdigest(), 16)
        vec[h % EMBED_DIM] += (1.0 if h & 2 else -1.0) * 0.3
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


async def _embed_emergent(text: str, model: str) -> List[float]:
    if not OPENAI_API_KEY:
        raise EmbedError("OPENAI_API_KEY not set — Emergent universal key does not cover embeddings")
    if AsyncOpenAI is not None:
        response = await _emergent_client().embeddings.create(model=model or DEFAULT_OPENAI_EMBED, input=text[:8000])
        return response.data[0].embedding
    import openai
    openai.api_key = OPENAI_API_KEY
    response = await openai.Embedding.acreate(model=model or DEFAULT_OPENAI_EMBED, input=text[:8000])
    return response["data"][0]["embedding"]


async def _embed_ollama(text: str, model: str) -> List[float]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{OLLAMA_HOST.rstrip('/')}/api/embeddings",
                json={"model": model or DEFAULT_OLLAMA_EMBED, "prompt": text[:8000]},
            )
            response.raise_for_status()
        except httpx.RequestError as exc:
            raise EmbedUnreachable(f"Ollama embeddings unreachable: {exc}") from exc
    vec = response.json().get("embedding") or []
    if not vec:
        raise EmbedError("Ollama returned empty embedding")
    return vec


def _ensure_st_model(model_name: str):
    global _ST_MODEL
    if _ST_MODEL is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise EmbedError(f"sentence-transformers not installed: {exc}") from exc
        _ST_MODEL = SentenceTransformer(model_name or DEFAULT_ST_EMBED, device="cpu")
    return _ST_MODEL


async def _embed_st(text: str, model: str) -> List[float]:
    import asyncio
    def _run():
        vec = _ensure_st_model(model or DEFAULT_ST_EMBED).encode(text[:8000], normalize_embeddings=True)
        return [float(x) for x in vec.tolist()]
    return await asyncio.to_thread(_run)


async def embed(text: str, persona: str = "default") -> Tuple[List[float], Dict[str, Any]]:
    provider, model = await get_embed_settings(persona)
    meta: Dict[str, Any] = {"persona": persona, "provider_requested": provider, "model": model}
    try:
        if provider == "ollama":
            vec = await _embed_ollama(text, model)
        elif provider == "emergent":
            vec = await _embed_emergent(text, model)
        elif provider == "st":
            vec = await _embed_st(text, model)
        else:
            vec = _embed_hash(text)
            provider = "hash"
        meta["provider_used"] = provider
    except Exception as exc:  # provider failure must not kill memory recall
        if provider == "hash":
            raise
        logger.warning("Embed fallback to hash: %s", exc)
        vec = _embed_hash(text)
        meta.update({"provider_used": "hash", "model": DEFAULT_EMBED_MODEL, "fallback_reason": str(exc)[:200]})
    return vec, meta


def _cosine(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a)
    nb = sum(y * y for y in b)
    return dot / (math.sqrt(na) * math.sqrt(nb)) if na and nb else 0.0


async def store_memory(content: str, *, persona: str = "council", category: str = "manual", source_type: str = "manual", source_id: Optional[str] = None, tags: Optional[List[str]] = None, pinned: Optional[bool] = None) -> Dict[str, Any]:
    if not content or len(content.strip()) < 3:
        raise ValueError("content too short")
    cat = (category or "manual").lower()
    if cat not in KNOWN_CATEGORIES:
        cat = "manual"
    if pinned is None:
        pinned = cat in PERMANENT_CATEGORIES
    vec, embed_meta = await embed(content, persona=persona)
    doc = {"id": str(uuid4()), "content": content, "persona": persona.lower(), "category": cat, "permanent": cat in PERMANENT_CATEGORIES, "source_type": source_type, "source_id": source_id, "tags": tags or [], "pinned": bool(pinned), "freshness": 1.0, "reinforce_count": 0, "created_at": _utc_now(), "last_referenced": _utc_now(), "embedding": vec, "embed_meta": embed_meta}
    await _memory().insert_one(doc.copy())
    return {k: v for k, v in doc.items() if k != "embedding"}


async def add_memory(content: str, persona: str = "default", category: str = "research", source: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Compatibility alias for callers introduced during runtime stabilization."""
    metadata = metadata or {}
    return await store_memory(content, persona=persona, category=category, source_type=str(metadata.get("source_type", "manual")), source_id=source, tags=metadata.get("tags"))


async def auto_store(content: str, *, persona: str = "council", category: str = "temporary", source_type: str = "manual", source_id: Optional[str] = None, tags: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    if not content or len(content.strip()) < 3:
        return None
    try:
        return await store_memory(content, persona=persona, category=category, source_type=source_type, source_id=source_id, tags=tags)
    except Exception as exc:
        logger.warning("memory_bank.auto_store failed (category=%s): %s", category, exc)
        return None


async def _decay_score(memory_doc: Dict[str, Any]) -> float:
    if memory_doc.get("pinned"):
        return 1.0
    base = float(memory_doc.get("freshness", 1.0))
    stamp = memory_doc.get("last_referenced") or memory_doc.get("last_reinforced_at") or memory_doc.get("created_at")
    try:
        ref = datetime.fromisoformat(stamp or _utc_now())
        if ref.tzinfo is None:
            ref = ref.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return base
    age_days = max(0.0, (datetime.now(timezone.utc) - ref).total_seconds() / 86400.0)
    return max(MIN_FRESHNESS, base - DECAY_PER_DAY * age_days)


async def search_memory(query: str, *, persona: Optional[str] = None, category: Optional[str] = None, top_k: int = 10, min_score: float = 0.30, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    if limit is not None:
        top_k = limit
    qvec, _ = await embed(query, persona=persona or "default")
    filt: Dict[str, Any] = {}
    if persona:
        filt["persona"] = persona.lower()
    if category:
        filt["category"] = category.lower()
    rows = await _memory().find(filt, {"_id": 0}).to_list(length=2000)
    scored = []
    for row in rows:
        sim = _cosine(qvec, row.get("embedding") or [])
        fresh = await _decay_score(row)
        score = 0.85 * sim + 0.15 * fresh
        if score >= min_score:
            row.pop("embedding", None)
            row.update({"sim": round(sim, 4), "freshness_now": round(fresh, 4), "score": round(score, 4)})
            scored.append((score, row))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [row for _, row in scored[:max(1, min(top_k, 100))]]


async def reinforce(memory_id: str) -> Optional[Dict[str, Any]]:
    doc = await _memory().find_one({"id": memory_id}, {"_id": 0, "embedding": 0})
    if not doc:
        return None
    update = {"freshness": min(1.0, float(doc.get("freshness", 1.0)) + REINFORCEMENT_BUMP), "reinforce_count": int(doc.get("reinforce_count", 0)) + 1, "last_referenced": _utc_now()}
    await _memory().update_one({"id": memory_id}, {"$set": update})
    doc.update(update)
    return doc


async def reinforce_memory(memory_id: str) -> bool:
    return await reinforce(memory_id) is not None


async def list_memories(persona: Optional[str] = None, category: Optional[str] = None, limit: int = 40, include_decayed: bool = False) -> List[Dict[str, Any]]:
    filt: Dict[str, Any] = {}
    if persona:
        filt["persona"] = persona.lower()
    if category:
        filt["category"] = category.lower()
    rows = await _memory().find(filt, {"_id": 0, "embedding": 0}).sort("last_referenced", -1).limit(limit).to_list(length=limit)
    out = []
    for row in rows:
        fresh = await _decay_score(row)
        if include_decayed or fresh > MIN_FRESHNESS:
            row["freshness_now"] = round(fresh, 4)
            out.append(row)
    return out


async def delete_memory(memory_id: str) -> bool:
    return (await _memory().delete_one({"id": memory_id})).deleted_count > 0


async def add_triple(*, from_node: str, to_node: str, relation: str, source_id: Optional[str] = None, weight: float = 1.0) -> Dict[str, Any]:
    key = {"from_node": from_node.strip(), "to_node": to_node.strip(), "relation": relation.strip().lower()}
    set_ops = {**key, "source_id": source_id, "updated_at": _utc_now()}
    await _graph().update_one(key, {"$set": set_ops, "$inc": {"weight": weight, "hits": 1}}, upsert=True)
    return await _graph().find_one(key, {"_id": 0}) or {**set_ops, "weight": weight, "hits": 1}


async def add_graph_triple(from_entity: str, to_entity: str, relation: str, source_id: Optional[str] = None, weight: float = 1.0) -> Dict[str, Any]:
    return await add_triple(from_node=from_entity, to_node=to_entity, relation=relation, source_id=source_id, weight=weight)


async def list_triples(node: Optional[str] = None, relation: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    filt: Dict[str, Any] = {}
    if node:
        filt["$or"] = [{"from_node": node}, {"to_node": node}]
    if relation:
        filt["relation"] = relation.lower()
    return await _graph().find(filt, {"_id": 0}).sort("weight", -1).limit(limit).to_list(length=limit)


async def graph_neighbors(entity: str, limit: int = 50) -> List[Dict[str, Any]]:
    return await list_triples(node=entity, limit=limit)


async def neighborhood(node: str, depth: int = 1, limit_per_layer: int = 12, min_weight: float = 0.0) -> Dict[str, Any]:
    seen_nodes = {node}
    edges_out: List[Dict[str, Any]] = []
    frontier = {node}
    for _ in range(max(1, depth)):
        if not frontier:
            break
        filt: Dict[str, Any] = {"$or": [{"from_node": {"$in": list(frontier)}}, {"to_node": {"$in": list(frontier)}}]}
        if min_weight > 0:
            filt["weight"] = {"$gte": float(min_weight)}
        layer = await _graph().find(filt, {"_id": 0}).sort("weight", -1).limit(limit_per_layer * len(frontier)).to_list(length=limit_per_layer * len(frontier))
        next_frontier = set()
        for edge in layer:
            edges_out.append(edge)
            for endpoint in (edge["from_node"], edge["to_node"]):
                if endpoint not in seen_nodes:
                    seen_nodes.add(endpoint)
                    next_frontier.add(endpoint)
        frontier = next_frontier
    return {"root": node, "depth": depth, "min_weight": float(min_weight), "nodes": sorted(seen_nodes), "edges": edges_out}


async def decay_memories() -> Dict[str, int]:
    rows = await _memory().find({"pinned": {"$ne": True}}, {"_id": 0}).to_list(length=10000)
    updated = 0
    for row in rows:
        memory_id = row.get("id")
        if not memory_id:
            continue
        freshness = await _decay_score(row)
        await _memory().update_one({"id": memory_id}, {"$set": {"freshness": freshness}})
        updated += 1
    return {"updated": updated}

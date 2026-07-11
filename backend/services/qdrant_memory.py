"""Qdrant semantic-memory service for ATLAS.

This module complements MongoDB: Mongo remains the source of truth while
Qdrant stores searchable vectors keyed by the same memory IDs.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Dict, Iterable, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY") or None
QDRANT_COLLECTION = os.environ.get("QDRANT_COLLECTION", "atlas_memory")
EMBED_MODEL = os.environ.get("ATLAS_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def client() -> QdrantClient:
    return QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=10.0)


@lru_cache(maxsize=1)
def embedder():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBED_MODEL)


def embed_text(text: str) -> List[float]:
    cleaned = (text or "").strip()
    if not cleaned:
        raise ValueError("text must not be empty")
    vector = embedder().encode(cleaned, normalize_embeddings=True)
    return vector.tolist()


def ensure_collection() -> Dict[str, Any]:
    qdrant = client()
    existing = {item.name for item in qdrant.get_collections().collections}
    if QDRANT_COLLECTION not in existing:
        dimensions = len(embed_text("ATLAS vector-dimension probe"))
        qdrant.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=dimensions, distance=Distance.COSINE),
        )
        return {"collection": QDRANT_COLLECTION, "created": True, "dimensions": dimensions}
    info = qdrant.get_collection(QDRANT_COLLECTION)
    return {"collection": QDRANT_COLLECTION, "created": False, "status": str(info.status)}


def upsert_memory(memory_id: str, content: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    ensure_collection()
    point = PointStruct(
        id=memory_id,
        vector=embed_text(content),
        payload={"content": content, **(payload or {})},
    )
    client().upsert(collection_name=QDRANT_COLLECTION, points=[point], wait=True)
    return {"id": memory_id, "collection": QDRANT_COLLECTION, "stored": True}


def upsert_many(records: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    ensure_collection()
    points: List[PointStruct] = []
    for record in records:
        memory_id = str(record["id"])
        content = str(record["content"])
        payload = {k: v for k, v in record.items() if k not in {"id", "content", "embedding"}}
        payload["content"] = content
        points.append(PointStruct(id=memory_id, vector=embed_text(content), payload=payload))
    if points:
        client().upsert(collection_name=QDRANT_COLLECTION, points=points, wait=True)
    return {"collection": QDRANT_COLLECTION, "stored": len(points)}


def search_memory(query: str, limit: int = 8, score_threshold: float = 0.25) -> List[Dict[str, Any]]:
    ensure_collection()
    hits = client().search(
        collection_name=QDRANT_COLLECTION,
        query_vector=embed_text(query),
        limit=max(1, min(limit, 50)),
        score_threshold=score_threshold,
        with_payload=True,
    )
    return [
        {"id": str(hit.id), "score": float(hit.score), "payload": hit.payload or {}}
        for hit in hits
    ]


def delete_memory(memory_id: str) -> Dict[str, Any]:
    client().delete(collection_name=QDRANT_COLLECTION, points_selector=[memory_id], wait=True)
    return {"id": memory_id, "deleted": True}


def health() -> Dict[str, Any]:
    try:
        collections = client().get_collections().collections
        return {
            "ok": True,
            "url": QDRANT_URL,
            "collection": QDRANT_COLLECTION,
            "collections": [item.name for item in collections],
            "embed_model": EMBED_MODEL,
        }
    except Exception as exc:
        return {
            "ok": False,
            "url": QDRANT_URL,
            "collection": QDRANT_COLLECTION,
            "embed_model": EMBED_MODEL,
            "error": str(exc)[:300],
        }

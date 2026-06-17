"""
Knowledge Ingestion orchestrator.

Pipeline:
  1. fetch(url) via source_fetchers
  2. distill() via knowledge_distiller (LLM-routed agent)
  3. dedup by sha256(normalised_url):
       - if exists → reinforce existing memory_bank row + bump record.reinforce_count
       - else → persist new KnowledgeRecord + memory_bank row
  4. graph triples (auto-stored via Phase-2 memory_bank.add_triple):
       concept   -> relates_to  -> tag
       project   -> uses        -> concept     (when related_projects has entries)
       agent     -> studies     -> concept     (1 per agent in related_agents)

Storage:
  * `knowledge_records` collection  — the structured record
  * `memory_bank` Phase-2 row       — searchable distilled text; category is
                                        chosen per agent:
                                          ajani/minerva/hermes  → category=research (decays)
                                          council               → category=council  (permanent)
                                        a project_id forces category=project (permanent)
"""
import logging
import os
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient

from models.knowledge_models import (
    Distillation,
    FetchedSource,
    KnowledgeRecord,
    SourceType,
    url_hash,
)
from services import memory_bank as mb
from services.knowledge_distiller import distill
from services.source_fetchers import IngestError, fetch

logger = logging.getLogger("atlas.knowledge_ingestion")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _records():
    return _db()["knowledge_records"]


# --- Category decision -----------------------------------------------------
def _category_for(agent: str, project_id: Optional[str]) -> str:
    if project_id:
        return "project"
    if agent == "council":
        return "council"
    # research memory decays unless reinforced — matches the architect's rule.
    return "research"


# --- Main entry point ------------------------------------------------------
async def ingest_url(
    url: str, *,
    project_id: Optional[str] = None,
    force_agent: Optional[str] = None,
    extra_tags: Optional[List[str]] = None,
    pdf_blob_b64: Optional[str] = None,
    pdf_filename: Optional[str] = None,
) -> Dict[str, Any]:
    """Ingest a URL end-to-end. Returns {record, reused, memory_bank_id, mb_row}.

    Raises IngestError on hard fetch failure (404, rate-limit, unreachable)."""
    source: FetchedSource = await fetch(
        url, pdf_blob_b64=pdf_blob_b64, pdf_filename=pdf_filename,
    )
    distilled: Distillation = await distill(source, force_agent=force_agent)

    h = url_hash(source.source_url)
    existing = await _records().find_one({"source_hash": h}, {"_id": 0})
    if existing:
        return await _reinforce(existing, distilled, source, extra_tags or [], project_id)

    # Net new — build the record and persist.
    tags = list({*distilled.tags, *(extra_tags or [])})
    agent = distilled.suggested_agent
    category = _category_for(agent, project_id)
    body = _compose_body(distilled, source)
    mb_row = await mb.auto_store(
        body, persona=agent, category=category,
        source_type=source.source_type.value,
        source_id=None,                # set after we mint record.id
        tags=tags + [source.source_type.value, "knowledge"],
    )
    mb_id = (mb_row or {}).get("id")

    record = KnowledgeRecord(
        title=distilled.title,
        summary=distilled.summary,
        key_points=distilled.key_points,
        tags=tags,
        source_type=source.source_type,
        source_url=source.source_url,
        source_hash=h,
        source_author=source.author,
        confidence_score=distilled.confidence_score,
        related_agents=[agent],
        related_projects=[project_id] if project_id else [],
        concepts=distilled.concepts,
        memory_bank_id=mb_id,
    )
    await _records().insert_one(record.model_dump())
    await _wire_graph(record)
    return {"record": _strip(record.model_dump()), "reused": False,
            "memory_bank_id": mb_id}


# --- Reinforce path --------------------------------------------------------
async def _reinforce(
    existing: Dict[str, Any], distilled: Distillation, source: FetchedSource,
    extra_tags: List[str], project_id: Optional[str],
) -> Dict[str, Any]:
    """Same URL re-ingested → bump freshness, merge tags/concepts, append
    agent if a new persona analysed it, link a new project if provided."""
    mb_id = existing.get("memory_bank_id")
    if mb_id:
        try:
            await mb.reinforce(mb_id)
        except Exception as exc:    # noqa: BLE001
            logger.warning("memory reinforce failed: %s", exc)

    updates: Dict[str, Any] = {
        "reinforce_count": int(existing.get("reinforce_count", 0)) + 1,
        "updated_at": _now(),
        "confidence_score": _max(existing.get("confidence_score", 0.0),
                                 distilled.confidence_score),
    }
    merged_tags = list({*(existing.get("tags") or []), *distilled.tags, *extra_tags})
    if merged_tags != (existing.get("tags") or []):
        updates["tags"] = merged_tags
    merged_concepts = list({*(existing.get("concepts") or []), *distilled.concepts})
    if merged_concepts != (existing.get("concepts") or []):
        updates["concepts"] = merged_concepts
    merged_agents = list({*(existing.get("related_agents") or []),
                          distilled.suggested_agent})
    if merged_agents != (existing.get("related_agents") or []):
        updates["related_agents"] = merged_agents
    if project_id:
        merged_projects = list({*(existing.get("related_projects") or []), project_id})
        if merged_projects != (existing.get("related_projects") or []):
            updates["related_projects"] = merged_projects

    await _records().update_one(
        {"source_hash": existing["source_hash"]}, {"$set": updates},
    )
    refreshed = await _records().find_one(
        {"source_hash": existing["source_hash"]}, {"_id": 0},
    )
    # Re-wire any new graph nodes the merge introduced.
    if refreshed:
        await _wire_graph(KnowledgeRecord(**refreshed))
    return {"record": _strip(refreshed or existing), "reused": True,
            "memory_bank_id": mb_id}


# --- Graph wiring ----------------------------------------------------------
async def _wire_graph(rec: KnowledgeRecord) -> None:
    """Emit graph triples as the architect specified:
         source_concept  -> relates_to -> subject(tag)
         project         -> uses       -> concept
         agent           -> studies    -> concept
    """
    src_id = rec.id
    # concept -> relates_to -> tag
    for concept in rec.concepts:
        for tag in rec.tags[:5]:    # cap edges so we don't explode the graph
            try:
                await mb.add_triple(from_node=concept, to_node=tag,
                                    relation="relates_to",
                                    source_id=src_id, weight=1.0)
            except Exception as exc:    # noqa: BLE001
                logger.debug("triple skip %s→%s: %s", concept, tag, exc)
    # project -> uses -> concept
    for pid in rec.related_projects:
        for concept in rec.concepts:
            try:
                await mb.add_triple(from_node=pid, to_node=concept,
                                    relation="uses",
                                    source_id=src_id, weight=1.0)
            except Exception:    # noqa: BLE001
                pass
    # agent -> studies -> concept
    for agent in rec.related_agents:
        for concept in rec.concepts:
            try:
                await mb.add_triple(from_node=agent, to_node=concept,
                                    relation="studies",
                                    source_id=src_id, weight=1.0)
            except Exception:    # noqa: BLE001
                pass


# --- Search & view ---------------------------------------------------------
async def search(
    *, q: Optional[str] = None, agent: Optional[str] = None,
    project_id: Optional[str] = None, source_type: Optional[str] = None,
    tag: Optional[str] = None, limit: int = 30,
) -> List[Dict[str, Any]]:
    filt: Dict[str, Any] = {}
    if agent:
        filt["related_agents"] = agent
    if project_id:
        filt["related_projects"] = project_id
    if source_type:
        filt["source_type"] = source_type
    if tag:
        filt["tags"] = tag.lower()
    if q:
        # Mongo text-ish: regex across title + summary + tags
        regex = {"$regex": re.escape(q), "$options": "i"}
        filt["$or"] = [
            {"title": regex}, {"summary": regex}, {"tags": regex},
            {"concepts": regex},
        ]
    cur = _records().find(filt, {"_id": 0}).sort("updated_at", -1).limit(limit)
    return [_strip(d) async for d in cur]


async def get(record_id: str) -> Optional[Dict[str, Any]]:
    return await _records().find_one({"id": record_id}, {"_id": 0})


async def get_by_url(url: str) -> Optional[Dict[str, Any]]:
    return await _records().find_one({"source_hash": url_hash(url)}, {"_id": 0})


async def delete(record_id: str) -> bool:
    rec = await get(record_id)
    if not rec:
        return False
    await _records().delete_one({"id": record_id})
    return True


# --- Helpers ---------------------------------------------------------------
import re

def _compose_body(d: Distillation, src: FetchedSource) -> str:
    """The searchable text written into memory_bank — the architect's distilled
    knowledge, NEVER the raw transcript / readme / page body."""
    bullets = "\n".join(f"- {kp}" for kp in d.key_points)
    return (
        f"{d.title}\n\n"
        f"SOURCE: {src.source_type.value} · {src.source_url}\n"
        f"AUTHOR: {src.author or '—'}\n"
        f"CONFIDENCE: {d.confidence_score}\n\n"
        f"SUMMARY:\n{d.summary}\n\n"
        f"KEY POINTS:\n{bullets}\n\n"
        f"TAGS: {', '.join(d.tags)}\n"
        f"CONCEPTS: {', '.join(d.concepts)}"
    ).strip()


def _max(a, b) -> float:
    return max(float(a or 0.0), float(b or 0.0))


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()


def _strip(doc: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in doc.items() if k != "_id"}

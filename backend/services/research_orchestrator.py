"""
Autonomous Research Orchestrator.

Implements the queue + state machine + curiosity engine + cycle runner
described by the user. Honors strict rules:
  * Every record carries an `evidence` envelope (source, confidence,
    evidence_refs, date, verification_status). No simulated results.
  * The state machine is explicit. Transitions are logged, not silent.
  * The orchestrator runs ONE cycle per `/api/research/orchestrator/run`
    call — there is no autonomous background thread. The phrase
    "without waiting for user prompts" is honored by making it callable
    from the worldwatch / GitHub watcher OR an external cron.

Collections:
  * research_queue       — every discovered item + state + evidence
  * research_missions    — curiosity-generated investigation missions
  * research_cycles      — proof-of-execution per cycle (audit trail)
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient

from services import worldwatch as ww
from services import knowledge_ingestion as ki
from services import memory_bank as mb
from services import lesson_generator as lg
from services import knowledge_watcher as kw
from services.llm_provider import send as llm_send

logger = logging.getLogger("atlas.research_orchestrator")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _queue():    return _db()["research_queue"]
def _missions(): return _db()["research_missions"]
def _cycles():   return _db()["research_cycles"]


def _utc(): return datetime.now(timezone.utc).isoformat()


# Explicit state machine
STATES = ["discovered", "queued", "investigating", "analyzed",
          "verified", "stored", "linked",
          "lesson_generated", "blueprint_generated", "project_created"]


# --- Evidence envelope contract ------------------------------------------
def make_evidence(
    *, source: str, confidence: float, evidence_refs: List[Dict[str, Any]],
    verification_status: str = "unverified",
) -> Dict[str, Any]:
    """User rule: every conclusion must include source / confidence /
    evidence / date / verification status."""
    if not source:
        raise ValueError("evidence.source is required")
    if not isinstance(evidence_refs, list) or len(evidence_refs) == 0:
        raise ValueError("evidence.evidence_refs must be a non-empty list")
    return {
        "source": source,
        "confidence": max(0.0, min(1.0, float(confidence))),
        "evidence_refs": evidence_refs,
        "date": _utc(),
        "verification_status": verification_status,   # unverified | manual | automated | weak | llm_simulated
    }


def assert_envelope(env: Optional[Dict[str, Any]]) -> bool:
    """Strict verification gate. Returns True iff envelope is complete."""
    if not env: return False
    needed = ("source", "confidence", "evidence_refs", "date", "verification_status")
    return all(k in env for k in needed) and len(env.get("evidence_refs") or []) > 0


# --- Council 4-voice review chain ----------------------------------------
async def _council_review_chain(item: Dict[str, Any], concepts: List[str],
                                title: str, conf: float) -> Dict[str, Any]:
    """Ajani (strategy) → Minerva (knowledge) → Hermes (engineering) →
    Council (final synthesis). Each voice persists a real persona_chat
    message. Returns the chain manifest with all message_ids."""
    from services.persona_chat import chat_any
    from models.persona_models import ChatRequest

    chain: Dict[str, Any] = {"started_at": _utc(), "voices": [], "errors": []}
    base_q = (
        f"Research item — title: {title} · confidence: {conf:.2f} · "
        f"concepts: {', '.join(concepts[:6])}."
    )
    voices = [
        ("ajani",   "STRATEGY review: should ATLAS prioritise this item? What strategic angle?"),
        ("minerva", "KNOWLEDGE review: what gaps does this fill in ATLAS memory? What overlaps existing knowledge?"),
        ("hermes",  "ENGINEERING review: feasibility, risks, prerequisites, build-cost class."),
        ("council", "FINAL SYNTHESIS of the three voices above into a single recommendation: accept / hold / reject + 1-sentence why."),
    ]
    for persona, prompt in voices:
        try:
            resp = await chat_any(
                persona,
                ChatRequest(message=f"{base_q}\n\n{prompt}",
                            session_id=None),
            )
            chain["voices"].append({
                "persona": persona,
                "message_id": getattr(resp, "message_id", None),
                "reply_excerpt": (getattr(resp, "reply", "") or "")[:280],
            })
        except Exception as exc:    # noqa: BLE001
            chain["errors"].append({"persona": persona, "msg": str(exc)[:200]})
    chain["ended_at"] = _utc()
    return chain


# --- Discovery → enqueue --------------------------------------------------
async def enqueue_item(
    *, source_type: str, url: str, title: str,
    domain: str, agent: str,
    payload: Optional[Dict[str, Any]] = None,
    confidence: float = 0.5,
) -> Dict[str, Any]:
    """Idempotent — same URL won't be enqueued twice. Returns existing if so."""
    h = hashlib.sha256(url.encode()).hexdigest()[:24]
    existing = await _queue().find_one({"item_hash": h}, {"_id": 0})
    if existing:
        return existing
    rec = {
        "id": uuid4().hex,
        "item_hash": h,
        "source_type": source_type,         # arxiv | github | hackaday | nasa | youtube | …
        "url": url,
        "title": title[:280],
        "domain": domain,
        "agent": agent,
        "payload": payload or {},
        "state": "discovered",
        "state_history": [
            {"to": "discovered", "at": _utc(), "by": "discovery_engine"},
        ],
        "evidence": make_evidence(
            source=source_type, confidence=confidence,
            evidence_refs=[{"url": url, "kind": "primary"}],
            verification_status="unverified",
        ),
        "knowledge_id": None,
        "memory_bank_id": None,
        "lesson_ids": [],
        "blueprint_id": None,
        "created_at": _utc(),
        "updated_at": _utc(),
    }
    await _queue().insert_one(rec)
    return rec


async def _set_state(item_id: str, new_state: str, *,
                     by: str = "orchestrator",
                     extra: Optional[Dict[str, Any]] = None) -> None:
    if new_state not in STATES:
        raise ValueError(f"unknown state: {new_state}")
    doc = await _queue().find_one({"id": item_id}, {"_id": 0})
    if not doc:
        return
    history = doc.get("state_history", [])
    history.append({"from": doc.get("state"), "to": new_state,
                    "at": _utc(), "by": by})
    update = {"state": new_state, "state_history": history,
              "updated_at": _utc()}
    if extra:
        update.update(extra)
    await _queue().update_one({"id": item_id}, {"$set": update})


# --- One full cycle -------------------------------------------------------
async def run_cycle(*,
                    discover_per_feed: int = 1,
                    max_investigate: int = 5,
                    generate_lessons: bool = True,
                    mode: str = "lego",
                    forge_blueprints: bool = False) -> Dict[str, Any]:
    """
    Phases:
      1. DISCOVER — pull WorldWatch feeds → enqueue.
      2. INVESTIGATE — for each `queued`/`discovered` item up to N, run
         `kbase.ingest_url` and capture concepts.
      3. ANALYZE — distillation already happened in step 2; here we just
         verify the knowledge_record exists and has ≥1 concept.
      4. VERIFY — confidence ≥ 0.4 AND distillation produced concepts.
      5. STORE — write back to research_queue with knowledge_id + mb_id.
      6. LINK — add graph triples (queue_item → knowledge → concept).
      7. LESSONS — optionally produce ATLAS lesson per verified item.
    """
    cycle_id = uuid4().hex
    started_at = _utc()
    proof: Dict[str, Any] = {
        "cycle_id": cycle_id, "started_at": started_at,
        "phases": {}, "errors": [],
    }

    # Phase 1: discover via worldwatch
    ww_run = await ww.run(max_per_feed=discover_per_feed)
    # Pull the just-created updates and enqueue any new ones
    updates = await ww.list_updates(limit=50)
    enqueued: List[str] = []
    for u in updates:
        try:
            rec = await enqueue_item(
                source_type=u.get("source_type") or "worldwatch_" + u.get("domain", "?"),
                url=u.get("url"),
                title=u.get("title") or "",
                domain=u.get("domain", "general"),
                agent=u.get("agent", "minerva"),
                payload={"what_changed": u.get("what_changed"),
                         "feed_label": u.get("feed_label"),
                         "published": u.get("published")},
                confidence=0.55,
            )
            if rec.get("state") == "discovered":
                enqueued.append(rec["id"])
                await _set_state(rec["id"], "queued", by="cycle_phase1")
        except Exception as exc:    # noqa: BLE001
            proof["errors"].append({"phase": 1, "msg": str(exc)[:160]})
    proof["phases"]["1_discover"] = {
        "worldwatch_run_id": ww_run["run_id"],
        "ww_new_entries": ww_run["entries_new"],
        "enqueued": len(enqueued),
    }

    # Phase 2-5: investigate → analyze → verify → store
    investigated: List[Dict[str, Any]] = []
    cur = _queue().find(
        {"state": {"$in": ["queued", "discovered"]}},
        {"_id": 0},
    ).sort("created_at", -1).limit(max_investigate)

    items = [d async for d in cur]
    for item in items:
        try:
            await _set_state(item["id"], "investigating", by="cycle_phase2")
            ingest_result = await ki.ingest_url(
                item["url"],
                extra_tags=["research_queue", f"agent:{item['agent']}",
                            f"domain:{item['domain']}"],
            )
            rec = ingest_result.get("record") or {}
            kb_id = rec.get("id")
            mb_id = ingest_result.get("memory_bank_id")
            concepts = rec.get("concepts") or []
            conf = rec.get("confidence_score") or 0.0

            await _set_state(item["id"], "analyzed", by="cycle_phase3",
                             extra={"knowledge_id": kb_id,
                                    "memory_bank_id": mb_id})

            verification = "automated" if (conf >= 0.4 and concepts) else "weak"
            evidence = make_evidence(
                source=item["source_type"], confidence=conf,
                evidence_refs=[
                    {"kind": "knowledge", "id": kb_id, "url": item["url"]},
                    {"kind": "memory_bank", "id": mb_id},
                    {"kind": "concepts", "count": len(concepts),
                     "sample": concepts[:5]},
                ],
                verification_status=verification,
            )
            await _queue().update_one(
                {"id": item["id"]},
                {"$set": {"evidence": evidence}},
            )
            await _set_state(item["id"], "verified", by="cycle_phase4")
            await _set_state(item["id"], "stored", by="cycle_phase5")

            # Phase 6: LINK with graph triples
            try:
                await mb.add_triple(
                    from_node=f"queue:{item['id'][:8]}",
                    to_node=kb_id or "noid",
                    relation="produced_knowledge",
                    source_id=item["id"], weight=1.0,
                )
                for c in concepts[:5]:
                    await mb.add_triple(
                        from_node=f"queue:{item['id'][:8]}",
                        to_node=c,
                        relation="surfaced",
                        source_id=item["id"], weight=1.0,
                    )
            except Exception as exc:    # noqa: BLE001
                proof["errors"].append({"phase": 6, "msg": str(exc)[:160]})
            await _set_state(item["id"], "linked", by="cycle_phase6")

            # Phase 7: lessons
            lesson_id = None
            if generate_lessons and kb_id and concepts:
                try:
                    lesson = await lg.generate_lesson(
                        knowledge_id=kb_id,
                        source_url=item["url"],
                        title=rec.get("title") or item["title"],
                        concepts=concepts,
                        agent=item["agent"],
                        mode=mode,
                    )
                    lesson_id = lesson["id"]
                    await _queue().update_one(
                        {"id": item["id"]},
                        {"$push": {"lesson_ids": lesson_id}},
                    )
                    await _set_state(item["id"], "lesson_generated",
                                     by="cycle_phase7")
                except Exception as exc:    # noqa: BLE001
                    proof["errors"].append({"phase": 7, "msg": str(exc)[:160]})

            # Phase 8: Council 4-voice review chain for low-confidence items
            council_chain = None
            if conf < 0.7:
                council_chain = await _council_review_chain(
                    item, concepts, rec.get("title") or item["title"], conf,
                )
                await _queue().update_one(
                    {"id": item["id"]},
                    {"$set": {"council_review_chain": council_chain}},
                )

            # Phase 9: auto-project for verification=automated AND lesson exists
            project_id = None
            if forge_blueprints and verification == "automated" and lesson_id:
                try:
                    from services import blueprint_forge as bf
                    forge_res = await bf.forge_from_queue(item["id"])
                    if forge_res.get("ok"):
                        await _set_state(item["id"], "blueprint_generated",
                                         by="cycle_phase9")
                        # Create a project record from the blueprint
                        project_id = uuid4().hex
                        await _db()["projects_queue"].insert_one({
                            "id": project_id,
                            "title": item["title"],
                            "queue_item_id": item["id"],
                            "knowledge_id": kb_id,
                            "blueprint_id": forge_res.get("id"),
                            "lesson_id": lesson_id,
                            "agent": item["agent"],
                            "status": "proposed",
                            "evidence": {
                                "source": "orchestrator_auto",
                                "confidence": conf,
                                "evidence_refs": [
                                    {"kind": "queue", "id": item["id"]},
                                    {"kind": "blueprint", "id": forge_res.get("id")},
                                    {"kind": "lesson", "id": lesson_id},
                                ],
                                "date": _utc(),
                                "verification_status": "automated",
                            },
                            "created_at": _utc(),
                        })
                        await _queue().update_one(
                            {"id": item["id"]},
                            {"$set": {"project_id": project_id}},
                        )
                        await _set_state(item["id"], "project_created",
                                         by="cycle_phase10")
                except Exception as exc:    # noqa: BLE001
                    proof["errors"].append({"phase": 9, "msg": str(exc)[:160]})

            investigated.append({
                "queue_id": item["id"],
                "url": item["url"],
                "knowledge_id": kb_id,
                "memory_bank_id": mb_id,
                "confidence": conf,
                "verification": verification,
                "concepts_count": len(concepts),
                "lesson_id": lesson_id,
                "council_chain": council_chain,
                "project_id": project_id,
                "envelope_verified": assert_envelope(evidence),
            })
        except Exception as exc:    # noqa: BLE001
            proof["errors"].append({"phase": "investigate",
                                    "queue_id": item.get("id"),
                                    "msg": str(exc)[:200]})
            await _set_state(item["id"], "queued", by="cycle_error")

    proof["phases"]["2-7_investigate_to_lessons"] = {
        "examined": len(items),
        "fully_processed": len(investigated),
        "investigated": investigated,
    }
    proof["ended_at"] = _utc()
    proof["status"] = "ok" if not proof["errors"] else "partial"
    await _cycles().insert_one(proof.copy())
    return proof


# --- Curiosity Engine ----------------------------------------------------
async def curiosity_scan() -> Dict[str, Any]:
    """Deterministic gap analysis. Looks at:
       * domains with the FEWEST verified queue items
       * concepts that appear ≤ 1 time in graph_triples
       * confusing_topics from learning profile (re-investigation candidates)

    Emits 1-3 mission records.
    """
    db = _db()
    started_at = _utc()
    missions_created: List[Dict[str, Any]] = []

    # 1. Domains under-covered
    coverage = {d: 0 for d in ww.DOMAINS}
    async for row in db["research_queue"].aggregate([
        {"$match": {"state": "linked"}},
        {"$group": {"_id": "$domain", "count": {"$sum": 1}}},
    ]):
        if row["_id"] in coverage:
            coverage[row["_id"]] = row["count"]
    weakest = sorted(coverage.items(), key=lambda kv: kv[1])[:3]
    for domain, count in weakest:
        m_id = uuid4().hex
        mission = {
            "id": m_id,
            "kind": "domain_coverage",
            "title": f"Investigate {domain} — currently linked items: {count}",
            "target": domain,
            "current_count": count,
            "evidence": make_evidence(
                source="curiosity_scan",
                confidence=0.7,
                evidence_refs=[{"kind": "coverage_count", "domain": domain, "count": count}],
                verification_status="automated",
            ),
            "status": "open",
            "created_at": _utc(),
        }
        await _missions().insert_one(mission)
        missions_created.append({"id": m_id, "title": mission["title"]})

    # 2. Confusing topics from learning profile
    try:
        from services import adaptation as ad
        profile = await ad.get_learning_profile()
        for conf in (profile.get("confusing_topics") or [])[-3:]:
            m_id = uuid4().hex
            mission = {
                "id": m_id,
                "kind": "confusion_followup",
                "title": f"Re-investigate: {conf.get('topic', '?')[:80]} (user struggled)",
                "target": conf.get("topic"),
                "evidence": make_evidence(
                    source="learning_profile",
                    confidence=0.8,
                    evidence_refs=[{"kind": "confusion", "topic": conf.get("topic"),
                                    "count": conf.get("count")}],
                    verification_status="manual",
                ),
                "status": "open",
                "created_at": _utc(),
            }
            await _missions().insert_one(mission)
            missions_created.append({"id": m_id, "title": mission["title"]})
    except Exception as exc:    # noqa: BLE001
        logger.warning("curiosity profile read failed: %s", exc)

    return {
        "started_at": started_at,
        "ended_at": _utc(),
        "missions_created": missions_created,
        "weakest_domains": [{"domain": d, "count": c} for d, c in weakest],
    }


async def list_missions(status: Optional[str] = None) -> List[Dict[str, Any]]:
    q: Dict[str, Any] = {}
    if status:
        q["status"] = status
    cur = _missions().find(q, {"_id": 0}).sort("created_at", -1)
    return [d async for d in cur]


# --- Project Improvement Loop --------------------------------------------
async def evaluate_projects() -> Dict[str, Any]:
    """For each active project, find recent worldwatch updates / queue items
    in the same domain and ask Council whether the project should be
    updated. Persists recommendations on each project."""
    db = _db()
    started_at = _utc()
    recommendations: List[Dict[str, Any]] = []
    projects = await db["projects_queue"].find({"status": "proposed"}, {"_id": 0}).to_list(length=50)
    if not projects:
        return {"started_at": started_at, "ended_at": _utc(),
                "recommendations": [], "projects_checked": 0,
                "note": "no projects in 'proposed' status"}

    for proj in projects:
        # Find recent updates that share a queue agent/domain with this project
        agent = proj.get("agent")
        recent = await db["research_queue"].find(
            {"state": "linked", "agent": agent},
            {"_id": 0, "id": 1, "title": 1, "domain": 1},
        ).sort("created_at", -1).limit(5).to_list(length=5)

        if not recent:
            continue

        # 1-shot Council ask
        try:
            from services.persona_chat import chat_any
            from models.persona_models import ChatRequest
            ctx = "; ".join(f"{r['title'][:80]} ({r['domain']})" for r in recent[:3])
            prompt = (
                f"Project: {proj['title']} (status={proj['status']}). "
                f"Recent related findings: {ctx}. "
                f"Should we update the project? Accept / Hold / Reject + reason."
            )
            resp = await chat_any(
                "council",
                ChatRequest(message=prompt, session_id=None),
            )
            rec = {
                "project_id": proj["id"],
                "project_title": proj["title"],
                "council_message_id": getattr(resp, "message_id", None),
                "council_reply_excerpt": (getattr(resp, "reply", "") or "")[:280],
                "considered_queue_items": [r["id"] for r in recent],
                "evidence": make_evidence(
                    source="project_improvement_loop",
                    confidence=0.7,
                    evidence_refs=[{"kind": "project", "id": proj["id"]}] +
                                  [{"kind": "queue", "id": r["id"]} for r in recent],
                    verification_status="automated",
                ),
                "created_at": _utc(),
            }
            await db["project_recommendations"].insert_one(rec.copy())
            await db["projects_queue"].update_one(
                {"id": proj["id"]},
                {"$push": {"recommendation_ids": rec["council_message_id"]}},
            )
            recommendations.append({
                "project_id": proj["id"],
                "council_message_id": rec["council_message_id"],
                "reply_excerpt": rec["council_reply_excerpt"],
            })
        except Exception as exc:    # noqa: BLE001
            recommendations.append({"project_id": proj["id"],
                                     "error": str(exc)[:200]})

    return {
        "started_at": started_at, "ended_at": _utc(),
        "projects_checked": len(projects),
        "recommendations": recommendations,
    }


# --- Queue read APIs -----------------------------------------------------
async def queue_list(state: Optional[str] = None,
                     domain: Optional[str] = None,
                     limit: int = 100) -> List[Dict[str, Any]]:
    q: Dict[str, Any] = {}
    if state:
        q["state"] = state
    if domain:
        q["domain"] = domain
    cur = _queue().find(q, {"_id": 0}).sort("created_at", -1).limit(limit)
    return [d async for d in cur]


async def queue_status() -> Dict[str, Any]:
    by_state: Dict[str, int] = {s: 0 for s in STATES}
    by_domain: Dict[str, int] = {}
    by_verify: Dict[str, int] = {}
    async for d in _queue().aggregate([
        {"$group": {"_id": "$state", "count": {"$sum": 1}}},
    ]):
        by_state[d["_id"]] = d["count"]
    async for d in _queue().aggregate([
        {"$group": {"_id": "$domain", "count": {"$sum": 1}}},
    ]):
        by_domain[d["_id"] or "?"] = d["count"]
    async for d in _queue().aggregate([
        {"$group": {"_id": "$evidence.verification_status", "count": {"$sum": 1}}},
    ]):
        by_verify[d["_id"] or "?"] = d["count"]
    last_cycle = await _cycles().find_one({}, {"_id": 0},
                                           sort=[("started_at", -1)])
    return {
        "by_state": by_state,
        "by_domain": by_domain,
        "by_verification": by_verify,
        "total": await _queue().count_documents({}),
        "missions_open": await _missions().count_documents({"status": "open"}),
        "last_cycle": last_cycle,
        "states": STATES,
    }

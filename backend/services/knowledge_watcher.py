"""
Knowledge Watcher — actively ingests GitHub link-list repositories.

Pipeline per source registration:
  1. Fetch the repo README via existing `_fetch_github` (60k char cap).
  2. Extract every URL we recognise (YouTube channel/video/playlist, websites,
     PDFs, other GitHub repos, arXiv, generic).
  3. For each extracted URL: run the existing kbase.ingest_url pipeline so
     we get distillation → memory mirror → graph triples for free.
  4. For YouTube specifically: if transcript fetch fails (the cloud-IP block
     is known and graceful), record `transcript_status=TRANSCRIPT_UNAVAILABLE`
     and store the source URL + extracted-from-README metadata only — never
     a full copyrighted transcript.
  5. Persist a `watcher_runs` document containing **proof of execution**:
     files scanned, links extracted, ingest results per URL, errors, IDs.

Collections used:
  * watchers       — registry of monitored sources
  * watcher_runs   — proof-of-execution records (one per run)
  * (downstream): knowledge_records, memory_bank, graph_triples, lessons

Public surface used by routes/watchers.py:
  - register_github_source(url, *, label=None)
  - run_github_watcher(source_id, *, generate_lesson=True)
  - list_sources()
  - get_status(source_id)
  - get_proof(source_id)
"""
from __future__ import annotations

import hashlib
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse, urldefrag
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient

from services import memory_bank as mb
from services import knowledge_ingestion as ki
from services.source_fetchers import IngestError, classify, _fetch_github  # type: ignore
from services.lesson_generator import generate_lesson as _generate_lesson

logger = logging.getLogger("atlas.knowledge_watcher")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _watchers(): return _db()["watchers"]
def _runs():     return _db()["watcher_runs"]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


# --- URL extraction --------------------------------------------------------
_URL_RE = re.compile(r"https?://[^\s\)\]\}\>\"'`,]+", re.IGNORECASE)


def _category_heading_for(line_idx: int, lines: List[str]) -> Optional[str]:
    """Walk backwards from this line until we find a markdown heading (# / ## / ###)."""
    for i in range(line_idx, -1, -1):
        ln = lines[i].strip()
        m = re.match(r"^#{1,6}\s+(.+?)\s*$", ln)
        if m:
            return m.group(1).strip()
    return None


def _classify_link(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if "youtube.com" in host or "youtu.be" in host:
        if "/playlist" in url or "list=" in url:
            return "youtube_playlist"
        if "/channel/" in url or "/c/" in url or "/@" in url or host.endswith("youtube.com") and "/user/" in url:
            return "youtube_channel"
        return "youtube_video"
    if "github.com" in host:
        return "github"
    if "arxiv.org" in host:
        return "arxiv"
    if url.lower().endswith(".pdf"):
        return "pdf"
    return "web"


def _extract_links(readme_text: str) -> List[Dict[str, Any]]:
    """Return a list of {url, kind, category} dicts. Dedupes by URL."""
    out: List[Dict[str, Any]] = []
    seen: set = set()
    lines = readme_text.splitlines()
    for idx, line in enumerate(lines):
        for raw in _URL_RE.findall(line):
            url, _ = urldefrag(raw.rstrip(".,;:!?"))
            if url in seen:
                continue
            seen.add(url)
            kind = _classify_link(url)
            heading = _category_heading_for(idx, lines) or "uncategorised"
            out.append({"url": url, "kind": kind, "category": heading})
    return out


# --- Source registry -------------------------------------------------------
async def register_github_source(url: str, *, label: Optional[str] = None) -> Dict[str, Any]:
    """Register a GitHub repo as a watcher source. Idempotent (returns existing)."""
    if "github.com" not in (urlparse(url).hostname or ""):
        raise ValueError(f"not a github url: {url}")
    h = hashlib.sha256(url.encode()).hexdigest()[:24]
    existing = await _watchers().find_one({"source_hash": h}, {"_id": 0})
    if existing:
        return existing
    doc = {
        "id": uuid4().hex,
        "source_hash": h,
        "url": url,
        "label": label or url,
        "kind": "github",
        "registered_at": _utc(),
        "last_run_at": None,
        "last_commit_sha": None,
        "run_count": 0,
        "status": "registered",
    }
    await _watchers().insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}


async def list_sources(kind: Optional[str] = None) -> List[Dict[str, Any]]:
    q: Dict[str, Any] = {}
    if kind:
        q["kind"] = kind
    cur = _watchers().find(q, {"_id": 0}).sort("registered_at", -1)
    return [d async for d in cur]


# --- Run a watcher ---------------------------------------------------------
async def run_github_watcher(
    source_id: str, *, generate_lesson: bool = True, max_links: int = 40,
) -> Dict[str, Any]:
    """Fetch README, extract links, ingest each through kbase, optionally
    generate a lesson plan from the first high-confidence result. Returns
    full proof-of-execution record."""
    src = await _watchers().find_one({"id": source_id}, {"_id": 0})
    if not src:
        raise ValueError(f"unknown watcher source: {source_id}")

    run_id = uuid4().hex
    started_at = _utc()
    proof: Dict[str, Any] = {
        "run_id": run_id,
        "source_id": source_id,
        "source_url": src["url"],
        "started_at": started_at,
        "files_scanned": [],
        "links_extracted": [],
        "ingest_results": [],
        "knowledge_ids": [],
        "memory_ids": [],
        "graph_edges_created": 0,
        "lessons_created": [],
        "errors": [],
        "transcripts_found": 0,
        "transcripts_unavailable": 0,
    }

    # 1. Fetch README
    try:
        fetched = await _fetch_github(src["url"])
        readme_text = fetched.text or ""
        proof["files_scanned"].append({
            "filename": "README",
            "chars": len(readme_text),
            "title": fetched.title,
        })
    except IngestError as exc:
        proof["errors"].append({"stage": "fetch_readme", "msg": str(exc)})
        await _persist_run(proof, status="failed", started_at=started_at)
        return proof

    # 2. Extract links
    links = _extract_links(readme_text)[:max_links]
    proof["links_extracted"] = links

    # 3. Ingest each link through kbase pipeline
    graph_before = await _count_graph_edges()
    for link in links:
        url = link["url"]
        kind = link["kind"]
        category = link["category"]
        try:
            result = await ki.ingest_url(
                url,
                extra_tags=[
                    f"watcher:{source_id[:8]}",
                    f"category:{_slug(category)}",
                    f"kind:{kind}",
                ],
            )
            record = result.get("record", {})
            mb_id = result.get("memory_bank_id")
            proof["ingest_results"].append({
                "url": url,
                "kind": kind,
                "category": category,
                "knowledge_id": record.get("id"),
                "memory_bank_id": mb_id,
                "reused": result.get("reused", False),
                "title": record.get("title"),
                "agent": (record.get("related_agents") or ["unknown"])[0],
                "concepts": record.get("concepts", [])[:5],
                "confidence": record.get("confidence_score"),
            })
            if record.get("id"):
                proof["knowledge_ids"].append(record["id"])
            if mb_id:
                proof["memory_ids"].append(mb_id)
            if kind.startswith("youtube"):
                proof["transcripts_found"] += 1
        except IngestError as exc:
            err_msg = str(exc)
            proof["ingest_results"].append({
                "url": url,
                "kind": kind,
                "category": category,
                "status": "TRANSCRIPT_UNAVAILABLE" if kind.startswith("youtube") else "fetch_failed",
                "error": err_msg[:200],
            })
            if kind.startswith("youtube"):
                proof["transcripts_unavailable"] += 1
                # Still store source-URL-only metadata so the source is tracked
                await _record_unfetched_youtube(url, category, source_id, proof)
            else:
                proof["errors"].append({"stage": "ingest", "url": url, "msg": err_msg[:200]})
        except Exception as exc:    # noqa: BLE001
            proof["errors"].append({"stage": "ingest_unexpected", "url": url, "msg": str(exc)[:200]})

    graph_after = await _count_graph_edges()
    proof["graph_edges_created"] = max(0, graph_after - graph_before)

    # 4. Optional lesson generation — pick the first real-fetched ingest
    if generate_lesson:
        first_real = next(
            (r for r in proof["ingest_results"]
             if r.get("knowledge_id") and r.get("title")
             and not str(r.get("title", "")).startswith("[transcript unavailable]")),
            None,
        )
        # Fallback: if nothing real-fetched, accept any with a knowledge_id
        if not first_real:
            first_real = next(
                (r for r in proof["ingest_results"] if r.get("knowledge_id")),
                None,
            )
        if first_real:
            try:
                lesson = await _generate_lesson(
                    knowledge_id=first_real["knowledge_id"],
                    source_url=first_real["url"],
                    title=first_real.get("title") or first_real["category"],
                    concepts=first_real.get("concepts") or [],
                    agent=first_real.get("agent") or "minerva",
                )
                proof["lessons_created"].append({
                    "lesson_id": lesson["lesson_id"],
                    "title": lesson["title"],
                    "knowledge_id": first_real["knowledge_id"],
                })
            except Exception as exc:    # noqa: BLE001
                proof["errors"].append({"stage": "lesson", "msg": str(exc)[:200]})

    # 5. Persist run + update source
    await _persist_run(proof, status="ok", started_at=started_at)
    await _watchers().update_one(
        {"id": source_id},
        {"$set": {
            "last_run_at": started_at,
            "last_commit_sha": _hash_first_line(readme_text),
            "status": "ok",
        }, "$inc": {"run_count": 1}},
    )
    return proof


async def get_status(source_id: str) -> Optional[Dict[str, Any]]:
    src = await _watchers().find_one({"id": source_id}, {"_id": 0})
    if not src:
        return None
    last_run = await _runs().find_one(
        {"source_id": source_id}, {"_id": 0}, sort=[("started_at", -1)],
    )
    return {"source": src, "last_run": last_run}


async def get_proof(source_id: str) -> Optional[Dict[str, Any]]:
    return await _runs().find_one(
        {"source_id": source_id}, {"_id": 0}, sort=[("started_at", -1)],
    )


# --- helpers ---------------------------------------------------------------
async def _record_unfetched_youtube(
    url: str, category: str, source_id: str, proof: Dict[str, Any],
) -> None:
    """For YouTube links whose transcripts are unavailable, store a stub
    knowledge entry + memory mirror referencing the source URL only.
    This honours the 'never store copyrighted transcript' rule."""
    try:
        h = hashlib.sha256(url.encode()).hexdigest()
        existing = await _db()["knowledge_records"].find_one(
            {"source_hash": h}, {"_id": 0},
        )
        if existing:
            proof["knowledge_ids"].append(existing.get("id"))
            if existing.get("memory_bank_id"):
                proof["memory_ids"].append(existing["memory_bank_id"])
            return
        kid = uuid4().hex
        title = f"[transcript unavailable] {category} · {url}"
        body = (
            f"YouTube source listed in GitHub watcher under category '{category}'.\n"
            f"Transcript fetch unavailable (cloud-IP block on free YouTube tier).\n"
            f"Source URL retained for citation: {url}\n"
            f"This record stores ONLY the URL + category — no copyrighted text."
        )
        mb_row = await mb.auto_store(
            body, persona="minerva", category="research",
            source_type="youtube",
            tags=["youtube", "watcher:" + source_id[:8],
                  f"category:{_slug(category)}", "transcript_unavailable"],
        )
        mb_id = (mb_row or {}).get("id")
        await _db()["knowledge_records"].insert_one({
            "id": kid,
            "title": title,
            "summary": body,
            "key_points": [],
            "tags": ["youtube", "transcript_unavailable",
                     f"category:{_slug(category)}"],
            "source_type": "youtube",
            "source_url": url,
            "source_hash": h,
            "source_author": None,
            "confidence_score": 0.0,
            "related_agents": ["minerva"],
            "related_projects": [],
            "concepts": [],
            "memory_bank_id": mb_id,
            "transcript_status": "TRANSCRIPT_UNAVAILABLE",
            "reinforce_count": 0,
            "created_at": _utc(),
            "updated_at": _utc(),
        })
        proof["knowledge_ids"].append(kid)
        if mb_id:
            proof["memory_ids"].append(mb_id)
    except Exception as exc:    # noqa: BLE001
        proof["errors"].append({"stage": "record_unfetched_youtube",
                                "url": url, "msg": str(exc)[:200]})


async def _persist_run(proof: Dict[str, Any], *, status: str, started_at: str) -> None:
    proof["ended_at"] = _utc()
    proof["status"] = status
    proof["summary"] = {
        "links_extracted": len(proof["links_extracted"]),
        "ingest_attempts": len(proof["ingest_results"]),
        "knowledge_ids_created_or_reused": len(set(proof["knowledge_ids"])),
        "memory_ids_created_or_reused": len(set(proof["memory_ids"])),
        "graph_edges_created": proof["graph_edges_created"],
        "lessons_created": len(proof["lessons_created"]),
        "transcripts_found": proof["transcripts_found"],
        "transcripts_unavailable": proof["transcripts_unavailable"],
        "errors": len(proof["errors"]),
    }
    await _runs().insert_one(proof.copy())


async def _count_graph_edges() -> int:
    return await _db()["graph_triples"].count_documents({})


def _hash_first_line(text: str) -> str:
    head = (text or "").splitlines()[:1]
    return hashlib.sha256("\n".join(head).encode()).hexdigest()[:12]


def _slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:48] or "x"

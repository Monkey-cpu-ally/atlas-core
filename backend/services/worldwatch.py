"""
World Update Watcher.

A curated, opt-in feed reader for "what changed in the world" across the
ATLAS domains: AI, robotics, software engineering, electronics, batteries,
green tech, manufacturing, design, architecture, medicine, agriculture,
aerospace.

Design honest:
  * Not a general web crawler — it pulls a hand-curated list of public RSS/Atom
    feeds (`WORLDWATCH_FEEDS`) that aren't subject to cloud-IP block.
  * For each new entry: snapshot via `httpx`, distill via existing kbase
    ingestion pipeline, write KB/MB/graph triples, and emit a
    "what changed" note (single sentence + 3 bullets).
  * De-dupes by entry GUID + content hash so a re-run is idempotent.
  * Source list is editable at runtime via the routes layer (not in this
    file) — but the seed is shipped in `worldwatch_feeds.py`.

Collections:
  * worldwatch_feeds   — registered feed sources
  * worldwatch_updates — per-entry update records (the "what changed" trail)
  * worldwatch_runs    — proof-of-execution per run
"""
from __future__ import annotations

import hashlib
import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4
from xml.etree import ElementTree as ET

import httpx
from motor.motor_asyncio import AsyncIOMotorClient

from services import knowledge_ingestion as ki
from services import memory_bank as mb
from services.llm_provider import send as llm_send

logger = logging.getLogger("atlas.worldwatch")

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _feeds():   return _db()["worldwatch_feeds"]
def _updates(): return _db()["worldwatch_updates"]
def _runs():    return _db()["worldwatch_runs"]


def _utc(): return datetime.now(timezone.utc).isoformat()


# --- Curated seed feed list (RSS/Atom only) -------------------------------
# Picked for: public RSS, not cloud-IP blocked, low spam ratio, one per domain.
DOMAINS = [
    "AI", "robotics", "software_engineering", "electronics", "batteries",
    "green_tech", "manufacturing", "design", "architecture", "medicine",
    "agriculture", "aerospace",
]

SEED_FEEDS: List[Dict[str, Any]] = [
    # AI
    {"domain": "AI",
     "url": "https://export.arxiv.org/rss/cs.AI",
     "label": "arXiv cs.AI",
     "agent": "minerva"},
    # robotics
    {"domain": "robotics",
     "url": "https://export.arxiv.org/rss/cs.RO",
     "label": "arXiv cs.RO",
     "agent": "ajani"},
    # software engineering
    {"domain": "software_engineering",
     "url": "https://export.arxiv.org/rss/cs.SE",
     "label": "arXiv cs.SE",
     "agent": "hermes"},
    # electronics
    {"domain": "electronics",
     "url": "https://hackaday.com/feed/",
     "label": "Hackaday",
     "agent": "ajani"},
    # batteries
    {"domain": "batteries",
     "url": "https://export.arxiv.org/rss/cond-mat.mtrl-sci",
     "label": "arXiv cond-mat.mtrl-sci",
     "agent": "minerva"},
    # green tech
    {"domain": "green_tech",
     "url": "https://export.arxiv.org/rss/physics.atm-clus",
     "label": "arXiv physics.atm-clus",
     "agent": "minerva"},
    # manufacturing
    {"domain": "manufacturing",
     "url": "https://export.arxiv.org/rss/cs.RO",
     "label": "arXiv (manufacturing-adjacent)",
     "agent": "ajani"},
    # design (no easy public feed → use Architizer's; fallback ok)
    {"domain": "design",
     "url": "https://www.dezeen.com/feed/",
     "label": "Dezeen",
     "agent": "ajani"},
    # architecture
    {"domain": "architecture",
     "url": "https://www.archdaily.com/feed",
     "label": "ArchDaily",
     "agent": "ajani"},
    # medicine
    {"domain": "medicine",
     "url": "https://export.arxiv.org/rss/q-bio.QM",
     "label": "arXiv q-bio.QM",
     "agent": "minerva"},
    # agriculture
    {"domain": "agriculture",
     "url": "https://export.arxiv.org/rss/q-bio.PE",
     "label": "arXiv q-bio.PE",
     "agent": "minerva"},
    # aerospace
    {"domain": "aerospace",
     "url": "https://www.nasa.gov/feed/",
     "label": "NASA news",
     "agent": "ajani"},

    # ----- Patent feeds (source_type=patent, url is the search query) -----
    {"domain": "AI",
     "url": "patent:large language model agent",
     "label": "Patents · LLM agents",
     "agent": "minerva",
     "source_type": "patent"},
    {"domain": "robotics",
     "url": "patent:humanoid robot manipulation",
     "label": "Patents · humanoid robotics",
     "agent": "ajani",
     "source_type": "patent"},
    {"domain": "batteries",
     "url": "patent:solid-state battery electrolyte",
     "label": "Patents · solid-state batteries",
     "agent": "minerva",
     "source_type": "patent"},
    {"domain": "electronics",
     "url": "patent:neuromorphic chip",
     "label": "Patents · neuromorphic compute",
     "agent": "ajani",
     "source_type": "patent"},
    {"domain": "green_tech",
     "url": "patent:direct air capture sorbent",
     "label": "Patents · carbon capture",
     "agent": "minerva",
     "source_type": "patent"},
    {"domain": "aerospace",
     "url": "patent:electric aircraft propulsion",
     "label": "Patents · electric aviation",
     "agent": "ajani",
     "source_type": "patent"},
]

USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "atlas-worldwatch/2.0")


async def seed_feeds() -> Dict[str, Any]:
    """Idempotent — only inserts feeds not already in the collection."""
    inserted = 0
    skipped = 0
    for f in SEED_FEEDS:
        h = hashlib.sha256(f["url"].encode()).hexdigest()[:24]
        existing = await _feeds().find_one({"source_hash": h})
        if existing:
            skipped += 1
            continue
        await _feeds().insert_one({
            "id": uuid4().hex,
            "source_hash": h,
            "domain": f["domain"],
            "url": f["url"],
            "label": f["label"],
            "agent": f["agent"],
            "source_type": f.get("source_type", "rss"),
            "registered_at": _utc(),
            "last_run_at": None,
            "run_count": 0,
            "approved": True,         # all seed feeds are pre-approved
        })
        inserted += 1
    return {"inserted": inserted, "skipped": skipped, "total_seed": len(SEED_FEEDS)}


async def list_feeds(domain: Optional[str] = None) -> List[Dict[str, Any]]:
    q: Dict[str, Any] = {}
    if domain: q["domain"] = domain.lower()
    cur = _feeds().find(q, {"_id": 0}).sort("registered_at", -1)
    return [d async for d in cur]


async def list_updates(
    domain: Optional[str] = None, limit: int = 100,
) -> List[Dict[str, Any]]:
    q: Dict[str, Any] = {}
    if domain: q["domain"] = domain.lower()
    cur = _updates().find(q, {"_id": 0}).sort("captured_at", -1).limit(limit)
    return [d async for d in cur]


async def status() -> Dict[str, Any]:
    feeds = await list_feeds()
    last_run = await _runs().find_one({}, {"_id": 0}, sort=[("started_at", -1)])
    by_domain: Dict[str, int] = {}
    async for d in _updates().aggregate([
        {"$group": {"_id": "$domain", "count": {"$sum": 1}}},
    ]):
        by_domain[d["_id"] or "?"] = d["count"]
    return {
        "feeds_count": len(feeds),
        "feeds_by_domain": {f["domain"]: f["url"] for f in feeds},
        "updates_total": await _updates().count_documents({}),
        "updates_by_domain": by_domain,
        "last_run": last_run,
        "domains_covered": DOMAINS,
    }


# --- Run the watcher -------------------------------------------------------
async def run(*, max_per_feed: int = 3) -> Dict[str, Any]:
    """Pull each registered feed and ingest the newest N entries.
    Idempotent: entries already in `worldwatch_updates` are skipped."""
    started_at = _utc()
    run_id = uuid4().hex
    proof: Dict[str, Any] = {
        "run_id": run_id, "started_at": started_at,
        "feeds_processed": 0, "entries_seen": 0,
        "entries_new": 0, "errors": [],
        "updates_ids": [],
    }
    feeds = await list_feeds()
    if not feeds:
        await seed_feeds()
        feeds = await list_feeds()

    for f in feeds:
        proof["feeds_processed"] += 1
        src_type = f.get("source_type", "rss")
        try:
            if src_type == "patent":
                entries = await _fetch_patent_entries(f["url"], max_per_feed)
            else:
                entries = await _fetch_feed_entries(f["url"], max_per_feed)
        except Exception as exc:    # noqa: BLE001
            proof["errors"].append({
                "feed_id": f["id"], "url": f["url"], "stage": "fetch",
                "msg": str(exc)[:200],
            })
            continue
        proof["entries_seen"] += len(entries)

        for entry in entries:
            try:
                update = await _ingest_entry(f, entry)
                if update.get("new"):
                    proof["entries_new"] += 1
                    proof["updates_ids"].append(update["id"])
            except Exception as exc:    # noqa: BLE001
                proof["errors"].append({
                    "feed_id": f["id"], "url": entry.get("link"),
                    "stage": "ingest_entry", "msg": str(exc)[:200],
                })

        await _feeds().update_one(
            {"id": f["id"]},
            {"$set": {"last_run_at": _utc()}, "$inc": {"run_count": 1}},
        )

    proof["ended_at"] = _utc()
    proof["status"] = "ok" if not proof["errors"] else "partial"
    await _runs().insert_one(proof.copy())
    return proof


async def _fetch_feed_entries(url: str, n: int) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient(
        timeout=20.0, follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        r = await client.get(url)
        r.raise_for_status()
        xml = r.text

    # Some feeds (Dezeen) ship a BOM/leading whitespace before <?xml; strict
    # ET.fromstring rejects anything before the prolog, so normalise first.
    xml = xml.lstrip("\ufeff").lstrip()

    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise RuntimeError(f"RSS parse: {exc}") from exc

    out: List[Dict[str, Any]] = []
    # RSS 2.0: <rss><channel><item>; Atom: <feed><entry>
    items = root.findall(".//item") or root.findall(
        ".//{http://www.w3.org/2005/Atom}entry"
    )
    for it in items[:n]:
        title = _text(it, "title")
        link = _text(it, "link") or _attr(it, "link", "href")
        desc = _text(it, "description") or _text(it, "summary") or _text(it, "content")
        pub  = _text(it, "pubDate") or _text(it, "published") or _text(it, "updated")
        guid = _text(it, "guid") or link or title
        if not (title and link):
            continue
        out.append({
            "title": title.strip()[:300],
            "link": link.strip(),
            "summary": (desc or "").strip()[:6000],
            "published": (pub or "").strip(),
            "guid": guid.strip(),
        })
    return out


async def _fetch_patent_entries(url_or_query: str, n: int) -> List[Dict[str, Any]]:
    """For source_type=patent feeds the `url` field is `patent:<query>`.
    We re-use `patent_client.search_patents` to discover new filings and
    shape them into the same entry contract used by the RSS path so the
    rest of the ingestion pipeline stays unchanged."""
    from services import patent_client as pc

    query = url_or_query.split("patent:", 1)[-1].strip() if "patent:" in url_or_query else url_or_query
    try:
        results = await pc.search_patents(query, top_n=n)
    except pc.PatentUnreachable as exc:
        raise RuntimeError(f"patents unreachable: {exc}") from exc

    out: List[Dict[str, Any]] = []
    for p in results[:n]:
        if not (p.get("id") and p.get("url")):
            continue
        out.append({
            "title": (p.get("title") or p["id"])[:300],
            "link": p["url"],
            "summary": (
                f"Patent {p['id']}"
                + (f" · assignee: {p.get('assignee')}" if p.get("assignee") else "")
                + (f" · filed: {p.get('filed')}" if p.get("filed") else "")
                + "\n\n"
                + (p.get("abstract") or "")
            )[:6000],
            "published": p.get("filed", ""),
            "guid": p["id"],
        })
    return out


async def _ingest_entry(feed: Dict[str, Any], entry: Dict[str, Any]) -> Dict[str, Any]:
    """De-dupe by guid+content hash. New entries get a 'what changed' note +
    a KB/MB/graph triple-write."""
    h = hashlib.sha256(
        f"{entry['guid']}|{entry['link']}".encode(),
    ).hexdigest()[:24]
    existing = await _updates().find_one({"entry_hash": h}, {"_id": 0})
    if existing:
        return {"id": existing["id"], "new": False}

    note = await _what_changed_note(entry, feed["domain"])

    upd_id = uuid4().hex
    # Try the existing kbase pipeline for the underlying link
    kb_id: Optional[str] = None
    mb_id: Optional[str] = None
    try:
        result = await ki.ingest_url(
            entry["link"],
            extra_tags=[
                "worldwatch", f"domain:{feed['domain']}",
                f"agent:{feed['agent']}", f"feed:{feed['label'][:32]}",
            ],
        )
        kb_id = (result.get("record") or {}).get("id")
        mb_id = result.get("memory_bank_id")
    except Exception as exc:    # noqa: BLE001
        logger.warning("kbase ingest skipped for %s: %s", entry['link'], exc)
        # Still create a MB row directly from the feed entry's own text
        try:
            body = (
                f"WORLDWATCH · {feed['domain']} · {entry['title']}\n"
                f"SOURCE: {entry['link']}\n"
                f"PUBLISHED: {entry['published']}\n"
                f"SUMMARY:\n{(entry['summary'] or '')[:2000]}"
            )
            mb_row = await mb.auto_store(
                body, persona=feed["agent"], category="research",
                source_type="worldwatch",
                tags=["worldwatch", f"domain:{feed['domain']}",
                      f"agent:{feed['agent']}"],
            )
            mb_id = (mb_row or {}).get("id")
        except Exception as exc2:    # noqa: BLE001
            logger.warning("MB fallback failed: %s", exc2)

    # Graph triple wiring (domain ↔ agent, domain ↔ source)
    try:
        await mb.add_triple(
            from_node=f"agent:{feed['agent']}",
            to_node=f"domain:{feed['domain']}",
            relation="watches",
            source_id=upd_id, weight=1.0,
        )
        await mb.add_triple(
            from_node=f"domain:{feed['domain']}",
            to_node=feed["label"],
            relation="sourced_from",
            source_id=upd_id, weight=1.0,
        )
    except Exception as exc:    # noqa: BLE001
        logger.warning("graph wiring failed: %s", exc)

    doc = {
        "id": upd_id,
        "entry_hash": h,
        "domain": feed["domain"],
        "agent": feed["agent"],
        "feed_label": feed["label"],
        "feed_id": feed["id"],
        "source_type": feed.get("source_type", "rss"),
        "title": entry["title"],
        "url": entry["link"],
        "published": entry["published"],
        "summary_excerpt": (entry["summary"] or "")[:600],
        "what_changed": note,
        "knowledge_id": kb_id,
        "memory_bank_id": mb_id,
        "captured_at": _utc(),
    }
    await _updates().insert_one(doc)
    return {"id": upd_id, "new": True}


async def _what_changed_note(entry: Dict[str, Any], domain: str) -> Dict[str, Any]:
    """LLM-generated single-sentence 'what changed' + 3 bullets.
    Falls back gracefully if LLM fails."""
    sys = (
        "You read tech/science news. Reply with STRICT JSON only:\n"
        '{"one_line": str, "bullets": [str, str, str], "novelty": "incremental"|"notable"|"breakthrough"}'
    )
    user = (
        f"DOMAIN: {domain}\nTITLE: {entry['title']}\n"
        f"SUMMARY:\n{(entry['summary'] or '')[:1800]}\n\n"
        "Tell me what actually changed (not generic claims)."
    )
    try:
        resp = await llm_send("minerva", sys, user)
        raw = (resp.get("text") or "").strip()
        import json as _j, re as _re
        m = _re.search(r"\{.*\}", raw, _re.DOTALL)
        if m:
            return _j.loads(m.group(0))
    except Exception as exc:    # noqa: BLE001
        logger.warning("what-changed LLM failed: %s", exc)
    return {
        "one_line": entry["title"][:200],
        "bullets": [(entry["summary"] or "")[:120], "(LLM unavailable)", ""],
        "novelty": "incremental",
    }


# --- helpers --------------------------------------------------------------
def _text(el: ET.Element, tag: str) -> Optional[str]:
    # Try plain tag first
    child = el.find(tag)
    if child is not None and (child.text or "").strip():
        return child.text
    # Try Atom namespace
    child = el.find("{http://www.w3.org/2005/Atom}" + tag)
    if child is not None and (child.text or "").strip():
        return child.text
    return None


def _attr(el: ET.Element, tag: str, attr: str) -> Optional[str]:
    child = el.find(tag) or el.find("{http://www.w3.org/2005/Atom}" + tag)
    if child is not None:
        return child.get(attr)
    return None

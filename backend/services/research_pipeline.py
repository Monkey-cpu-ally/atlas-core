"""
Research pipeline orchestrator — Phase 3.

Wires the three research surfaces (web / pdf / patent) into:
  1. a fetch step (web_scraper / pdf_reader / patent_client)
  2. an optional LLM summary step (via the Phase-1 llm_provider)
  3. a persistence step into the Phase-2 Memory Bank with category='research'

All operations are async and never raise on memory failures (memory writes
are fire-and-forget via memory_bank.auto_store).
"""
import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4

from services import memory_bank as mb
from services.llm_provider import send as llm_send
from services.web_scraper import (
    ResearchUnreachable,
    fetch_page,
    search_web,
)
from services.pdf_reader import chunk_text, extract_pdf_text
from services.patent_client import (
    PatentUnreachable,
    fetch_patent_detail,
    search_patents,
)

logger = logging.getLogger("atlas.research_pipeline")

# Hermes is the pattern-hunter persona — best fit for distilling research.
RESEARCH_PERSONA = "hermes"
SUMMARISER_SYSTEM = (
    "You are Hermes, Maasai pattern hunter. You distil research material "
    "into 3-5 short paragraphs: (1) what this source is actually claiming, "
    "(2) what evidence it offers, (3) which assumptions deserve scrutiny, "
    "(4) one concrete connection to ongoing atlas work."
)
ENGINEER_SYSTEM = (
    "You are Ajani, Zulu warrior-engineer. Given a patent, write 2-3 short "
    "paragraphs on (a) what the patent actually builds, (b) the physics or "
    "mechanism, (c) build feasibility and risks in plain language."
)


async def _summarise(text: str, *, persona_system: str, persona: str) -> str:
    """One-shot LLM summary. Returns empty string on any failure so the
    pipeline can still persist the raw scrape into memory."""
    if not text.strip():
        return ""
    try:
        result = await llm_send(
            persona,
            persona_system,
            f"Source material:\n\n{text[:6000]}\n\nWrite the distilled summary now.",
            session_id=f"research-{persona}-{uuid4().hex[:12]}",
        )
        return (result.get("text") or "").strip()
    except Exception as exc:    # noqa: BLE001
        logger.warning("research summary failed (%s): %s", persona, exc)
        return ""


# ---------------------------------------------------------------------------
# Web research
# ---------------------------------------------------------------------------
async def research_web(query: str, top_n: int = 5, summarise: bool = True) -> Dict[str, Any]:
    """Search the web, fetch each top result, distil via Hermes, store in
    research memory. Returns the full payload for the HUD."""
    try:
        hits = await search_web(query, top_n=top_n)
    except ResearchUnreachable as exc:
        raise ResearchUnreachable(str(exc)) from exc

    sources: List[Dict[str, Any]] = []
    for hit in hits:
        try:
            page = await fetch_page(hit["url"])
        except ResearchUnreachable as exc:
            logger.info("skip %s: %s", hit["url"], exc)
            sources.append({**hit, "text": "", "skipped": str(exc)})
            continue
        summary = ""
        if summarise:
            summary = await _summarise(
                page["text"], persona_system=SUMMARISER_SYSTEM, persona=RESEARCH_PERSONA,
            )
        record = {
            **hit,
            "host": page["host"],
            "title": page["title"] or hit["title"],
            "text": page["text"],
            "word_count": page["word_count"],
            "summary": summary,
            "fetched_at": page["fetched_at"],
        }
        sources.append(record)
        body = (
            f"WEB · {record['title']}\n"
            f"URL: {record['url']}\n"
            f"Snippet: {record.get('snippet', '')}\n\n"
            f"{summary or record['text'][:2000]}"
        )
        await mb.auto_store(
            body,
            persona=RESEARCH_PERSONA,
            category="research",
            source_type="web",
            tags=[query[:80]],
        )
    return {
        "kind": "web",
        "query": query,
        "count": len(sources),
        "sources": sources,
    }


# ---------------------------------------------------------------------------
# PDF research
# ---------------------------------------------------------------------------
async def research_pdf(blob: bytes, filename: str, summarise: bool = True) -> Dict[str, Any]:
    """Read a PDF, chunk it, summarise via Hermes, store every chunk into
    research memory (each chunk gets its own row → granular recall)."""
    result = extract_pdf_text(blob)
    full = result["full_text"]
    chunks = chunk_text(full, max_chars=1800, overlap=200)
    summary = ""
    if summarise and full:
        summary = await _summarise(
            full, persona_system=SUMMARISER_SYSTEM, persona=RESEARCH_PERSONA,
        )

    # Persist a top-level memory + one per chunk for granular recall.
    top_body = (
        f"PDF · {filename}\n"
        f"Pages: {result['page_count']} · Words: {sum(p['word_count'] for p in result['pages'])}\n\n"
        f"{summary or full[:2000]}"
    )
    parent_id = (await mb.auto_store(
        top_body,
        persona=RESEARCH_PERSONA,
        category="research",
        source_type="pdf",
        tags=[filename[:80]],
    ) or {}).get("id")

    for i, ch in enumerate(chunks):
        await mb.auto_store(
            f"PDF-CHUNK [{filename} · part {i+1}/{len(chunks)}]\n\n{ch}",
            persona=RESEARCH_PERSONA,
            category="research",
            source_type="pdf",
            source_id=parent_id,
            tags=[filename[:80], f"chunk{i+1}"],
        )
    return {
        "kind": "pdf",
        "filename": filename,
        "page_count": result["page_count"],
        "extracted_pages": result["extracted_pages"],
        "chunk_count": len(chunks),
        "metadata": result["metadata"],
        "summary": summary,
        "parent_memory_id": parent_id,
    }


# ---------------------------------------------------------------------------
# Patent research
# ---------------------------------------------------------------------------
async def research_patents(query: str, top_n: int = 5, deep: bool = False) -> Dict[str, Any]:
    """Search Google Patents, optionally pull each detail page through Ajani's
    engineering critic, store both into research memory."""
    hits = await search_patents(query, top_n=top_n)
    patents: List[Dict[str, Any]] = []
    for hit in hits:
        record: Dict[str, Any] = dict(hit)
        if deep and hit.get("id"):
            try:
                detail = await fetch_patent_detail(hit["id"])
                record.update(detail)
                record["engineer_take"] = await _summarise(
                    f"TITLE: {detail['title']}\n\nABSTRACT: {detail['abstract']}\n\n"
                    f"CLAIMS:\n{detail['claims'][:3000]}",
                    persona_system=ENGINEER_SYSTEM,
                    persona="ajani",
                )
            except (PatentUnreachable, ValueError) as exc:
                record["error"] = str(exc)
        body = (
            f"PATENT · {record.get('id', '?')} · {record.get('title', '')}\n"
            f"Assignee: {record.get('assignee', '')}\n"
            f"URL: {record.get('url', '')}\n\n"
            f"{record.get('abstract', '')}\n\n"
            f"{record.get('engineer_take', '')}"
        ).strip()
        await mb.auto_store(
            body,
            persona="ajani" if deep else RESEARCH_PERSONA,
            category="research",
            source_type="patent",
            source_id=record.get("id"),
            tags=[query[:80]],
        )
        patents.append(record)
    return {
        "kind": "patent",
        "query": query,
        "count": len(patents),
        "deep": deep,
        "patents": patents,
    }

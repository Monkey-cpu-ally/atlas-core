"""ATLAS public-domain book ingestion and vector-memory retrieval.

This service completes the Project Gutenberg -> Memory Bank loop:
  search -> select -> download permitted plain text -> strip boilerplate ->
  chunk -> embed/store for Ajani, Minerva, Hermes -> semantic recall.

The same book text is not committed to Git. It is stored at runtime in the
existing Mongo-backed Memory Bank with embeddings and provenance metadata.
"""
from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional, Tuple

import httpx
from motor.motor_asyncio import AsyncIOMotorClient

from services import memory_bank as mb
from services.project_gutenberg_connector import DEFAULT_USER_AGENT, search_books

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
MAX_BOOK_BYTES = int(os.environ.get("ATLAS_BOOK_MAX_BYTES", str(8 * 1024 * 1024)))
DEFAULT_PERSONAS = ("ajani", "minerva", "hermes")
_client: Optional[AsyncIOMotorClient] = None

_START_RE = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.I | re.S)
_END_RE = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK.*?\*\*\*", re.I | re.S)


def _memory_collection():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]["memory_bank"]


def gutenberg_numeric_id(book: Dict[str, Any]) -> str:
    raw = str(book.get("id") or "").rstrip("/")
    tail = raw.rsplit("/", 1)[-1]
    return tail if tail.isdigit() else raw


def select_book(rows: List[Dict[str, Any]], book_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if not rows:
        return None
    wanted = (book_id or "").strip()
    if not wanted:
        return rows[0]
    for row in rows:
        if gutenberg_numeric_id(row) == wanted or str(row.get("id") or "") == wanted:
            return row
    return None


def strip_gutenberg_boilerplate(text: str) -> str:
    """Keep the ebook body while removing standard Gutenberg wrapper text."""
    value = (text or "").replace("\r\n", "\n").replace("\r", "\n")
    start = _START_RE.search(value)
    if start:
        value = value[start.end():]
    end = _END_RE.search(value)
    if end:
        value = value[:end.start()]
    value = re.sub(r"\n{4,}", "\n\n\n", value)
    return value.strip()


def chunk_book(text: str, *, max_chars: int = 3600, overlap: int = 300) -> List[str]:
    """Paragraph-aware overlapping chunks suitable for memory embeddings."""
    clean = (text or "").strip()
    if not clean:
        return []
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", clean) if p.strip()]
    chunks: List[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
            prefix = current[-overlap:] if overlap else ""
            current = f"{prefix}\n\n{paragraph}".strip()
        else:
            start = 0
            step = max(1, max_chars - overlap)
            while start < len(paragraph):
                chunks.append(paragraph[start:start + max_chars])
                start += step
            current = ""
    if current:
        chunks.append(current)
    return chunks


async def fetch_plain_text(url: str, *, timeout: float = 45.0) -> str:
    headers = {
        "User-Agent": os.getenv("ATLAS_GUTENBERG_USER_AGENT", DEFAULT_USER_AGENT),
        "Accept": "text/plain, text/plain; charset=utf-8;q=0.9, */*;q=0.1",
    }
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        if len(response.content) > MAX_BOOK_BYTES:
            raise ValueError(f"book exceeds ATLAS_BOOK_MAX_BYTES ({MAX_BOOK_BYTES})")
    return strip_gutenberg_boilerplate(response.text)


async def ingest_gutenberg_book(
    query: str,
    *,
    book_id: Optional[str] = None,
    subjects: Optional[List[str]] = None,
    personas: Optional[List[str]] = None,
) -> Dict[str, Any]:
    rows = await search_books(query)
    book = select_book(rows, book_id)
    if not book:
        raise ValueError("Project Gutenberg book not found in search results")
    links = book.get("links") or {}
    text_url = links.get("text")
    if not text_url:
        raise ValueError("selected Gutenberg record does not expose a plain-text acquisition link")

    text = await fetch_plain_text(str(text_url))
    chunks = chunk_book(text)
    if not chunks:
        raise ValueError("selected Gutenberg book produced no readable text chunks")

    gid = gutenberg_numeric_id(book)
    title = str(book.get("title") or "Untitled")
    authors = [str(a) for a in (book.get("authors") or [])]
    author_line = ", ".join(authors) or "Unknown author"
    catalog_url = str(links.get("catalog") or book.get("id") or "")
    subject_tags = [s.strip() for s in (subjects or []) if s and s.strip()]
    target_personas = [p.lower() for p in (personas or list(DEFAULT_PERSONAS)) if p.lower() in DEFAULT_PERSONAS]
    if not target_personas:
        target_personas = list(DEFAULT_PERSONAS)

    stored = 0
    reused = 0
    memory_ids: List[str] = []
    for persona in target_personas:
        for index, chunk in enumerate(chunks, start=1):
            source_id = f"gutenberg:{gid}:{persona}:{index}"
            existing = await _memory_collection().find_one({"source_id": source_id}, {"_id": 0, "id": 1})
            if existing:
                reused += 1
                if existing.get("id"):
                    memory_ids.append(existing["id"])
                continue
            body = (
                f"BOOK · {title}\n"
                f"Author: {author_line}\n"
                f"Project Gutenberg ID: {gid}\n"
                f"Source: {catalog_url}\n"
                f"Part: {index}/{len(chunks)}\n\n"
                f"{chunk}"
            )
            row = await mb.store_memory(
                body,
                persona=persona,
                category="research",
                source_type="book",
                source_id=source_id,
                tags=["book", "project-gutenberg", f"gutenberg:{gid}", title[:80], *subject_tags],
                pinned=False,
            )
            stored += 1
            if row.get("id"):
                memory_ids.append(row["id"])

    return {
        "provider": "Project Gutenberg",
        "book": {
            "id": gid,
            "title": title,
            "authors": authors,
            "catalog_url": catalog_url,
            "text_url": text_url,
            "language": book.get("language"),
        },
        "chunk_count": len(chunks),
        "personas": target_personas,
        "stored": stored,
        "reused": reused,
        "memory_ids": memory_ids,
        "vector_memory": True,
        "storage": "Mongo Memory Bank; ebook bytes are not committed to Git",
    }


async def search_book_memory(query: str, *, persona: str, top_k: int = 6) -> List[Dict[str, Any]]:
    """Semantic recall over only ingested book chunks for one ATLAS persona."""
    persona_key = persona.lower()
    if persona_key not in DEFAULT_PERSONAS:
        raise ValueError("persona must be ajani, minerva, or hermes")

    qvec, _ = await mb.embed(query, persona=persona_key)
    cursor = _memory_collection().find(
        {"persona": persona_key, "source_type": "book"},
        {"_id": 0},
    )
    rows = await cursor.to_list(length=5000)
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for row in rows:
        embedding = row.pop("embedding", None) or []
        score = mb._cosine(qvec, embedding)  # shared vector math from Memory Bank
        if score <= 0:
            continue
        row["sim"] = round(score, 4)
        row["score"] = round(score, 4)
        scored.append((score, row))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [row for _, row in scored[:top_k]]

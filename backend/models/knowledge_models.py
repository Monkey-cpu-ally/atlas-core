"""
Knowledge Ingestion — distilled record schemas.

Unlike Phase-1 raw `knowledge` rows (full transcripts) or Phase-2 generic
`memory_bank` rows (free text), a KnowledgeRecord is a STRUCTURED distillation
of a single source. The original source text is NOT stored verbatim — only
its title, author, URL, the architect-routed agent's summary + key_points,
plus the concept tags used to build graph triples.

Dedup: a row is keyed by `source_hash = sha256(normalised_url)`. Re-ingest
the same URL → update + reinforce, never duplicate.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SourceType(str, Enum):
    GITHUB        = "github"
    YOUTUBE       = "youtube"
    PDF           = "pdf"
    WEB           = "web"
    PATENT        = "patent"
    ACADEMIC      = "academic"     # arxiv + generic paper URLs


class IngestRequest(BaseModel):
    url: HttpUrl
    project_id: Optional[str] = None
    force_agent: Optional[str] = None      # 'ajani'|'minerva'|'hermes'|'council'
    extra_tags: List[str] = Field(default_factory=list)
    # PDF only — when the source IS a PDF the architect already has bytes for.
    pdf_blob: Optional[str] = None          # base64
    pdf_filename: Optional[str] = None


class FetchedSource(BaseModel):
    """Raw payload from a source fetcher — used internally, never stored."""
    source_type: SourceType
    source_url: str
    title: Optional[str] = None
    author: Optional[str] = None
    text: str = ""
    extra: Dict[str, Any] = Field(default_factory=dict)


class Distillation(BaseModel):
    """LLM output — what the persona learned from the source."""
    title: str
    summary: str
    key_points: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    concepts: List[str] = Field(default_factory=list)
    confidence_score: float = 0.6
    suggested_agent: str = "council"


class KnowledgeRecord(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    title: str
    summary: str
    key_points: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    source_type: SourceType
    source_url: str
    source_hash: str                                # sha256 of normalised URL
    source_author: Optional[str] = None
    confidence_score: float = 0.6
    related_agents: List[str] = Field(default_factory=list)   # 1+ of ajani/minerva/hermes/council
    related_projects: List[str] = Field(default_factory=list)
    concepts: List[str] = Field(default_factory=list)         # for graph wiring
    memory_bank_id: Optional[str] = None                       # back-pointer to the Phase-2 mb row
    reinforce_count: int = 0
    created_at: str = Field(default_factory=_utc_now)
    updated_at: str = Field(default_factory=_utc_now)


# --- Helpers ---------------------------------------------------------------
def normalise_url(url: str) -> str:
    """Lower-case host + strip trailing slash + drop fragment so equivalent
    URLs hash to the same `source_hash`."""
    from urllib.parse import urlparse, urlunparse
    p = urlparse(str(url).strip())
    netloc = (p.netloc or "").lower()
    # strip default www. prefix
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = (p.path or "/").rstrip("/") or "/"
    return urlunparse((p.scheme.lower() or "https", netloc, path, "", p.query, ""))


def url_hash(url: str) -> str:
    return hashlib.sha256(normalise_url(url).encode("utf-8")).hexdigest()

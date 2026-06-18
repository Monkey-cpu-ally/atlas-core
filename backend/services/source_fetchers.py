"""
Source fetchers — Phase Knowledge Ingestion.

A SINGLE entry point `fetch(url, ...)` that picks the right fetcher
based on the URL host and returns a normalised `FetchedSource`.

Supported source types:
  * github      — fetches the public README via api.github.com (no auth needed for public repos)
  * youtube     — pulls transcript via youtube_transcript_api (Phase 1 dep)
  * pdf         — caller passes bytes (base64 in the IngestRequest); we use Phase-3 pdf_reader
  * patent      — Phase-3 patent_client.fetch_patent_detail
  * academic    — arxiv abstract page via Phase-3 web_scraper.fetch_page (or generic web)
  * web         — Phase-3 web_scraper.fetch_page

None of these store full text in persistence — that happens only via the
Distillation step downstream.
"""
import base64
import logging
import re
from typing import Optional
from urllib.parse import urlparse

import httpx
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

from models.knowledge_models import FetchedSource, SourceType
from services.web_scraper import ResearchUnreachable, fetch_page
from services.patent_client import PatentUnreachable, fetch_patent_detail
from services.pdf_reader import extract_pdf_text

logger = logging.getLogger("atlas.source_fetchers")

_GH_README_API = "https://api.github.com/repos/{owner}/{repo}/readme"


class IngestError(Exception): pass    # noqa: E701


# --- URL classification -----------------------------------------------------
def classify(url: str) -> SourceType:
    host = (urlparse(url).hostname or "").lower()
    path = (urlparse(url).path or "").lower()
    if "github.com" in host:
        return SourceType.GITHUB
    if any(h in host for h in ("youtube.com", "youtu.be")):
        return SourceType.YOUTUBE
    if path.endswith(".pdf"):
        return SourceType.PDF
    if "patents.google.com" in host or "uspto.gov" in host:
        return SourceType.PATENT
    if "arxiv.org" in host or "nature.com" in host or "sciencedirect.com" in host:
        return SourceType.ACADEMIC
    return SourceType.WEB


# --- Top-level dispatcher ---------------------------------------------------
async def fetch(
    url: str, *, pdf_blob_b64: Optional[str] = None, pdf_filename: Optional[str] = None,
) -> FetchedSource:
    """Pick the right fetcher and return a FetchedSource. Raises IngestError
    on hard failures so the route layer can surface 503/404 cleanly."""
    kind = classify(url)
    try:
        if kind == SourceType.GITHUB:
            return await _fetch_github(url)
        if kind == SourceType.YOUTUBE:
            return _fetch_youtube(url)
        if kind == SourceType.PDF:
            return await _fetch_pdf(url, pdf_blob_b64, pdf_filename)
        if kind == SourceType.PATENT:
            return await _fetch_patent(url)
        if kind == SourceType.ACADEMIC:
            return await _fetch_academic(url)
        return await _fetch_web(url)
    except (ResearchUnreachable, PatentUnreachable) as exc:
        raise IngestError(str(exc)) from exc


# --- GitHub -----------------------------------------------------------------
_GH_PATH_RE = re.compile(r"^/([^/]+)/([^/]+)")


async def _fetch_github(url: str) -> FetchedSource:
    m = _GH_PATH_RE.match(urlparse(url).path)
    if not m:
        raise IngestError(f"unrecognised github url: {url}")
    owner, repo = m.group(1), m.group(2).removesuffix(".git")
    api_url = _GH_README_API.format(owner=owner, repo=repo)
    headers = {
        "Accept": "application/vnd.github.raw+json",
        "User-Agent": "atlas-knowledge-ingestion/1.0",
    }
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as cli:
        r = await cli.get(api_url, headers=headers)
        if r.status_code == 404:
            raise IngestError(f"github repo not found: {owner}/{repo}")
        if r.status_code == 403:
            raise IngestError("github API rate-limit; retry later or provide a token")
        r.raise_for_status()
    return FetchedSource(
        source_type=SourceType.GITHUB,
        source_url=url,
        title=f"{owner}/{repo}",
        author=owner,
        text=r.text[:60000],          # cap; the distiller only needs a few thousand chars
        extra={"owner": owner, "repo": repo, "fetched": "readme"},
    )


# --- YouTube ----------------------------------------------------------------
_YT_VIDEO_ID_RE = re.compile(
    r"(?:v=|/embed/|/v/|youtu\.be/|/shorts/)([0-9A-Za-z_-]{11})"
)


def _yt_video_id(url: str) -> Optional[str]:
    m = _YT_VIDEO_ID_RE.search(url)
    return m.group(1) if m else None


def _fetch_youtube(url: str) -> FetchedSource:
    vid = _yt_video_id(url)
    if not vid:
        raise IngestError(f"could not extract YouTube video id from {url}")
    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(vid, languages=["en", "en-US", "en-GB"])
        # fetched is a FetchedTranscript with `.snippets` (each has .text/.start/.duration)
        snippets = list(getattr(fetched, "snippets", fetched))
        segments = [
            {"text": getattr(s, "text", "") if not isinstance(s, dict) else s.get("text", "")}
            for s in snippets
        ]
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as exc:
        raise IngestError(f"YouTube transcript unavailable: {exc}") from exc
    except Exception as exc:    # noqa: BLE001 — yt-api can raise RequestBlocked etc
        # Cloud-IP block is common; surface a clean, actionable message.
        msg = str(exc)
        if "RequestBlocked" in type(exc).__name__ or "blocked" in msg.lower():
            raise IngestError(
                "YouTube is blocking this server's IP (cloud provider). "
                "Use a residential IP or proxy to enable YouTube ingestion."
            ) from exc
        raise IngestError(f"YouTube transcript fetch failed: {exc}") from exc
    transcript = " ".join(seg.get("text", "") for seg in segments)
    return FetchedSource(
        source_type=SourceType.YOUTUBE,
        source_url=url,
        title=f"YouTube video {vid}",
        author=None,
        text=transcript[:30000],
        extra={"video_id": vid, "segments": len(segments)},
    )


# --- PDF --------------------------------------------------------------------
async def _fetch_pdf(
    url: str, blob_b64: Optional[str], filename: Optional[str],
) -> FetchedSource:
    if blob_b64:
        try:
            blob = base64.b64decode(blob_b64)
        except Exception as exc:    # noqa: BLE001
            raise IngestError(f"invalid base64 pdf blob: {exc}") from exc
        title = filename or "uploaded.pdf"
    else:
        # Download remote PDF.
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as cli:
            try:
                r = await cli.get(url, headers={"User-Agent": "atlas-knowledge/1.0"})
                r.raise_for_status()
            except httpx.HTTPError as exc:
                raise IngestError(f"PDF download failed: {exc}") from exc
        if "pdf" not in r.headers.get("content-type", "").lower():
            raise IngestError("URL did not return application/pdf")
        blob = r.content
        title = url.rsplit("/", 1)[-1] or "remote.pdf"
    try:
        result = extract_pdf_text(blob)
    except ValueError as exc:
        raise IngestError(str(exc)) from exc
    return FetchedSource(
        source_type=SourceType.PDF,
        source_url=url,
        title=(result.get("metadata") or {}).get("title") or title,
        author=(result.get("metadata") or {}).get("author") or None,
        text=result["full_text"][:30000],
        extra={"pages": result["page_count"]},
    )


# --- Patent -----------------------------------------------------------------
_PATENT_ID_RE = re.compile(r"/patent/([A-Z0-9\-/]{4,40})", re.IGNORECASE)


async def _fetch_patent(url: str) -> FetchedSource:
    m = _PATENT_ID_RE.search(url)
    if not m:
        raise IngestError(f"could not extract patent id from {url}")
    detail = await fetch_patent_detail(m.group(1))
    text = (
        f"{detail.get('title', '')}\n\n"
        f"ABSTRACT:\n{detail.get('abstract', '')}\n\n"
        f"CLAIMS:\n{detail.get('claims', '')[:4000]}"
    )
    return FetchedSource(
        source_type=SourceType.PATENT,
        source_url=url,
        title=detail.get("title") or m.group(1),
        author=None,
        text=text[:30000],
        extra={"patent_id": detail.get("id")},
    )


# --- Academic (arxiv etc) ---------------------------------------------------
# ---------------------------------------------------------------------------
# arXiv — Phase 8d
# arXiv's free Atom-XML API (no key required): http://export.arxiv.org/api/query
# Accept either an abstract URL (https://arxiv.org/abs/<id>) or the bare id.
# ---------------------------------------------------------------------------
_ARXIV_ID_RE = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?")
_ARXIV_OLD_ID_RE = re.compile(r"([a-z\-]+/\d{7})(v\d+)?", re.IGNORECASE)


def _extract_arxiv_id(url: str) -> Optional[str]:
    m = _ARXIV_ID_RE.search(url) or _ARXIV_OLD_ID_RE.search(url)
    return (m.group(1) + (m.group(2) or "")) if m else None


def _parse_arxiv_entry(xml_text: str) -> dict:
    """Minimal Atom parser — pulls title, authors, summary from the first
    <entry>. We avoid feedparser (extra dep) and do a lightweight regex
    pass; arXiv's Atom is well-formed and stable."""
    def _grab(tag: str) -> str:
        m = re.search(
            rf"<{tag}[^>]*>(.*?)</{tag}>", xml_text, re.DOTALL | re.IGNORECASE,
        )
        return (m.group(1) if m else "").strip()

    # multiple <author><name>… in feedparser-friendly order
    authors = re.findall(
        r"<author>\s*<name>(.*?)</name>", xml_text, re.DOTALL | re.IGNORECASE,
    )
    return {
        "title": re.sub(r"\s+", " ", _grab("title")).strip(),
        "summary": re.sub(r"\s+", " ", _grab("summary")).strip(),
        "authors": [a.strip() for a in authors if a.strip()],
        "published": _grab("published"),
        "updated": _grab("updated"),
    }


async def _fetch_arxiv(url: str) -> FetchedSource:
    arxiv_id = _extract_arxiv_id(url)
    if not arxiv_id:
        # Not actually arXiv — fall back to generic academic page scrape.
        return await _fetch_academic_generic(url)
    api = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    try:
        async with httpx.AsyncClient(
            timeout=15.0, follow_redirects=True,
            headers={"User-Agent": "ATLAS/1.0 (arXiv fetcher)"},
        ) as client:
            resp = await client.get(api)
            resp.raise_for_status()
            entry = _parse_arxiv_entry(resp.text)
    except Exception as exc:    # noqa: BLE001
        logger.warning("arXiv fetch failed for %s (%s) — falling back to web scrape",
                       arxiv_id, exc)
        return await _fetch_academic_generic(url)

    title = entry["title"] or f"arXiv:{arxiv_id}"
    summary = entry["summary"]
    authors = entry["authors"]
    author_line = (", ".join(authors[:6]) + (" et al." if len(authors) > 6 else "")) or None

    # The text we hand to the distiller: title + abstract + authors. The
    # distiller does anti-copyright rewriting, so passing arXiv's verbatim
    # abstract is safe — it never lands in persistence raw.
    text_body = (
        f"# {title}\n\n"
        f"AUTHORS: {author_line or 'unknown'}\n"
        f"ARXIV ID: {arxiv_id}\n"
        f"PUBLISHED: {entry.get('published')}\n\n"
        f"ABSTRACT:\n{summary}\n"
    )
    return FetchedSource(
        source_type=SourceType.ACADEMIC,
        source_url=f"https://arxiv.org/abs/{arxiv_id}",
        title=title[:240],
        author=author_line,
        text=text_body,
        extra={
            "arxiv_id": arxiv_id,
            "authors": authors,
            "published": entry.get("published"),
            "updated": entry.get("updated"),
        },
    )


async def _fetch_academic_generic(url: str) -> FetchedSource:
    """Original generic page-scrape path. Used for non-arXiv academic hosts
    (nature.com, sciencedirect.com, etc.) and as the arXiv fallback."""
    src = await fetch_page(url)
    return FetchedSource(
        source_type=SourceType.ACADEMIC,
        source_url=url,
        title=src.get("title"),
        author=None,
        text=src.get("text") or "",
        extra={"host": src.get("host"), "word_count": src.get("word_count")},
    )


async def _fetch_academic(url: str) -> FetchedSource:
    """Academic dispatcher — arXiv gets its own structured fetcher;
    everything else falls back to the generic page scrape."""
    host = (urlparse(url).hostname or "").lower()
    if "arxiv.org" in host:
        return await _fetch_arxiv(url)
    return await _fetch_academic_generic(url)


# --- Generic web ------------------------------------------------------------
async def _fetch_web(url: str) -> FetchedSource:
    src = await fetch_page(url)
    return FetchedSource(
        source_type=SourceType.WEB,
        source_url=url,
        title=src.get("title"),
        author=None,
        text=src.get("text") or "",
        extra={"host": src.get("host"), "word_count": src.get("word_count")},
    )

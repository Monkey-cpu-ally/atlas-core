"""Archive engine — scan / classify / summarize / route uploaded knowledge.

Accepts PDFs and ZIP files. For PDFs we extract text via pypdf (no external
service). For ZIPs we recursively process every supported file inside. Each
extracted document is:

  1) classified by topic (which core should own this knowledge?)
  2) summarized at SEED + SHADOWS depth (teaching engine vocabulary)
  3) returned as a structured ArchiveEntry

The caller is responsible for persistence — this module is pure scan logic.
"""
from __future__ import annotations

import io
import os
import re
import zipfile
from dataclasses import dataclass, asdict
from typing import List, Optional

from pypdf import PdfReader

from ..cores import get_core
from ..shield_core.shield import sanitize_text


SUPPORTED_EXTS = (".pdf", ".txt", ".md")


@dataclass
class ArchiveEntry:
    filename: str
    bytes_size: int
    page_count: Optional[int]
    extracted_chars: int
    classified_core: str          # ajani / minerva / hermes
    domain: str                   # short label
    summary: str
    open_questions: List[str]
    excerpt: str                  # first ~600 chars after sanitization


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def _extract_pdf(data: bytes) -> tuple[str, int]:
    """Return (text, page_count)."""
    reader = PdfReader(io.BytesIO(data))
    pages: List[str] = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")
    return "\n".join(pages), len(reader.pages)


def _extract_text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def _extract_one(name: str, data: bytes) -> tuple[str, Optional[int]]:
    """Dispatch by extension. Returns (text, page_count_or_None)."""
    lower = name.lower()
    if lower.endswith(".pdf"):
        return _extract_pdf(data)
    if lower.endswith((".txt", ".md")):
        return _extract_text(data), None
    raise ValueError(f"Unsupported file type: {name}")


# ---------------------------------------------------------------------------
# Classify & summarize
# ---------------------------------------------------------------------------

CLASSIFY_PROMPT = """You are the ATLAS Archive Classifier. Given the first
~1500 characters of a document, decide:

  • which core should OWN this knowledge (ajani | minerva | hermes)
      - ajani:   strategy, engineering, energy, survival, projects
      - minerva: ethics, history, culture, biology, story, art, psychology
      - hermes:  math, physics, code, algorithms, formal systems
  • a 2-3 word domain label
  • a one-paragraph SEED summary (everyday words, no jargon)
  • 3 open questions a curious 12-year-old might ask after reading this

Output ONLY a JSON object with these exact keys:
  { "core": "...", "domain": "...", "summary": "...", "open_questions": ["...", "...", "..."] }
"""


def _safe_json(text: str) -> dict:
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {}
    import json as _json
    try:
        return _json.loads(match.group(0))
    except _json.JSONDecodeError:
        return {}


async def _classify_and_summarize(name: str, text: str) -> dict:
    head = text[:1500]
    # Use Hermes for the routing call — he's the pattern hunter.
    hermes = get_core("hermes")
    raw = await hermes.think(
        f"FILE: {name}\n\nCONTENT EXCERPT:\n{head}",
        context=CLASSIFY_PROMPT,
    )
    data = _safe_json(raw)
    return {
        "core": (data.get("core") or "ajani").lower(),
        "domain": data.get("domain") or "general",
        "summary": data.get("summary") or "(no summary returned)",
        "open_questions": data.get("open_questions") or [],
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def scan_bytes(filename: str, data: bytes) -> List[ArchiveEntry]:
    """Scan a single uploaded file. ZIPs are exploded into their entries."""
    entries: List[ArchiveEntry] = []
    lower = filename.lower()

    if lower.endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for member in zf.namelist():
                if member.endswith("/"):
                    continue
                if not member.lower().endswith(SUPPORTED_EXTS):
                    continue
                with zf.open(member) as fh:
                    inner_bytes = fh.read()
                entries.append(await _scan_single(member, inner_bytes))
    elif lower.endswith(SUPPORTED_EXTS):
        entries.append(await _scan_single(filename, data))
    else:
        raise ValueError(f"Unsupported file type: {filename}")
    return entries


async def _scan_single(name: str, data: bytes) -> ArchiveEntry:
    text, page_count = _extract_one(name, data)
    sanitized = sanitize_text(text)
    classification = await _classify_and_summarize(name, sanitized)
    return ArchiveEntry(
        filename=os.path.basename(name),
        bytes_size=len(data),
        page_count=page_count,
        extracted_chars=len(sanitized),
        classified_core=classification["core"],
        domain=classification["domain"],
        summary=classification["summary"],
        open_questions=classification["open_questions"],
        excerpt=sanitized[:600],
    )


def entry_to_dict(entry: ArchiveEntry) -> dict:
    return asdict(entry)

"""
PDF reader — Phase 3 Research Pipeline.

Wraps pypdf with two helpers:
  * extract_pdf_text(bytes_io)  → {pages: [...], full_text, page_count, metadata}
  * chunk_text(text, max_chars) → list[str] suitable for per-chunk embedding

The chunker is paragraph-aware (it never breaks a sentence mid-word and
prefers paragraph boundaries) so the downstream embedder gets clean,
self-contained passages.
"""
import io
import logging
from typing import List

import pypdf

logger = logging.getLogger("atlas.pdf_reader")

MAX_PAGES = 200          # refuse to read a 1000-page tome at intake time
MAX_TEXT_CHARS = 200_000  # cap full_text size returned to the API


def extract_pdf_text(blob: bytes) -> dict:
    """Read a PDF byte buffer and return per-page text + a flat full_text.

    Skips pages that pypdf can't decrypt or parse (logs a warning); never
    raises on partial corruption — returns whatever it managed to extract.
    """
    if not blob:
        raise ValueError("empty pdf blob")
    reader = pypdf.PdfReader(io.BytesIO(blob), strict=False)
    if reader.is_encrypted:
        # Try empty password — most "encrypted" academic PDFs use this.
        try:
            reader.decrypt("")
        except Exception:    # noqa: BLE001
            raise ValueError("pdf is password-protected") from None

    pages: List[dict] = []
    parts: List[str] = []
    for i, page in enumerate(reader.pages[:MAX_PAGES]):
        try:
            text = (page.extract_text() or "").strip()
        except Exception as exc:    # noqa: BLE001 — never let one page kill the read
            logger.warning("pdf page %d extract failed: %s", i + 1, exc)
            text = ""
        pages.append({"page": i + 1, "text": text, "word_count": len(text.split())})
        if text:
            parts.append(text)

    full_text = "\n\n".join(parts)
    metadata = {}
    try:
        info = reader.metadata or {}
        metadata = {
            "title": str(info.get("/Title", "")) if info else "",
            "author": str(info.get("/Author", "")) if info else "",
            "creator": str(info.get("/Creator", "")) if info else "",
            "producer": str(info.get("/Producer", "")) if info else "",
        }
    except Exception as exc:    # noqa: BLE001
        logger.debug("metadata read failed: %s", exc)

    return {
        "page_count": len(reader.pages),
        "extracted_pages": len(pages),
        "pages": pages,
        "full_text": full_text[:MAX_TEXT_CHARS],
        "metadata": metadata,
    }


def chunk_text(text: str, max_chars: int = 1800, overlap: int = 200) -> List[str]:
    """Paragraph-aware chunker with optional sentence overlap.

    Splits on blank lines first; if a paragraph exceeds max_chars it is
    sliced on sentence boundaries (period/!/?). Adjacent chunks share
    `overlap` chars to keep the embedded representation continuous.
    """
    if not text:
        return []
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    out: List[str] = []
    buf = ""
    for para in paragraphs:
        if len(para) > max_chars:
            # Heavy paragraph — slice on sentence boundaries.
            sentences = _split_sentences(para)
            for s in sentences:
                if len(buf) + len(s) + 1 > max_chars and buf:
                    out.append(buf.strip())
                    buf = (buf[-overlap:] if overlap else "") + " " + s
                else:
                    buf = (buf + " " + s).strip()
        else:
            if len(buf) + len(para) + 2 > max_chars and buf:
                out.append(buf.strip())
                buf = (buf[-overlap:] if overlap else "") + "\n\n" + para
            else:
                buf = (buf + "\n\n" + para).strip()
    if buf.strip():
        out.append(buf.strip())
    return out


def _split_sentences(text: str) -> List[str]:
    """Cheap sentence split — no nltk dependency."""
    import re
    # split after . ! ? followed by whitespace + uppercase
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\(])", text)
    return [p.strip() for p in parts if p.strip()]

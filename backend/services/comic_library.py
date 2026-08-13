"""ATLAS Comic Library: store actual lawfully obtained comic archives.

CBZ/ZIP/PDF bytes are stored in Mongo GridFS at runtime, never committed to
Git. Metadata is mirrored into the existing vector Memory Bank for Ajani,
Minerva and Hermes so they can discover/reference the issue in normal chat.

Visual panel understanding is a separate capability; this module establishes
safe storage, provenance, deduplication and retrieval of the actual issue.
"""
from __future__ import annotations

import base64
import hashlib
import io
import os
import zipfile
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

from services import memory_bank as mb
from services.comic_archives import provider_info, validate_source

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")
MAX_COMIC_BYTES = int(os.environ.get("ATLAS_COMIC_MAX_BYTES", str(300 * 1024 * 1024)))
MAX_ARCHIVE_ENTRIES = int(os.environ.get("ATLAS_COMIC_MAX_ENTRIES", "1000"))
DEFAULT_PERSONAS = ("ajani", "minerva", "hermes")
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
_client: Optional[AsyncIOMotorClient] = None


def _db():
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(MONGO_URL)
    return _client[DB_NAME]


def _meta():
    return _db()["comic_library"]


def _bucket():
    return AsyncIOMotorGridFSBucket(_db(), bucket_name="comic_files")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ext(name: str) -> str:
    lower = (name or "").lower()
    if lower.endswith(".cbz"):
        return ".cbz"
    if lower.endswith(".zip"):
        return ".zip"
    if lower.endswith(".pdf"):
        return ".pdf"
    return ""


def inspect_comic_bytes(filename: str, payload: bytes) -> Dict[str, Any]:
    """Validate supported archive type and estimate page count without OCR."""
    if not payload:
        raise ValueError("comic payload is empty")
    if len(payload) > MAX_COMIC_BYTES:
        raise ValueError(f"comic exceeds ATLAS_COMIC_MAX_BYTES ({MAX_COMIC_BYTES})")
    ext = _ext(filename)
    if ext in {".cbz", ".zip"}:
        try:
            with zipfile.ZipFile(io.BytesIO(payload)) as zf:
                infos = zf.infolist()
                if len(infos) > MAX_ARCHIVE_ENTRIES:
                    raise ValueError("comic archive contains too many files")
                names = [i.filename for i in infos if not i.is_dir()]
        except zipfile.BadZipFile as exc:
            raise ValueError("invalid CBZ/ZIP archive") from exc
        page_files = [n for n in names if any(n.lower().endswith(e) for e in IMAGE_EXTS)]
        if not page_files:
            raise ValueError("CBZ/ZIP contains no supported image pages")
        return {"format": "cbz", "page_count": len(page_files), "entries": len(names)}
    if ext == ".pdf":
        if not payload.startswith(b"%PDF"):
            raise ValueError("invalid PDF header")
        # Lightweight count avoids adding a new PDF dependency to API startup.
        page_count = max(1, payload.count(b"/Type /Page"))
        return {"format": "pdf", "page_count": page_count, "entries": None}
    raise ValueError("supported comic formats are .cbz, .zip and .pdf")


async def import_comic(
    *, provider: str,
    title: str,
    source_url: str,
    filename: str,
    archive_b64: str,
    series: Optional[str] = None,
    issue_number: Optional[str] = None,
    publisher: Optional[str] = None,
    year: Optional[int] = None,
    subjects: Optional[List[str]] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    p = provider_info(provider)
    if not p:
        raise ValueError("unknown comic provider")
    if not validate_source(provider, source_url):
        raise ValueError("source_url does not match selected comic provider")
    if not title.strip():
        raise ValueError("title is required")
    try:
        payload = base64.b64decode(archive_b64, validate=True)
    except Exception as exc:
        raise ValueError("archive_b64 is not valid base64") from exc

    inspection = inspect_comic_bytes(filename, payload)
    digest = hashlib.sha256(payload).hexdigest()
    existing = await _meta().find_one({"sha256": digest}, {"_id": 0})
    if existing:
        return {"comic": existing, "reused": True, "stored_file": True}

    comic_id = str(uuid4())
    gridfs_id = await _bucket().upload_from_stream(
        filename,
        payload,
        metadata={"comic_id": comic_id, "sha256": digest, "provider": provider},
    )
    tags = [s.strip() for s in (subjects or []) if s and s.strip()]
    doc = {
        "id": comic_id,
        "title": title.strip(),
        "series": (series or "").strip() or None,
        "issue_number": (issue_number or "").strip() or None,
        "publisher": (publisher or "").strip() or None,
        "year": year,
        "provider": provider,
        "provider_name": p["name"],
        "source_url": source_url,
        "filename": filename,
        "format": inspection["format"],
        "page_count": inspection["page_count"],
        "gridfs_id": str(gridfs_id),
        "sha256": digest,
        "subjects": tags,
        "notes": (notes or "").strip() or None,
        "rights_policy": p["rights_policy"],
        "reference_only": True,
        "verbatim_output_policy": "do_not_reproduce_entire_issue; use for private reference and analysis",
        "created_at": _now(),
    }
    await _meta().insert_one(doc.copy())

    reference = (
        f"COMIC REFERENCE · {doc['title']}\n"
        f"Series: {doc.get('series') or 'n/a'} · Issue: {doc.get('issue_number') or 'n/a'}\n"
        f"Publisher: {doc.get('publisher') or 'n/a'} · Year: {doc.get('year') or 'n/a'}\n"
        f"Provider: {doc['provider_name']}\nSource: {source_url}\n"
        f"Pages: {doc['page_count']} · Format: {doc['format']}\n"
        f"Subjects: {', '.join(tags) if tags else 'general creative reference'}\n"
        f"Notes: {doc.get('notes') or 'none'}"
    )
    memory_ids: List[str] = []
    for persona in DEFAULT_PERSONAS:
        row = await mb.store_memory(
            reference,
            persona=persona,
            category="research",
            source_type="comic",
            source_id=f"comic:{comic_id}:{persona}",
            tags=["comic", provider, comic_id, *tags],
            pinned=False,
        )
        if row.get("id"):
            memory_ids.append(row["id"])
    await _meta().update_one({"id": comic_id}, {"$set": {"memory_ids": memory_ids}})
    doc["memory_ids"] = memory_ids
    return {"comic": doc, "reused": False, "stored_file": True}


async def list_comics(*, provider: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    filt: Dict[str, Any] = {}
    if provider:
        filt["provider"] = provider
    cur = _meta().find(filt, {"_id": 0}).sort("created_at", -1).limit(max(1, min(limit, 500)))
    return [row async for row in cur]


async def get_comic(comic_id: str) -> Optional[Dict[str, Any]]:
    return await _meta().find_one({"id": comic_id}, {"_id": 0})

"""Live preview connectors for ATLAS World Knowledge Network.

This module provides the first safe live-connection layer. It fetches only
lightweight metadata/snippets from approved sources and never stores full
copyrighted source material.

The functions are intentionally conservative:
- no database writes
- no full-page archiving
- no crawling beyond the approved source URL
- no claim verification yet
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import httpx

from services import world_knowledge_connector as registry

MAX_BYTES = 350_000
DEFAULT_TIMEOUT = 12.0
USER_AGENT = "ATLAS-WorldKnowledgePreview/1.0 (+metadata-only)"


class LiveConnectorError(RuntimeError):
    """Raised when a live preview connector fails safely."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clean_text(value: str | None, max_len: int = 1000) -> str:
    if not value:
        return ""
    text = re.sub(r"\s+", " ", value).strip()
    return text[:max_len]


def _extract_tag(html: str, pattern: str) -> str:
    match = re.search(pattern, html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return _clean_text(match.group(1))


def _extract_meta_content(html: str, name: str) -> str:
    patterns = [
        rf'<meta[^>]+name=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']',
        rf'<meta[^>]+property=["\']{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']{re.escape(name)}["\']',
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']{re.escape(name)}["\']',
    ]
    for pattern in patterns:
        value = _extract_tag(html, pattern)
        if value:
            return value
    return ""


async def _fetch_text(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise LiveConnectorError("only http/https source URLs are allowed")

    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,application/rss+xml,application/xml;q=0.9,*/*;q=0.5"}
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, follow_redirects=True, headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
        content = response.content[:MAX_BYTES]
    return content.decode(response.encoding or "utf-8", errors="replace")


async def preview_web_metadata(source_id: str) -> Dict[str, Any]:
    """Fetch a conservative metadata preview for an approved web source."""
    source = registry.get_source(source_id)
    if not source:
        raise LiveConnectorError(f"unknown source_id: {source_id}")

    url = source.get("url")
    if not url:
        raise LiveConnectorError(f"source has no URL: {source_id}")

    html = await _fetch_text(url)
    title = _extract_tag(html, r"<title[^>]*>(.*?)</title>")
    description = _extract_meta_content(html, "description") or _extract_meta_content(html, "og:description")
    canonical = _extract_tag(html, r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']') or url

    headings = []
    for match in re.finditer(r"<h[12][^>]*>(.*?)</h[12]>", html, flags=re.IGNORECASE | re.DOTALL):
        heading = re.sub(r"<[^>]+>", " ", match.group(1))
        heading = _clean_text(heading, 160)
        if heading and heading not in headings:
            headings.append(heading)
        if len(headings) >= 8:
            break

    return {
        "source_id": source_id,
        "source_name": source.get("name"),
        "ai_owner": source.get("ai_owner"),
        "connector_type": "web_metadata",
        "fetched_at": _utc_now(),
        "url": url,
        "canonical_url": canonical,
        "title": title or source.get("name"),
        "description": description,
        "headings": headings,
        "content_stored": False,
        "copyright_rule": "metadata/snippets only; no full source copy stored",
    }


async def preview_rss(source_id: str, limit: int = 5) -> Dict[str, Any]:
    """Fetch a lightweight RSS/Atom preview when the source URL is a feed.

    Many registry entries list a home URL rather than a feed URL, so failures
    are returned cleanly and can be improved later by adding exact feed URLs.
    """
    source = registry.get_source(source_id)
    if not source:
        raise LiveConnectorError(f"unknown source_id: {source_id}")

    url = source.get("url")
    if not url:
        raise LiveConnectorError(f"source has no URL: {source_id}")

    xml_text = await _fetch_text(url)
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        raise LiveConnectorError("source URL did not return parseable RSS/Atom XML; add an exact feed URL later") from exc

    items: List[Dict[str, Any]] = []
    for item in root.findall(".//item")[: max(1, min(limit, 20))]:
        title = _clean_text(item.findtext("title"), 240)
        link = _clean_text(item.findtext("link"), 500)
        published = _clean_text(item.findtext("pubDate"), 120)
        summary = _clean_text(item.findtext("description"), 700)
        items.append({"title": title, "link": link, "published_at": published, "summary_or_excerpt": summary})

    if not items:
        ns_items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
        for item in ns_items[: max(1, min(limit, 20))]:
            title = _clean_text(item.findtext("{http://www.w3.org/2005/Atom}title"), 240)
            link_el = item.find("{http://www.w3.org/2005/Atom}link")
            link = link_el.attrib.get("href", "") if link_el is not None else ""
            published = _clean_text(item.findtext("{http://www.w3.org/2005/Atom}updated"), 120)
            summary = _clean_text(item.findtext("{http://www.w3.org/2005/Atom}summary"), 700)
            items.append({"title": title, "link": link, "published_at": published, "summary_or_excerpt": summary})

    return {
        "source_id": source_id,
        "source_name": source.get("name"),
        "ai_owner": source.get("ai_owner"),
        "connector_type": "rss",
        "fetched_at": _utc_now(),
        "url": url,
        "items_found": len(items),
        "items": items,
        "content_stored": False,
        "copyright_rule": "feed metadata/snippets only; no full source copy stored",
    }


async def preview_source(source_id: str, limit: int = 5) -> Dict[str, Any]:
    """Preview one approved source using the safest available connector."""
    source = registry.get_source(source_id)
    if not source:
        raise LiveConnectorError(f"unknown source_id: {source_id}")

    planned = registry.plan_sync_job(source_id)
    connector_type = planned["connector_type"]

    if connector_type == "github":
        from services import source_code_connector
        return await source_code_connector.preview_github_repository(source_id, commit_limit=limit)

    if connector_type == "rss":
        try:
            return await preview_rss(source_id, limit=limit)
        except LiveConnectorError as exc:
            fallback = await preview_web_metadata(source_id)
            fallback["connector_type"] = "web_metadata_fallback"
            fallback["rss_error"] = str(exc)
            return fallback

    return await preview_web_metadata(source_id)

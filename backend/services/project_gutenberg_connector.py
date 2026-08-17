"""Project Gutenberg connector for the ATLAS book/creative knowledge layer.

Uses Project Gutenberg's supported OPDS discovery feed instead of crawling
HTML pages. One request is made per user search. Bulk mirroring/downloads are
intentionally out of scope here; use Gutenberg's official catalog/mirror
instructions for that workflow.
"""
from __future__ import annotations

import os
from typing import Dict, List
from urllib.parse import urlencode
from xml.etree import ElementTree as ET

import httpx

OPDS_SEARCH_URL = "https://www.gutenberg.org/ebooks/search.opds/"
DEFAULT_USER_AGENT = (
    "ATLAS-KnowledgeBank/1.0 "
    "(+https://github.com/Monkey-cpu-ally/atlas-core)"
)
ATOM = "{http://www.w3.org/2005/Atom}"
DCTERMS = "{http://purl.org/dc/terms/}"


def _text(node, tag: str) -> str:
    child = node.find(tag)
    return (child.text or "").strip() if child is not None and child.text else ""


def _authors(entry) -> List[str]:
    values: List[str] = []
    for author in entry.findall(f"{ATOM}author"):
        name = _text(author, f"{ATOM}name")
        if name:
            values.append(name)
    return values


def _links(entry) -> Dict[str, str]:
    links: Dict[str, str] = {}
    for link in entry.findall(f"{ATOM}link"):
        href = (link.attrib.get("href") or "").strip()
        rel = (link.attrib.get("rel") or "").strip()
        media_type = (link.attrib.get("type") or "").strip()
        if not href:
            continue
        if rel == "alternate" and media_type == "text/html":
            links.setdefault("catalog", href)
        elif "text/plain" in media_type:
            links.setdefault("text", href)
        elif "epub" in media_type:
            links.setdefault("epub", href)
        elif "kindle" in media_type or "mobipocket" in media_type:
            links.setdefault("kindle", href)
    return links


def parse_opds(xml_text: str) -> List[Dict[str, object]]:
    """Parse a Gutenberg OPDS result page into normalized ATLAS book records."""
    root = ET.fromstring(xml_text)
    books: List[Dict[str, object]] = []
    for entry in root.findall(f"{ATOM}entry"):
        book_id = _text(entry, f"{ATOM}id")
        title = _text(entry, f"{ATOM}title")
        summary = _text(entry, f"{ATOM}summary")
        issued = _text(entry, f"{DCTERMS}issued")
        language = _text(entry, f"{DCTERMS}language")
        books.append({
            "id": book_id,
            "title": title,
            "authors": _authors(entry),
            "summary": summary,
            "gutenberg_release_date": issued,
            "language": language,
            "provider": "Project Gutenberg",
            "resource_type": "public_domain_book",
            "rights_policy": "verify_item_and_jurisdiction_before_local_copy",
            "links": _links(entry),
        })
    return books


async def search_books(query: str, *, timeout: float = 20.0) -> List[Dict[str, object]]:
    """Search one OPDS result page. Does not auto-page or bulk-download."""
    q = (query or "").strip()
    if not q:
        return []
    url = f"{OPDS_SEARCH_URL}?{urlencode({'query': q})}"
    user_agent = os.getenv("ATLAS_GUTENBERG_USER_AGENT", DEFAULT_USER_AGENT)
    headers = {"User-Agent": user_agent, "Accept": "application/atom+xml, application/xml;q=0.9"}
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
        response = await client.get(url)
        response.raise_for_status()
    return parse_opds(response.text)

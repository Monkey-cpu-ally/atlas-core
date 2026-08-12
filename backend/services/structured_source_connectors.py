"""Structured source connectors for ATLAS Knowledge Bank.

These adapters normalize high-value public knowledge sources into the existing
FetchedSource model. Raw source text is handed to the existing distiller and is
not persisted directly by this module.
"""
from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional
from urllib.parse import unquote, urlparse

import httpx

from models.knowledge_models import FetchedSource, SourceType

USER_AGENT = os.environ.get(
    "ATLAS_KNOWLEDGE_USER_AGENT",
    "ATLAS-Knowledge/1.0 (research connector; contact configured by operator)",
)
TIMEOUT = 20.0


def provider_for_url(url: str) -> Optional[str]:
    host = (urlparse(url).hostname or "").lower()
    if host.endswith("wikipedia.org"):
        return "wikipedia"
    if host.endswith("wikidata.org"):
        return "wikidata"
    if host.endswith("openalex.org"):
        return "openalex"
    if host.endswith("ncbi.nlm.nih.gov") or host.endswith("pubmed.ncbi.nlm.nih.gov"):
        return "pubmed"
    if host.endswith("ntrs.nasa.gov"):
        return "nasa_ntrs"
    if host.endswith("nist.gov"):
        return "nist"
    if host.endswith("loc.gov"):
        return "library_of_congress"
    return None


async def fetch_structured(url: str) -> FetchedSource:
    provider = provider_for_url(url)
    if provider == "wikipedia":
        return await _fetch_wikipedia(url)
    if provider == "wikidata":
        return await _fetch_wikidata(url)
    if provider == "openalex":
        return await _fetch_openalex(url)
    if provider == "pubmed":
        return await _fetch_pubmed(url)
    if provider == "nasa_ntrs":
        return await _fetch_nasa_ntrs(url)
    if provider == "nist":
        return await _fetch_nist(url)
    if provider == "library_of_congress":
        return await _fetch_loc(url)
    raise ValueError(f"No structured connector for URL: {url}")


async def _get_json(url: str, *, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        response = await client.get(url, params=params, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        return response.json()


async def _get_text(url: str, *, params: Optional[Dict[str, Any]] = None) -> str:
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        response = await client.get(url, params=params, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        return response.text


def _trim(text: str, limit: int = 60000) -> str:
    return (text or "").strip()[:limit]


async def _fetch_wikipedia(url: str) -> FetchedSource:
    parsed = urlparse(url)
    match = re.search(r"/wiki/(.+)$", parsed.path)
    if not match:
        raise ValueError("Wikipedia connector expects an article URL")
    title = unquote(match.group(1)).replace("_", " ")
    endpoint = f"{parsed.scheme or 'https'}://{parsed.netloc}/w/api.php"
    payload = await _get_json(endpoint, params={
        "action": "query", "format": "json", "formatversion": 2,
        "prop": "extracts|info", "explaintext": 1, "redirects": 1,
        "inprop": "url", "titles": title,
    })
    pages = payload.get("query", {}).get("pages", [])
    if not pages or pages[0].get("missing"):
        raise ValueError(f"Wikipedia article not found: {title}")
    page = pages[0]
    canonical = page.get("canonicalurl") or url
    return FetchedSource(
        source_type=SourceType.WEB,
        source_url=canonical,
        title=page.get("title") or title,
        author="Wikipedia contributors",
        text=_trim(page.get("extract", "")),
        extra={"provider": "wikipedia", "page_id": page.get("pageid")},
    )


async def _fetch_wikidata(url: str) -> FetchedSource:
    match = re.search(r"/(Q\d+)(?:$|[/?#])", url, re.IGNORECASE)
    if not match:
        raise ValueError("Wikidata connector expects an entity URL such as /wiki/Q42")
    qid = match.group(1).upper()
    payload = await _get_json(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json")
    entity = payload.get("entities", {}).get(qid, {})
    labels = entity.get("labels", {})
    descriptions = entity.get("descriptions", {})
    label = labels.get("en", {}).get("value") or qid
    description = descriptions.get("en", {}).get("value", "")
    aliases = [a.get("value") for a in entity.get("aliases", {}).get("en", [])[:20] if a.get("value")]
    property_ids = list((entity.get("claims") or {}).keys())[:100]
    text = f"{label}\n\nDESCRIPTION: {description}\nALIASES: {', '.join(aliases)}\nPROPERTIES: {', '.join(property_ids)}"
    return FetchedSource(
        source_type=SourceType.WEB,
        source_url=f"https://www.wikidata.org/wiki/{qid}",
        title=label,
        author="Wikidata contributors",
        text=_trim(text),
        extra={"provider": "wikidata", "entity_id": qid, "property_ids": property_ids},
    )


def _openalex_abstract(inverted: Optional[Dict[str, Any]]) -> str:
    if not inverted:
        return ""
    positions = []
    for word, indexes in inverted.items():
        for index in indexes:
            positions.append((int(index), word))
    return " ".join(word for _, word in sorted(positions))


async def _fetch_openalex(url: str) -> FetchedSource:
    match = re.search(r"/(W\d+)(?:$|[/?#])", url, re.IGNORECASE)
    if not match:
        raise ValueError("OpenAlex connector currently expects a work URL such as /W2741809807")
    work_id = match.group(1).upper()
    payload = await _get_json(f"https://api.openalex.org/works/{work_id}")
    authors = [
        a.get("author", {}).get("display_name")
        for a in payload.get("authorships", [])[:20]
        if a.get("author", {}).get("display_name")
    ]
    abstract = _openalex_abstract(payload.get("abstract_inverted_index"))
    title = payload.get("display_name") or payload.get("title") or work_id
    text = (
        f"# {title}\n\nAUTHORS: {', '.join(authors)}\n"
        f"PUBLICATION YEAR: {payload.get('publication_year')}\n"
        f"DOI: {payload.get('doi') or '—'}\n"
        f"CITED BY: {payload.get('cited_by_count', 0)}\n\nABSTRACT:\n{abstract}"
    )
    return FetchedSource(
        source_type=SourceType.ACADEMIC,
        source_url=payload.get("id") or f"https://openalex.org/{work_id}",
        title=title,
        author=", ".join(authors[:6]) or None,
        text=_trim(text),
        extra={"provider": "openalex", "work_id": work_id, "doi": payload.get("doi")},
    )


async def _fetch_pubmed(url: str) -> FetchedSource:
    match = re.search(r"/(\d{4,12})/?(?:[?#].*)?$", url)
    if not match:
        raise ValueError("PubMed connector expects an article URL ending in a PMID")
    pmid = match.group(1)
    xml_text = await _get_text(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
        params={"db": "pubmed", "id": pmid, "retmode": "xml", "tool": "ATLAS_Knowledge"},
    )
    root = ET.fromstring(xml_text)
    article = root.find(".//PubmedArticle")
    if article is None:
        raise ValueError(f"PubMed record not found: {pmid}")
    title_node = article.find(".//ArticleTitle")
    title = "".join(title_node.itertext()).strip() if title_node is not None else f"PubMed {pmid}"
    abstract_parts = []
    for node in article.findall(".//Abstract/AbstractText"):
        label = node.attrib.get("Label")
        body = "".join(node.itertext()).strip()
        abstract_parts.append(f"{label}: {body}" if label else body)
    authors = []
    for node in article.findall(".//Author")[:20]:
        name = " ".join(filter(None, [node.findtext("ForeName"), node.findtext("LastName")])).strip()
        if name:
            authors.append(name)
    text = f"# {title}\n\nPMID: {pmid}\nAUTHORS: {', '.join(authors)}\n\nABSTRACT:\n{' '.join(abstract_parts)}"
    return FetchedSource(
        source_type=SourceType.ACADEMIC,
        source_url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        title=title,
        author=", ".join(authors[:6]) or None,
        text=_trim(text),
        extra={"provider": "pubmed", "pmid": pmid},
    )


async def _fetch_nasa_ntrs(url: str) -> FetchedSource:
    match = re.search(r"/citations/([A-Za-z0-9._-]+)", url)
    if not match:
        raise ValueError("NASA NTRS connector expects a /citations/<id> URL")
    citation_id = match.group(1)
    payload = await _get_json(f"https://ntrs.nasa.gov/api/citations/{citation_id}")
    title = payload.get("title") or citation_id
    abstract = payload.get("abstract") or ""
    authors = []
    for author in payload.get("authorAffiliations", []) or payload.get("authors", []) or []:
        if isinstance(author, dict):
            name = author.get("meta", {}).get("author", {}).get("name") or author.get("name")
            if name:
                authors.append(name)
    subjects = payload.get("subjectCategories") or []
    text = f"# {title}\n\nNASA DOCUMENT ID: {citation_id}\nAUTHORS: {', '.join(authors)}\nSUBJECTS: {subjects}\n\nABSTRACT:\n{abstract}"
    return FetchedSource(
        source_type=SourceType.ACADEMIC,
        source_url=f"https://ntrs.nasa.gov/citations/{citation_id}",
        title=title,
        author=", ".join(authors[:6]) or None,
        text=_trim(text),
        extra={"provider": "nasa_ntrs", "citation_id": citation_id},
    )


async def _fetch_nist(url: str) -> FetchedSource:
    """NIST has several APIs; use the page as the stable entry point for V1.

    Provider tagging lets the Knowledge Bank distinguish NIST material now,
    while specialized NVD/PDR adapters can be layered in without changing the
    ingestion contract.
    """
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        response = await client.get(url, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
    text = re.sub(r"<script\b[^>]*>.*?</script>", " ", response.text, flags=re.I | re.S)
    text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    title = re.sub(r"<[^>]+>", " ", title_match.group(1)).strip() if title_match else "NIST resource"
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return FetchedSource(
        source_type=SourceType.WEB,
        source_url=str(response.url),
        title=title,
        author="National Institute of Standards and Technology",
        text=_trim(text),
        extra={"provider": "nist"},
    )


async def _fetch_loc(url: str) -> FetchedSource:
    match = re.search(r"/item/([^/?#]+)/?", url)
    if not match:
        raise ValueError("Library of Congress connector expects a /item/<id>/ URL")
    item_id = match.group(1)
    payload = await _get_json(f"https://www.loc.gov/item/{item_id}/", params={"fo": "json"})
    item = payload.get("item", payload)
    title = item.get("title") or item_id
    description = item.get("description") or item.get("summary") or []
    if isinstance(description, list):
        description = " ".join(str(x) for x in description)
    creators = item.get("contributor_names") or item.get("contributors") or []
    text = (
        f"# {title}\n\nCREATORS: {creators}\nDATE: {item.get('date') or item.get('created_published') or '—'}\n"
        f"SUBJECTS: {item.get('subject') or item.get('subjects') or []}\n\nDESCRIPTION:\n{description}"
    )
    return FetchedSource(
        source_type=SourceType.WEB,
        source_url=f"https://www.loc.gov/item/{item_id}/",
        title=title,
        author=str(creators[:6]) if isinstance(creators, list) and creators else None,
        text=_trim(text),
        extra={"provider": "library_of_congress", "item_id": item_id},
    )

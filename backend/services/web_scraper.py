"""
Web scraper — Phase 3 Research Pipeline.

Fetches HTML pages and extracts readable text without depending on a paid
search API. Two surfaces:

  * search_web(query, top_n)  → list of {title, url, snippet} via
                                 DuckDuckGo HTML (no API key, accepts
                                 server traffic)
  * fetch_page(url)            → {url, title, text, word_count, fetched_at}
                                 reads the HTML, strips boilerplate, returns
                                 a clean text block ready for embedding.

Cloud-IP block handling: some search engines and CDNs reject datacentre
traffic. We surface that as a 503-friendly ResearchUnreachable exception
so the route layer can return a clean error to the HUD.
"""
import logging
import re
from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import quote_plus, urljoin, urlparse

import httpx
from selectolax.parser import HTMLParser

logger = logging.getLogger("atlas.web_scraper")

_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)
_HEADERS = {
    "User-Agent": _USER_AGENT,
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

# Tags whose text is almost never useful for research summarisation.
_DROP_TAGS = {
    "script", "style", "noscript", "iframe", "form", "button", "svg",
    "header", "footer", "nav", "aside",
}


class ResearchUnreachable(Exception):
    """Upstream search/fetch is blocking the cloud IP or returned 5xx."""


# ---------------------------------------------------------------------------
# Search — DuckDuckGo HTML (no API key)
# ---------------------------------------------------------------------------
async def search_web(query: str, top_n: int = 5) -> List[dict]:
    """Return up to `top_n` search results: {title, url, snippet}.

    DuckDuckGo's HTML endpoint (html.duckduckgo.com/html) is documented for
    bots, allows server requests, and returns simple anchor markup. If it
    starts rejecting our IP we raise ResearchUnreachable so the route can
    fall back to "paste a URL manually".
    """
    if not query.strip():
        return []
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as cli:
            r = await cli.post(url, headers=_HEADERS, data={"q": query})
            r.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ResearchUnreachable(
            f"DuckDuckGo HTML returned {exc.response.status_code} — likely blocking the server IP"
        ) from exc
    except httpx.RequestError as exc:
        raise ResearchUnreachable(f"DuckDuckGo HTML unreachable: {exc}") from exc

    tree = HTMLParser(r.text)
    results: List[dict] = []
    for node in tree.css("div.result")[: top_n * 2]:    # over-fetch then dedupe
        a = node.css_first("a.result__a")
        snip = node.css_first("a.result__snippet") or node.css_first(".result__snippet")
        if not a:
            continue
        href = a.attributes.get("href", "")
        # DDG wraps real URLs in /l/?uddg=… — pull the real one back out.
        m = re.search(r"uddg=([^&]+)", href)
        if m:
            from urllib.parse import unquote
            href = unquote(m.group(1))
        if not href.startswith("http"):
            continue
        title = (a.text() or "").strip()
        snippet = (snip.text() if snip else "").strip()
        results.append({"title": title, "url": href, "snippet": snippet})
        if len(results) >= top_n:
            break
    return results


# ---------------------------------------------------------------------------
# Page fetch + text extract
# ---------------------------------------------------------------------------
def _extract_text(html: str) -> tuple[str, str]:
    """Return (title, body_text). Strips scripts/styles/nav and collapses
    whitespace. Keeps line breaks between block elements so summarisation
    later can chunk on paragraphs."""
    tree = HTMLParser(html)
    title_node = tree.css_first("title")
    title = (title_node.text() if title_node else "").strip()

    # Drop noise nodes in place.
    for tag in _DROP_TAGS:
        for n in tree.css(tag):
            n.decompose()

    # Prefer <main> or <article> when present (much cleaner extraction).
    root = (
        tree.css_first("main")
        or tree.css_first("article")
        or tree.body
        or tree.root
    )
    if root is None:
        return title, ""
    # text(separator="\n") keeps block boundaries; collapse runs of blank lines.
    raw = root.text(separator="\n", strip=True)
    cleaned = re.sub(r"\n{3,}", "\n\n", raw)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    return title, cleaned.strip()


async def fetch_page(url: str, *, max_bytes: int = 1_500_000) -> dict:
    """Fetch a URL and return a clean text payload.

    Caps response size at 1.5 MB so a runaway page can't blow up memory or
    embedding latency. Truncates the extracted text to ~12 000 chars (the
    Hermes summariser only needs the first few thousand to triage)."""
    if not url.startswith(("http://", "https://")):
        raise ValueError("url must be absolute http(s)")
    parsed = urlparse(url)
    host = parsed.hostname or "unknown"
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as cli:
            r = await cli.get(url, headers=_HEADERS)
            r.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise ResearchUnreachable(
            f"{host} returned {exc.response.status_code}"
        ) from exc
    except httpx.RequestError as exc:
        raise ResearchUnreachable(f"{host} unreachable: {exc}") from exc

    content_type = r.headers.get("content-type", "")
    if "html" not in content_type and "xml" not in content_type:
        raise ResearchUnreachable(f"{host} returned non-HTML content-type: {content_type}")

    body = r.text[: max_bytes // 2]    # str char-length ≈ 2x bytes for utf-8
    title, text = _extract_text(body)
    return {
        "url": url,
        "host": host,
        "title": title or url,
        "text": text[:12000],
        "word_count": len(text.split()),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def resolve_url(base: str, href: Optional[str]) -> Optional[str]:
    """Helper for downstream consumers — turn relative links into absolute."""
    if not href:
        return None
    return urljoin(base, href)

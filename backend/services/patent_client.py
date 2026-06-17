"""
Patent client — Phase 3 Research Pipeline.

Queries Google Patents' public search endpoint (no API key required) and
extracts a compact summary per result. Falls back gracefully when the
upstream blocks the cloud IP.

Endpoints we touch:
  GET https://patents.google.com/xhr/query?url=q%3D<query>&exp=
  GET https://patents.google.com/patent/<id>/en  (HTML detail page)
"""
import logging
import re
from typing import List
from urllib.parse import quote_plus

import httpx
from selectolax.parser import HTMLParser

logger = logging.getLogger("atlas.patent_client")

_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)
_HEADERS = {"User-Agent": _UA, "Accept": "application/json,text/html"}


class PatentUnreachable(Exception):
    pass


async def search_patents(query: str, top_n: int = 5) -> List[dict]:
    """Return up to `top_n` patents with {id, title, abstract, url, assignee, filed}.

    Uses the public Google Patents search page directly (no API key). The
    XHR endpoint occasionally rate-limits cloud IPs; on a 4xx/5xx we raise
    PatentUnreachable so the route returns a clean 503 to the HUD.
    """
    if not query.strip():
        return []
    url = (
        "https://patents.google.com/xhr/query"
        f"?url=q%3D{quote_plus(query)}&exp=&download="
    )
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as cli:
            r = await cli.get(url, headers=_HEADERS)
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPStatusError as exc:
        raise PatentUnreachable(
            f"Google Patents returned {exc.response.status_code}"
        ) from exc
    except httpx.RequestError as exc:
        raise PatentUnreachable(f"Google Patents unreachable: {exc}") from exc
    except ValueError as exc:    # JSON parse fail
        raise PatentUnreachable(f"Google Patents returned non-JSON: {exc}") from exc

    results = (data.get("results") or {}).get("cluster") or []
    out: List[dict] = []
    for cluster in results:
        for item in (cluster.get("result") or [])[:top_n]:
            pat = item.get("patent") or {}
            pid = pat.get("publication_number") or pat.get("country_code", "") + pat.get("doc_number", "")
            if not pid:
                continue
            out.append({
                "id": pid,
                "title": pat.get("title", "").strip(),
                "abstract": (pat.get("snippet") or "").replace("\n", " ").strip(),
                "assignee": pat.get("assignee", ""),
                "inventor": ", ".join(pat.get("inventor", []) or []),
                "filed": pat.get("filing_date", ""),
                "url": f"https://patents.google.com/patent/{pid}/en",
            })
            if len(out) >= top_n:
                return out
    return out


async def fetch_patent_detail(patent_id: str) -> dict:
    """Pull the detail page for one patent and return a richer summary.

    Returns {id, title, abstract, claims, description_excerpt, url}.
    Truncates claims+description so the embedder gets compact passages.
    """
    if not re.match(r"^[A-Z0-9\-/]{4,40}$", patent_id):
        raise ValueError("invalid patent id format")
    url = f"https://patents.google.com/patent/{patent_id}/en"
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as cli:
            r = await cli.get(url, headers=_HEADERS)
            r.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise PatentUnreachable(
            f"Patent detail returned {exc.response.status_code}"
        ) from exc
    except httpx.RequestError as exc:
        raise PatentUnreachable(f"Patent detail unreachable: {exc}") from exc

    tree = HTMLParser(r.text)

    def _text(selector: str) -> str:
        node = tree.css_first(selector)
        return (node.text(strip=True) if node else "").strip()

    title = _text("h1#title") or _text("h1")
    abstract = _text("abstract")
    # Claims are usually under <claims> or <section id="claims">
    claims_node = tree.css_first("section.claims") or tree.css_first("claims")
    claims = (claims_node.text(separator="\n", strip=True) if claims_node else "").strip()
    desc_node = tree.css_first("section.description") or tree.css_first("description")
    description = (desc_node.text(separator="\n", strip=True) if desc_node else "").strip()

    return {
        "id": patent_id,
        "title": title,
        "abstract": abstract[:4000],
        "claims": claims[:6000],
        "description_excerpt": description[:6000],
        "url": url,
    }

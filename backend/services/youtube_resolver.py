"""
YouTube channel-RSS resolver.

For a YouTube channel URL, fetch the Atom RSS feed
`https://www.youtube.com/feeds/videos.xml?channel_id=<UC...>` and return the
latest N video URLs.

Why this exists:
  The YouTube transcript API requires a video ID; channel URLs don't have one.
  Per Self-Improvement proposal `410a020f53e34e3997c96e70664eda24`, the fix
  is to enumerate the channel's most recent videos via its RSS feed, then
  attempt transcript ingestion on the resulting video URLs.

Channel URL forms supported:
  /channel/UC...                — channel_id is in the path
  /user/<name>                  — needs an HTML scrape to find canonical channel_id
  /c/<custom>                   — needs an HTML scrape
  /@handle                      — needs an HTML scrape

The RSS feed is a public Atom XML file. Empirically it is **not** subject to
the same cloud-IP block as the private transcript endpoint, so this layer
typically works even when transcript fetch does not.
"""
from __future__ import annotations

import logging
import re
from typing import List, Optional, Tuple
from urllib.parse import urlparse
from xml.etree import ElementTree as ET

import httpx

logger = logging.getLogger("atlas.youtube_resolver")

USER_AGENT = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 atlas-watcher")
RSS_URL_TEMPLATE = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
HTTP_TIMEOUT = 15.0

# Patterns to pull `UCxxxxxx...` out of a channel page's HTML
_CHANNEL_ID_PATTERNS = [
    re.compile(r'"channelId":"(UC[0-9A-Za-z_-]{20,24})"'),
    re.compile(r'"externalId":"(UC[0-9A-Za-z_-]{20,24})"'),
    re.compile(r'<meta itemprop="channelId" content="(UC[0-9A-Za-z_-]{20,24})">'),
    re.compile(r'<link rel="canonical" href="https://www\.youtube\.com/channel/(UC[0-9A-Za-z_-]{20,24})">'),
]


class ResolverError(RuntimeError):
    pass


def parse_channel_form(url: str) -> Tuple[str, str]:
    """Return (form, identifier) for a YouTube channel URL.
       form ∈ {channel_id, user, custom, handle, unknown}."""
    host = (urlparse(url).hostname or "").lower()
    if not host.endswith("youtube.com") and host != "youtu.be":
        raise ValueError(f"not a youtube url: {url}")
    path = urlparse(url).path.rstrip("/")
    # /channel/UC...
    m = re.match(r"^/channel/(UC[0-9A-Za-z_-]{20,24})(/.*)?$", path)
    if m:
        return "channel_id", m.group(1)
    m = re.match(r"^/user/([^/]+)(/.*)?$", path)
    if m:
        return "user", m.group(1)
    m = re.match(r"^/c/([^/]+)(/.*)?$", path)
    if m:
        return "custom", m.group(1)
    m = re.match(r"^/@([^/]+)(/.*)?$", path)
    if m:
        return "handle", m.group(1)
    return "unknown", path


async def resolve_channel_id(channel_url: str) -> str:
    """Return the canonical channel_id (UC...) for any channel URL form.
    Performs an HTML scrape for /user/, /c/, /@ forms."""
    form, ident = parse_channel_form(channel_url)
    if form == "channel_id":
        return ident
    if form == "unknown":
        raise ResolverError(f"cannot recognise channel URL: {channel_url}")
    # Scrape the channel's HTML page to find its canonical channel_id
    try:
        async with httpx.AsyncClient(
            timeout=HTTP_TIMEOUT, follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            r = await client.get(channel_url)
            r.raise_for_status()
            html = r.text
    except httpx.HTTPError as exc:
        raise ResolverError(f"channel HTML fetch failed: {exc}") from exc
    for pat in _CHANNEL_ID_PATTERNS:
        m = pat.search(html)
        if m:
            return m.group(1)
    raise ResolverError(f"channel_id not found in HTML for {channel_url}")


async def latest_video_urls(channel_url: str, *, n: int = 3) -> List[dict]:
    """Return up to n latest videos as
       [{video_id, url, title, published, author}].
    Atom feed format: <feed><entry>… first entry is newest."""
    channel_id = await resolve_channel_id(channel_url)
    rss_url = RSS_URL_TEMPLATE.format(channel_id=channel_id)
    try:
        async with httpx.AsyncClient(
            timeout=HTTP_TIMEOUT, follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            r = await client.get(rss_url)
            r.raise_for_status()
            xml = r.text
    except httpx.HTTPError as exc:
        raise ResolverError(f"RSS fetch failed for {channel_id}: {exc}") from exc

    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise ResolverError(f"RSS XML parse failed: {exc}") from exc

    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt": "http://www.youtube.com/xml/schemas/2015",
    }
    channel_title: Optional[str] = None
    title_el = root.find("atom:title", ns)
    if title_el is not None:
        channel_title = (title_el.text or "").strip()

    videos: List[dict] = []
    for entry in root.findall("atom:entry", ns)[:n]:
        vid_el = entry.find("yt:videoId", ns)
        title_el = entry.find("atom:title", ns)
        pub_el = entry.find("atom:published", ns)
        auth_el = entry.find("atom:author/atom:name", ns)
        if vid_el is None or not (vid_el.text or "").strip():
            continue
        video_id = vid_el.text.strip()
        videos.append({
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "title": (title_el.text or "").strip() if title_el is not None else "",
            "published": (pub_el.text or "").strip() if pub_el is not None else "",
            "author": (auth_el.text or "").strip() if auth_el is not None else (channel_title or ""),
            "channel_id": channel_id,
            "channel_title": channel_title,
        })
    return videos

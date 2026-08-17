"""Rights-aware full-comic archive providers for ATLAS.

These sources are discovery/reference providers, not anonymous download APIs.
ATLAS does not scrape authenticated download endpoints. A user may import a
lawfully obtained CBZ/ZIP/PDF into the Comic Library through comic_library.py.
"""
from __future__ import annotations

from typing import Dict, List, Optional
from urllib.parse import urlparse

PROVIDERS: Dict[str, Dict[str, object]] = {
    "digital_comic_museum": {
        "name": "Digital Comic Museum",
        "base_url": "https://digitalcomicmuseum.com/",
        "content_scope": "Public-domain Golden Age comics and related historic publications",
        "access": "Free registration required for downloads",
        "automation_policy": "discovery/reference only; do not scrape authenticated downloads",
        "rights_policy": "provider reports items are individually researched for public-domain status; preserve item provenance",
        "domains": ["Creative Writing", "Film Studies", "History", "Visual Arts", "Game Design"],
    },
    "comic_book_plus": {
        "name": "Comic Book Plus",
        "base_url": "https://comicbookplus.com/",
        "content_scope": "Public-domain comics, strips, pulp and related historic material",
        "access": "Online reading; downloads may require an account",
        "automation_policy": "discovery/reference only; do not scrape authenticated downloads",
        "rights_policy": "verify item status on provider before import; preserve item provenance",
        "domains": ["Creative Writing", "Film Studies", "History", "Visual Arts", "Game Design"],
    },
}


def provider_info(provider: str) -> Optional[Dict[str, object]]:
    key = (provider or "").strip().lower()
    data = PROVIDERS.get(key)
    return {"id": key, **data} if data else None


def list_providers() -> List[Dict[str, object]]:
    return [provider_info(key) for key in PROVIDERS if provider_info(key)]


def provider_for_url(url: str) -> Optional[str]:
    try:
        host = (urlparse(url).hostname or "").lower()
    except Exception:
        return None
    if host == "digitalcomicmuseum.com" or host.endswith(".digitalcomicmuseum.com"):
        return "digital_comic_museum"
    if host == "comicbookplus.com" or host.endswith(".comicbookplus.com"):
        return "comic_book_plus"
    return None


def validate_source(provider: str, source_url: str) -> bool:
    expected = (provider or "").strip().lower()
    return expected in PROVIDERS and provider_for_url(source_url) == expected

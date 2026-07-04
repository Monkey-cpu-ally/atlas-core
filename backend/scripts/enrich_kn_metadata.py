"""One-shot Knowledge Network metadata enrichment.

Populates real `country / region / source_language / culture_tag /
trust_level / access_method / update_frequency` values on the 19 seeded
sources so `/api/knowledge-network/stats` renders a meaningful facet
map instead of a wall of `unknown` / `unspecified`.

Idempotent: safe to re-run. Rows without a matching pattern are left
untouched. Nothing here overwrites the persona `ai_owner` (that already
comes from the source registration).

Usage:
    python -m scripts.enrich_kn_metadata            # from /app/backend

Match strategy: URL substring OR label substring. First hit wins.
"""
from __future__ import annotations

import asyncio
import os
from typing import Any, Dict, List, Tuple

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

# Reusable metadata bundles ----------------------------------------------------
ARXIV = {
    "country": "US",
    "region": "Global",
    "source_language": "en",
    "trust_level": "high",
    "source_type": "academic_preprint",
    "access_method": "public_rss",
    "update_frequency": "daily",
    "culture_tag": "academic_open_science",
}
USPTO_PATENT = {
    "country": "US",
    "region": "Global",
    "source_language": "en",
    "trust_level": "official",
    "source_type": "patent_registry",
    "access_method": "structured_query",
    "update_frequency": "weekly",
    "culture_tag": "industrial_ip",
}
US_GOV = {
    "country": "US",
    "region": "North America",
    "source_language": "en",
    "trust_level": "official",
    "source_type": "government_agency",
    "access_method": "public_rss",
    "update_frequency": "daily",
    "culture_tag": "western_scientific",
}
US_UNIV = {
    "country": "US",
    "region": "North America",
    "source_language": "en",
    "trust_level": "high",
    "source_type": "university_course",
    "access_method": "public_video",
    "update_frequency": "weekly",
    "culture_tag": "academic_open_learning",
}
UK_EDITORIAL = {
    "country": "UK",
    "region": "Europe",
    "source_language": "en",
    "trust_level": "editorial",
    "source_type": "editorial_design",
    "access_method": "public_rss",
    "update_frequency": "daily",
    "culture_tag": "european_design",
}
US_EDITORIAL_MAKER = {
    "country": "US",
    "region": "North America",
    "source_language": "en",
    "trust_level": "editorial",
    "source_type": "editorial_maker",
    "access_method": "public_rss",
    "update_frequency": "daily",
    "culture_tag": "maker_hacker",
}
INTL_ARCH = {
    "country": "International",
    "region": "Global",
    "source_language": "en",
    "trust_level": "editorial",
    "source_type": "editorial_architecture",
    "access_method": "public_rss",
    "update_frequency": "daily",
    "culture_tag": "global_architecture",
}
COMMUNITY_INDEX = {
    "country": "International",
    "region": "Global",
    "source_language": "en",
    "trust_level": "community",
    "source_type": "curated_index",
    "access_method": "git_watch",
    "update_frequency": "on_demand",
    "culture_tag": "community_curated",
}

# Match rules ----------------------------------------------------------------
# Each entry: ({"registry": <name>|None, "url_contains": str|None,
#               "label_contains": str|None, "kind": str|None},
#              metadata_dict)
RULES: List[Tuple[Dict[str, Any], Dict[str, Any]]] = [
    ({"url_contains": "export.arxiv.org"}, ARXIV),
    ({"url_contains": "nasa.gov"}, US_GOV),
    ({"url_contains": "@mitocw"}, US_UNIV),
    ({"url_contains": "hackaday.com"}, US_EDITORIAL_MAKER),
    ({"url_contains": "dezeen.com"}, UK_EDITORIAL),
    ({"url_contains": "archdaily.com"}, INTL_ARCH),
    ({"url_contains": "github.com/PrejudiceNeutrino"}, COMMUNITY_INDEX),
    # Patent feeds — worldwatch_feeds with url prefix "patent:"
    ({"registry": "worldwatch_feeds", "url_startswith": "patent:"}, USPTO_PATENT),
]

REGISTRIES = ("worldwatch_feeds", "watchers", "youtube_channels")


def _matches(doc: Dict[str, Any], registry: str, pattern: Dict[str, Any]) -> bool:
    if pattern.get("registry") and pattern["registry"] != registry:
        return False
    if pattern.get("url_contains"):
        url = doc.get("url") or doc.get("channel_url") or ""
        if pattern["url_contains"] not in url:
            return False
    if pattern.get("url_startswith"):
        url = doc.get("url") or doc.get("channel_url") or ""
        if not url.startswith(pattern["url_startswith"]):
            return False
    if pattern.get("label_contains"):
        label = doc.get("label") or doc.get("name") or ""
        if pattern["label_contains"] not in label:
            return False
    if pattern.get("kind_field_equals"):
        field, val = pattern["kind_field_equals"]
        if doc.get(field) != val:
            return False
    return True


async def enrich() -> Dict[str, Any]:
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    total = 0
    matched = 0
    already_ok = 0
    repaired = 0
    by_country: Dict[str, int] = {}

    # --- 1. Repair pass: any worldwatch_feeds row whose `source_type` was
    #        clobbered by a prior migration must be restored to its kind
    #        discriminator (rss | patent). The semantic value is preserved
    #        by moving it to `content_type` where the KN metadata block
    #        expects to find it.
    _VALID_KIND = {"rss", "patent"}
    async for doc in db["worldwatch_feeds"].find({}):
        st = doc.get("source_type")
        if st and st not in _VALID_KIND:
            # Infer the correct kind from the URL scheme used at seed time.
            url = doc.get("url") or ""
            new_kind = "patent" if url.startswith("patent:") else "rss"
            await db["worldwatch_feeds"].update_one(
                {"id": doc["id"]},
                {"$set": {"source_type": new_kind, "content_type": st}},
            )
            repaired += 1

    # --- 2. Enrichment pass -------------------------------------------------
    for reg in REGISTRIES:
        async for doc in db[reg].find({}):
            total += 1
            for pattern, meta in RULES:
                if _matches(doc, reg, pattern):
                    # Route the semantic `source_type` to `content_type` so
                    # we never collide with the worldwatch kind discriminator.
                    physical = dict(meta)
                    if "source_type" in physical:
                        physical["content_type"] = physical.pop("source_type")
                    # Only overwrite fields that were missing / defaulted.
                    payload = {
                        k: v for k, v in physical.items()
                        if not doc.get(k) or doc.get(k) in ("unknown", "unspecified", "unverified")
                    }
                    if payload:
                        await db[reg].update_one({"id": doc["id"]}, {"$set": payload})
                        matched += 1
                        c = meta.get("country") or "unknown"
                        by_country[c] = by_country.get(c, 0) + 1
                    else:
                        already_ok += 1
                    break

    client.close()
    return {
        "total_sources_seen": total,
        "rows_enriched": matched,
        "rows_already_populated": already_ok,
        "rows_repaired": repaired,
        "by_country": by_country,
    }


if __name__ == "__main__":
    result = asyncio.run(enrich())
    import json
    print(json.dumps(result, indent=2))

"""Read-only access to the ATLAS Existing Resource Library seed catalog."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

CATALOG_PATH = Path(__file__).resolve().parents[2] / "knowledge-division" / "existing-resource-library-v1.json"


@lru_cache(maxsize=1)
def _catalog() -> Dict:
    with CATALOG_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def all_resources() -> List[Dict]:
    return list(_catalog().get("resources", []))


def get_resource(resource_id: str) -> Optional[Dict]:
    key = (resource_id or "").strip()
    return next((r for r in all_resources() if r.get("id") == key), None)


def search_resources(*, subject: Optional[str] = None, resource_type: Optional[str] = None,
                     provider: Optional[str] = None, q: Optional[str] = None) -> List[Dict]:
    rows = all_resources()
    if subject:
        needle = subject.casefold().strip()
        rows = [r for r in rows if any(needle == s.casefold() for s in r.get("subjects", []))]
    if resource_type:
        needle = resource_type.casefold().strip()
        rows = [r for r in rows if r.get("resource_type", "").casefold() == needle]
    if provider:
        needle = provider.casefold().strip()
        rows = [r for r in rows if r.get("provider", "").casefold() == needle]
    if q:
        needle = q.casefold().strip()
        rows = [r for r in rows if needle in (r.get("title", "") + " " + " ".join(r.get("subjects", []))).casefold()]
    return rows


def coverage(subjects: List[str]) -> Dict[str, Dict[str, int]]:
    result: Dict[str, Dict[str, int]] = {}
    for subject in subjects:
        rows = search_resources(subject=subject)
        result[subject] = {
            "total": len(rows),
            "lessons": sum(r.get("resource_type") in {"lesson_plan", "lesson_collection"} for r in rows),
            "papers": sum(r.get("resource_type") == "research_paper" for r in rows),
        }
    return result

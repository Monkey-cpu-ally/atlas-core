from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent
RESOURCES = ROOT / "resources"
REPO_ROOT = ROOT.parents[2]
KNOWLEDGE_DIVISION = REPO_ROOT / "knowledge-division"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_url(value: Any) -> str:
    """Normalize an HTTP(S) source URL for cross-catalog deduplication."""
    if not isinstance(value, str):
        return ""
    raw = value.strip()
    if not raw:
        return ""
    try:
        parts = urlsplit(raw)
    except ValueError:
        return raw.rstrip("/").lower()
    if parts.scheme.lower() not in {"http", "https"} or not parts.netloc:
        return raw.rstrip("/").lower()
    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), host, path, parts.query, ""))


def normalized_key(resource: Dict[str, Any]) -> str:
    url = canonical_url(resource.get("url") or resource.get("source_url"))
    if url:
        return f"url:{url}"
    provider = str(resource.get("provider") or "").strip().casefold()
    title = str(resource.get("title") or "").strip().casefold()
    return f"meta:{provider}|{title}"


def iter_subject_resources() -> Iterable[Tuple[str, Dict[str, Any]]]:
    """Yield the established subject-manifest resources used by runtime audits."""
    for path in sorted(RESOURCES.rglob("*.json")):
        try:
            manifest = load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        rows = manifest.get("resources")
        if not isinstance(rows, list):
            continue
        rel = str(path.relative_to(RESOURCES))
        subject = manifest.get("subject", "unknown")
        for index, resource in enumerate(rows):
            if not isinstance(resource, dict):
                continue
            resource_id = f"subjects:{rel}#{index}"
            yield resource_id, {
                "resource_id": resource_id,
                "manifest": rel,
                "catalog_family": "subject_manifest",
                "subject": subject,
                "subjects": [subject] if subject else [],
                "title": resource.get("title"),
                "provider": resource.get("provider"),
                "resource_type": resource.get("resource_type"),
                "url": resource.get("url"),
                "subsubjects": resource.get("subsubjects", []),
                "levels": resource.get("levels", []),
                "status": resource.get("status") or manifest.get("status"),
                "storage_policy": resource.get("local_ingestion"),
            }


def iter_division_catalog_resources() -> Iterable[Tuple[str, Dict[str, Any]]]:
    """Yield verified Knowledge Division catalogs without pretending they have level mappings."""
    if not KNOWLEDGE_DIVISION.is_dir():
        return
    paths = list(KNOWLEDGE_DIVISION.glob("resource-catalog-*.json"))
    batch_dir = KNOWLEDGE_DIVISION / "resource-batches"
    if batch_dir.is_dir():
        paths.extend(batch_dir.glob("*.json"))
    for path in sorted(set(paths)):
        try:
            manifest = load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        rows = manifest.get("resources")
        if not isinstance(rows, list):
            continue
        rel = str(path.relative_to(KNOWLEDGE_DIVISION))
        for index, resource in enumerate(rows):
            if not isinstance(resource, dict):
                continue
            status = str(resource.get("status") or "").strip().casefold()
            if status and status not in {"verified", "active", "approved"}:
                continue
            subjects = resource.get("subjects")
            if not isinstance(subjects, list):
                subjects = []
            resource_id = f"division:{rel}#{index}"
            yield resource_id, {
                "resource_id": resource_id,
                "manifest": rel,
                "catalog_family": "knowledge_division",
                "subject": subjects[0] if subjects else "unknown",
                "subjects": subjects,
                "title": resource.get("title"),
                "provider": resource.get("provider"),
                "resource_type": resource.get("type") or resource.get("resource_type"),
                "url": resource.get("source_url") or resource.get("url"),
                "subsubjects": resource.get("subsubjects", []),
                "levels": resource.get("levels", []),
                "status": resource.get("status"),
                "storage_policy": resource.get("storage_policy"),
            }


def iter_catalog_resources() -> Iterable[Tuple[str, Dict[str, Any]]]:
    """Yield a deduplicated index across runtime manifests and Knowledge Division catalogs.

    Subject manifests win when the same canonical endpoint exists in both systems because
    they carry the explicit subsubject/learning-level mappings used by the coverage audit.
    """
    seen = set()
    for iterator in (iter_subject_resources(), iter_division_catalog_resources()):
        for resource_id, resource in iterator:
            key = normalized_key(resource)
            if key in seen:
                continue
            seen.add(key)
            yield resource_id, resource


def build_index() -> Dict[str, Dict[str, Any]]:
    return dict(iter_catalog_resources())


if __name__ == "__main__":
    index = build_index()
    families: Dict[str, int] = {}
    for resource in index.values():
        family = str(resource.get("catalog_family") or "unknown")
        families[family] = families.get(family, 0) + 1
    print(json.dumps({"resource_count": len(index), "catalog_families": families}, indent=2))

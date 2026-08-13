"""Canonical ATLAS Knowledge Bank subject registry.

The original HUD Core 22 are permanent. Newer disciplines are extensions,
not replacements. This module provides one resolver for HUD names, canonical
slugs, legacy backend slugs, and bookshelf aliases without mutating MongoDB.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

_REGISTRY_PATH = Path(__file__).resolve().parents[2] / "knowledge-division" / "subject_registry.json"


def _key(value: str) -> str:
    """Normalize a user/backend/folder subject label for alias lookup."""
    value = (value or "").strip().lower().replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return re.sub(r"_+", "_", value).strip("_")


@lru_cache(maxsize=1)
def load_registry() -> Dict[str, Any]:
    with _REGISTRY_PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    core = data.get("core_subjects", [])
    if len(core) != 22:
        raise RuntimeError(f"ATLAS Core 22 registry must contain exactly 22 subjects; found {len(core)}")
    return data


def core_subjects() -> List[Dict[str, Any]]:
    return list(load_registry()["core_subjects"])


def extension_subjects() -> List[Dict[str, Any]]:
    return list(load_registry().get("extensions", []))


@lru_cache(maxsize=1)
def _index() -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    for tier, items in (("core", core_subjects()), ("extension", extension_subjects())):
        for item in items:
            record = dict(item)
            record["tier"] = tier
            candidates = {item["slug"], item["name"], *item.get("aliases", [])}
            for bank_path in item.get("bank_paths", []):
                candidates.add(Path(bank_path).name)
            for candidate in candidates:
                key = _key(candidate)
                existing = index.get(key)
                # A shared bank path (for example economics-business) must not
                # arbitrarily collapse two canonical subjects. Explicit names,
                # slugs and aliases win; ambiguous shared path keys are removed.
                if existing and existing["slug"] != record["slug"]:
                    index[key] = {"slug": "__ambiguous__", "tier": "ambiguous"}
                else:
                    index[key] = record
    return {k: v for k, v in index.items() if v.get("tier") != "ambiguous"}


def resolve_subject(value: str) -> Optional[Dict[str, Any]]:
    """Resolve a canonical slug/name/legacy alias/bank folder to one subject."""
    if not value:
        return None
    result = _index().get(_key(value))
    return dict(result) if result else None


def canonical_slug(value: str) -> Optional[str]:
    resolved = resolve_subject(value)
    return resolved["slug"] if resolved else None


def is_core_subject(value: str) -> bool:
    resolved = resolve_subject(value)
    return bool(resolved and resolved.get("tier") == "core")


def registry_summary() -> Dict[str, Any]:
    data = load_registry()
    return {
        "schema_version": data["schema_version"],
        "core_count": len(data["core_subjects"]),
        "extension_count": len(data.get("extensions", [])),
        "core_slugs": [item["slug"] for item in data["core_subjects"]],
    }

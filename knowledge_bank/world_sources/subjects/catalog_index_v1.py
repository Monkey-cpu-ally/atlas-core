from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

ROOT = Path(__file__).resolve().parent
RESOURCES = ROOT / "resources"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def iter_catalog_resources() -> Iterable[Tuple[str, Dict[str, Any]]]:
    """Yield stable resource IDs and normalized manifest metadata."""
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
            resource_id = f"{rel}#{index}"
            yield resource_id, {
                "resource_id": resource_id,
                "manifest": rel,
                "subject": subject,
                "title": resource.get("title"),
                "provider": resource.get("provider"),
                "resource_type": resource.get("resource_type"),
                "url": resource.get("url"),
                "subsubjects": resource.get("subsubjects", []),
                "levels": resource.get("levels", []),
            }


def build_index() -> Dict[str, Dict[str, Any]]:
    return dict(iter_catalog_resources())


if __name__ == "__main__":
    index = build_index()
    print(json.dumps({"resource_count": len(index)}, indent=2))

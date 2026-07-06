"""Simple JSON file store for ATLAS local development.

This store is intentionally small. It is meant for early persistence, not final
production storage.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


def _to_jsonable(value: Any) -> Any:
    """Convert common Python objects into JSON-safe values."""

    if is_dataclass(value):
        return _to_jsonable(asdict(value))
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list | tuple | set):
        return [_to_jsonable(item) for item in value]
    return value


class JsonFileStore:
    """Append-and-read JSON record store.

    Records are stored in one JSON file per collection.
    """

    def __init__(self, root_dir: str | Path) -> None:
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, collection: str) -> Path:
        safe_collection = collection.replace("/", "_").replace("..", "_")
        return self.root_dir / f"{safe_collection}.json"

    def read_collection(self, collection: str) -> list[dict[str, Any]]:
        path = self._path(collection)
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError(f"Collection must contain a list: {collection}")
        return data

    def write_collection(self, collection: str, records: list[dict[str, Any]]) -> None:
        path = self._path(collection)
        with path.open("w", encoding="utf-8") as file:
            json.dump(_to_jsonable(records), file, indent=2, sort_keys=True)
            file.write("\n")

    def append_record(self, collection: str, record: Any) -> dict[str, Any]:
        records = self.read_collection(collection)
        json_record = _to_jsonable(record)
        if not isinstance(json_record, dict):
            raise TypeError("Persisted record must serialize to a JSON object")
        records.append(json_record)
        self.write_collection(collection, records)
        return json_record

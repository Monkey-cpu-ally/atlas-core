"""Persistent JSON-backed source registry for the ATLAS learning engine."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict
from pathlib import Path
from threading import RLock
from typing import Any

from .source_registry import SourceRecord, SourceRegistry


class JsonSourceRegistry(SourceRegistry):
    """Source registry that survives process restarts.

    Records are loaded when the registry is created and written atomically after
    each successful mutation. The public API remains compatible with
    ``SourceRegistry`` so callers can replace the in-memory implementation
    without changing the learning pipeline.
    """

    FORMAT_VERSION = 1

    def __init__(self, path: str | os.PathLike[str]) -> None:
        self.path = Path(path)
        self._file_lock = RLock()
        super().__init__()
        self._load()

    def register(self, record: SourceRecord, *, replace: bool = False) -> SourceRecord:
        registered = super().register(record, replace=replace)
        try:
            self._persist()
        except Exception:
            # Restore the in-memory state from the last durable snapshot so a
            # failed disk write cannot leave memory and storage disagreeing.
            self._reset_from_disk()
            raise
        return registered

    def _load(self) -> None:
        if not self.path.exists():
            return

        with self._file_lock:
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid source registry JSON: {self.path}") from exc

        if not isinstance(raw, dict):
            raise ValueError("source registry root must be an object")
        if raw.get("format_version") != self.FORMAT_VERSION:
            raise ValueError("unsupported source registry format version")

        records = raw.get("records", [])
        if not isinstance(records, list):
            raise ValueError("source registry records must be a list")

        for item in records:
            if not isinstance(item, dict):
                raise ValueError("source registry record must be an object")
            super().register(self._record_from_dict(item))

    def _reset_from_disk(self) -> None:
        with self._lock:
            self._by_identity.clear()
            self._by_hash.clear()
        self._load()

    def _persist(self) -> None:
        payload: dict[str, Any] = {
            "format_version": self.FORMAT_VERSION,
            "records": [asdict(record) for record in self.records()],
        }
        serialized = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._file_lock:
            descriptor, temporary_name = tempfile.mkstemp(
                dir=str(self.path.parent),
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                text=True,
            )
            temporary_path = Path(temporary_name)
            try:
                with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                    handle.write(serialized)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary_path, self.path)
            finally:
                if temporary_path.exists():
                    temporary_path.unlink()

    @staticmethod
    def _record_from_dict(item: dict[str, Any]) -> SourceRecord:
        required = ("source_type", "source_id", "title", "content_hash")
        missing = [name for name in required if not str(item.get(name, "")).strip()]
        if missing:
            raise ValueError(f"source registry record missing fields: {', '.join(missing)}")

        metadata = item.get("metadata", {})
        if not isinstance(metadata, dict):
            raise ValueError("source registry metadata must be an object")

        return SourceRecord(
            source_type=str(item["source_type"]),
            source_id=str(item["source_id"]),
            title=str(item["title"]),
            content_hash=str(item["content_hash"]),
            canonical_url=item.get("canonical_url"),
            creator=item.get("creator"),
            metadata=dict(metadata),
            registered_at=str(item.get("registered_at") or ""),
        )

    def health(self) -> dict[str, object]:
        status = super().health()
        status.update(
            {
                "storage": "json",
                "path": str(self.path),
                "persistent": True,
                "file_exists": self.path.exists(),
            }
        )
        return status

"""Validated loader for ATLAS Creative Reference Library catalogs."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


LIBRARY_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class CreativeReference:
    reference_id: str
    title: str
    kind: str
    category: str
    study: Tuple[str, ...]


class CreativeReferenceLibrary:
    """Loads creator/work catalogs into one queryable, fail-fast reference index."""

    def __init__(self, references: List[CreativeReference]):
        ids = [ref.reference_id for ref in references]
        if len(ids) != len(set(ids)):
            raise ValueError("duplicate creative reference id")
        self._references = tuple(references)
        self._by_id: Dict[str, CreativeReference] = {ref.reference_id: ref for ref in references}

    @classmethod
    def load_default(cls) -> "CreativeReferenceLibrary":
        creators = cls._read_json(LIBRARY_DIR / "creative_masters.json").get("creators", [])
        works = cls._read_json(LIBRARY_DIR / "works_catalog.json").get("works", [])
        refs: List[CreativeReference] = []

        for item in creators:
            name = cls._required_text(item, "name")
            category = cls._required_text(item, "category")
            craft = cls._required_list(item, "craft")
            refs.append(CreativeReference(cls._id("creator", name), name, "creator", category, tuple(craft)))

        for item in works:
            title = cls._required_text(item, "title")
            medium = cls._required_text(item, "medium")
            study = cls._required_list(item, "study")
            refs.append(CreativeReference(cls._id("work", title), title, "work", medium, tuple(study)))

        if not refs:
            raise ValueError("creative reference library is empty")
        return cls(refs)

    @staticmethod
    def _read_json(path: Path) -> dict:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    @staticmethod
    def _required_text(item: dict, key: str) -> str:
        value = str(item.get(key, "")).strip()
        if not value:
            raise ValueError(f"missing required reference field: {key}")
        return value

    @staticmethod
    def _required_list(item: dict, key: str) -> List[str]:
        value = item.get(key)
        if not isinstance(value, list) or not value or not all(str(v).strip() for v in value):
            raise ValueError(f"invalid required reference list: {key}")
        return [str(v).strip() for v in value]

    @staticmethod
    def _id(kind: str, title: str) -> str:
        slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in title)
        slug = "-".join(part for part in slug.split("-") if part)
        return f"{kind}:{slug}"

    def all(self) -> Tuple[CreativeReference, ...]:
        return self._references

    def get(self, reference_id: str) -> CreativeReference | None:
        return self._by_id.get(reference_id)

    def search(self, query: str) -> Tuple[CreativeReference, ...]:
        needle = query.strip().lower()
        if not needle:
            return self.all()
        return tuple(
            ref for ref in self._references
            if needle in ref.title.lower()
            or needle in ref.category.lower()
            or any(needle in principle.lower() for principle in ref.study)
        )

    def stats(self) -> Dict[str, int]:
        creators = sum(ref.kind == "creator" for ref in self._references)
        works = sum(ref.kind == "work" for ref in self._references)
        return {"total": len(self._references), "creators": creators, "works": works}

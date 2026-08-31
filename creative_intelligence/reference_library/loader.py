"""Validated loader and deterministic retrieval for ATLAS Creative Reference Library."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

LIBRARY_DIR = Path(__file__).resolve().parent
_TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class CreativeReference:
    reference_id: str
    title: str
    kind: str
    category: str
    study: Tuple[str, ...]


@dataclass(frozen=True)
class ReferenceMatch:
    reference: CreativeReference
    score: int
    matched_terms: Tuple[str, ...]


class CreativeReferenceLibrary:
    """Loads catalogs into one fail-fast index with ranked local retrieval."""

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
        cleaned = [str(v).strip() for v in value]
        if len({v.casefold() for v in cleaned}) != len(cleaned):
            raise ValueError(f"duplicate values in reference list: {key}")
        return cleaned

    @staticmethod
    def _id(kind: str, title: str) -> str:
        slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in title)
        slug = "-".join(part for part in slug.split("-") if part)
        return f"{kind}:{slug}"

    @staticmethod
    def _tokens(values: Iterable[str]) -> set[str]:
        return {token for value in values for token in _TOKEN_RE.findall(value.casefold())}

    def all(self) -> Tuple[CreativeReference, ...]:
        return self._references

    def get(self, reference_id: str) -> CreativeReference | None:
        return self._by_id.get(reference_id)

    def search(self, query: str) -> Tuple[CreativeReference, ...]:
        needle = query.strip().casefold()
        if not needle:
            return self.all()
        return tuple(ref for ref in self._references if needle in ref.title.casefold() or needle in ref.category.casefold() or any(needle in principle.casefold() for principle in ref.study))

    def retrieve(self, query: str, *, limit: int = 12, kind: str | None = None) -> Tuple[ReferenceMatch, ...]:
        """Rank references using deterministic title/category/craft token signals.

        This is deliberately local and explainable. Vector retrieval can be layered on later
        without changing the caller contract.
        """
        if limit < 1:
            raise ValueError("retrieval limit must be positive")
        if kind not in {None, "creator", "work"}:
            raise ValueError("reference kind must be creator or work")
        terms = self._tokens([query])
        if not terms:
            return tuple()
        matches: List[ReferenceMatch] = []
        for ref in self._references:
            if kind and ref.kind != kind:
                continue
            title_tokens = self._tokens([ref.title])
            category_tokens = self._tokens([ref.category])
            study_tokens = self._tokens(ref.study)
            title_hits = terms & title_tokens
            category_hits = terms & category_tokens
            study_hits = terms & study_tokens
            matched = title_hits | category_hits | study_hits
            if not matched:
                continue
            score = (len(title_hits) * 8) + (len(category_hits) * 4) + (len(study_hits) * 3)
            phrase = query.strip().casefold()
            if phrase and phrase in ref.title.casefold():
                score += 12
            if any(phrase and phrase in principle.casefold() for principle in ref.study):
                score += 6
            matches.append(ReferenceMatch(ref, score, tuple(sorted(matched))))
        matches.sort(key=lambda match: (-match.score, match.reference.title.casefold(), match.reference.reference_id))
        return tuple(matches[:limit])

    def stats(self) -> Dict[str, int]:
        creators = sum(ref.kind == "creator" for ref in self._references)
        works = sum(ref.kind == "work" for ref in self._references)
        return {"total": len(self._references), "creators": creators, "works": works}

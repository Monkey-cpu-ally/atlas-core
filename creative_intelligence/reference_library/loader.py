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
    disciplines: Tuple[str, ...] = ()
    techniques: Tuple[str, ...] = ()
    strengths: Tuple[str, ...] = ()
    study_targets: Tuple[str, ...] = ()
    limitations: Tuple[str, ...] = ()
    provenance: Tuple[str, ...] = ()
    relationships: Tuple[str, ...] = ()

    def retrieval_text(self) -> Tuple[str, ...]:
        return (self.title, self.category, *self.study, *self.disciplines, *self.techniques, *self.strengths, *self.study_targets, *self.limitations, *self.relationships)


@dataclass(frozen=True)
class ReferenceMatch:
    reference: CreativeReference
    score: int
    matched_terms: Tuple[str, ...]


class CreativeReferenceLibrary:
    """Loads catalogs into one fail-fast index with ranked local retrieval."""

    PROFILE_FIELDS = ("disciplines", "techniques", "strengths", "study_targets", "limitations", "provenance", "relationships")

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
            refs.append(cls._reference("creator", name, category, craft, item))
        for item in works:
            title = cls._required_text(item, "title")
            medium = cls._required_text(item, "medium")
            study = cls._required_list(item, "study")
            refs.append(cls._reference("work", title, medium, study, item))
        if not refs:
            raise ValueError("creative reference library is empty")
        return cls(refs)

    @classmethod
    def _reference(cls, kind: str, title: str, category: str, study: List[str], item: dict) -> CreativeReference:
        profile = {field: tuple(cls._optional_list(item, field)) for field in cls.PROFILE_FIELDS}
        return CreativeReference(cls._id(kind, title), title, kind, category, tuple(study), **profile)

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
    def _clean_list(value, key: str, *, required: bool) -> List[str]:
        if value is None and not required:
            return []
        if not isinstance(value, list) or (required and not value) or not all(isinstance(v, str) and v.strip() for v in value):
            label = "required" if required else "optional"
            raise ValueError(f"invalid {label} reference list: {key}")
        cleaned = [v.strip() for v in value]
        if len({v.casefold() for v in cleaned}) != len(cleaned):
            raise ValueError(f"duplicate values in reference list: {key}")
        return cleaned

    @classmethod
    def _required_list(cls, item: dict, key: str) -> List[str]:
        return cls._clean_list(item.get(key), key, required=True)

    @classmethod
    def _optional_list(cls, item: dict, key: str) -> List[str]:
        return cls._clean_list(item.get(key), key, required=False)

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
        return tuple(ref for ref in self._references if any(needle in value.casefold() for value in ref.retrieval_text()))

    def retrieve(self, query: str, *, limit: int = 12, kind: str | None = None) -> Tuple[ReferenceMatch, ...]:
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
            title_hits = terms & self._tokens([ref.title])
            category_hits = terms & self._tokens([ref.category])
            study_hits = terms & self._tokens(ref.study)
            profile_hits = terms & self._tokens((*ref.disciplines, *ref.techniques, *ref.strengths, *ref.study_targets, *ref.limitations, *ref.relationships))
            matched = title_hits | category_hits | study_hits | profile_hits
            if not matched:
                continue
            score = len(title_hits) * 8 + len(category_hits) * 4 + len(study_hits) * 3 + len(profile_hits) * 2
            phrase = query.strip().casefold()
            if phrase and phrase in ref.title.casefold():
                score += 12
            if any(phrase and phrase in principle.casefold() for principle in (*ref.study, *ref.study_targets)):
                score += 6
            matches.append(ReferenceMatch(ref, score, tuple(sorted(matched))))
        matches.sort(key=lambda match: (-match.score, match.reference.title.casefold(), match.reference.reference_id))
        return tuple(matches[:limit])

    def stats(self) -> Dict[str, int]:
        creators = sum(ref.kind == "creator" for ref in self._references)
        works = sum(ref.kind == "work" for ref in self._references)
        profiled = sum(bool(ref.provenance or ref.techniques or ref.study_targets) for ref in self._references)
        return {"total": len(self._references), "creators": creators, "works": works, "profiled": profiled}

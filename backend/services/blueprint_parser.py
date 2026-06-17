"""
Blueprint parser — Phase 6.

Two entry points:
  * parse_structured(blueprint)   — accepts an explicit parts[] + relations[]
                                     payload and normalises it.
  * parse_text(blueprint)         — uses the Phase-1 llm_provider to coax a
                                     parts[] + relations[] list out of a
                                     free-text description; on LLM failure,
                                     falls back to a regex-based extractor.

Output is always the same shape — a list of `ExtractedPart` plus a list of
relations — so the Weaver planner downstream can ignore the source format.
"""
import json
import logging
import re
from typing import Dict, List, Optional, Tuple

from services.llm_provider import send as llm_send
from services import parts_db
from models.weaver_models import (
    BlueprintFormat,
    BlueprintInput,
    BlueprintRelation,
    ExtractedPart,
    PartCategory,
)

logger = logging.getLogger("atlas.blueprint_parser")

_PARSER_SYSTEM = (
    "You are Hermes, ATLAS's pattern hunter. You read a manufacturing or "
    "engineering description and extract:\n"
    "  1. parts[]      — {name, category, quantity, unit?}\n"
    "  2. relations[]  — {from_part, to_part, relation}\n"
    "Categories MUST be one of: component, material, fastener, electronic, "
    "sensor, actuator, tool, consumable.\n"
    "Relations MUST be one of: connects_to, mounts, powers, signals, supplies.\n"
    "Return STRICT JSON only — no prose, no markdown, no commentary."
)


async def parse(blueprint: BlueprintInput) -> Tuple[List[ExtractedPart], List[BlueprintRelation]]:
    """Dispatcher — returns (parts, relations) ready for the planner."""
    if blueprint.format == BlueprintFormat.JSON:
        return _parse_structured(blueprint)
    # CAD_EXPORT and DIAGRAM are placeholders right now — fall through to
    # text parsing on the .description if present; CAD ingest lands later.
    return await parse_text(blueprint)


def _parse_structured(blueprint: BlueprintInput) -> Tuple[List[ExtractedPart], List[BlueprintRelation]]:
    parts: List[ExtractedPart] = []
    for spec in blueprint.parts or []:
        try:
            parts.append(_coerce_part(spec))
        except Exception as exc:    # noqa: BLE001
            logger.warning("skip invalid blueprint part %r: %s", spec, exc)
    relations = list(blueprint.relations or [])
    return parts, relations


def _coerce_part(spec: Dict) -> ExtractedPart:
    """Map a loose dict into an ExtractedPart, defaulting category to component
    when the architect hasn't specified one."""
    cat_raw = (spec.get("category") or "component").lower()
    try:
        cat = PartCategory(cat_raw)
    except ValueError:
        cat = PartCategory.COMPONENT
    return ExtractedPart(
        name=str(spec["name"]).strip(),
        category=cat,
        quantity=float(spec.get("quantity") or 1.0),
        unit=str(spec.get("unit") or "unit"),
        raw_text=spec.get("raw_text"),
        notes=spec.get("notes"),
    )


# ---------------------------------------------------------------------------
# Free-text parsing
# ---------------------------------------------------------------------------
async def parse_text(blueprint: BlueprintInput) -> Tuple[List[ExtractedPart], List[BlueprintRelation]]:
    """Try the LLM first; on failure fall back to a regex extractor."""
    body = (blueprint.text or blueprint.description or "").strip()
    if not body:
        return [], []
    parts, relations = await _llm_parse(body)
    if not parts:
        parts, relations = _regex_parse(body)
    return parts, relations


async def _llm_parse(text: str) -> Tuple[List[ExtractedPart], List[BlueprintRelation]]:
    prompt = (
        "Description:\n"
        f"---\n{text[:6000]}\n---\n\n"
        "Return JSON of the form:\n"
        '{"parts": [{"name": "...", "category": "component|material|fastener|electronic|sensor|actuator|tool|consumable", "quantity": 1, "unit": "unit"}], '
        '"relations": [{"from_part": "...", "to_part": "...", "relation": "connects_to|mounts|powers|signals|supplies"}]}'
    )
    try:
        res = await llm_send("hermes", _PARSER_SYSTEM, prompt,
                             session_id="weaver-parse")
        raw = (res.get("text") or "").strip()
    except Exception as exc:    # noqa: BLE001
        logger.warning("blueprint LLM parse failed: %s", exc)
        return [], []

    payload = _extract_json(raw)
    if not isinstance(payload, dict):
        return [], []

    parts: List[ExtractedPart] = []
    for p in (payload.get("parts") or []):
        try:
            parts.append(_coerce_part(p))
        except Exception as exc:    # noqa: BLE001
            logger.debug("skip part %r: %s", p, exc)

    relations: List[BlueprintRelation] = []
    for r in (payload.get("relations") or []):
        try:
            relations.append(BlueprintRelation(
                from_part=str(r["from_part"]),
                to_part=str(r["to_part"]),
                relation=str(r.get("relation") or "connects_to"),
            ))
        except Exception as exc:    # noqa: BLE001
            logger.debug("skip relation %r: %s", r, exc)

    return parts, relations


def _extract_json(raw: str) -> Optional[Dict]:
    """Pull the first {...} object out of a string, tolerant of preamble."""
    if not raw:
        return None
    # Strip fenced code blocks.
    raw = re.sub(r"```(?:json)?", "", raw).replace("```", "")
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


# Regex fallback — catches obvious "N × Foo" or "qty: X, Foo" patterns.
_QTY_PATTERNS = [
    re.compile(r"(?P<qty>\d+)\s*[x×]\s*(?P<name>[A-Za-z][A-Za-z0-9 \-/]+)"),
    re.compile(r"(?P<qty>\d+)\s+(?P<name>[A-Z][A-Za-z0-9 \-/]+)"),
]


def _regex_parse(text: str) -> Tuple[List[ExtractedPart], List[BlueprintRelation]]:
    seen: Dict[str, ExtractedPart] = {}
    for line in text.splitlines():
        for pat in _QTY_PATTERNS:
            for m in pat.finditer(line):
                name = m.group("name").strip().strip(".,;:")
                qty = float(m.group("qty"))
                if len(name) < 3 or name.lower() in seen:
                    continue
                seen[name.lower()] = ExtractedPart(
                    name=name,
                    category=PartCategory.COMPONENT,
                    quantity=qty,
                    raw_text=line.strip(),
                )
    return list(seen.values()), []


# ---------------------------------------------------------------------------
# Library match enrichment
# ---------------------------------------------------------------------------
async def match_against_library(
    parts: List[ExtractedPart],
) -> List[ExtractedPart]:
    """For every extracted part, try to attach a library_part_id + confidence.
    Returns NEW list (does not mutate input)."""
    enriched: List[ExtractedPart] = []
    for p in parts:
        hit = await parts_db.match_part(p.name)
        if hit:
            enriched.append(p.model_copy(update={
                "library_part_id": hit["id"],
                "library_match_confidence": float(hit.get("_match_confidence", 0.0)),
            }))
        else:
            enriched.append(p)
    return enriched

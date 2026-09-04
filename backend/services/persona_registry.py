"""Canonical ATLAS persona registry loader.

The versioned JSON contract is the only production identity source. The HUD
uses a checked generated copy so its build does not redefine persona roles,
colors, names, or prompts.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict


REGISTRY_PATH = Path(__file__).resolve().parents[2] / "contracts" / "personas.v1.json"
REQUIRED_PERSONAS = {"ajani", "minerva", "hermes", "council"}
REQUIRED_FIELDS = {
    "id",
    "name",
    "title",
    "domain",
    "one_liner",
    "core_belief",
    "teaching_lens",
    "hard_rule",
    "color",
    "color_token",
    "pulse_style",
    "prompt_version",
    "voice_prompt",
}


class PersonaRegistryError(RuntimeError):
    """Raised when the production persona identity contract is invalid."""


@lru_cache(maxsize=1)
def load_registry() -> Dict[str, Any]:
    try:
        payload = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PersonaRegistryError(f"unable to load persona registry: {exc}") from exc

    personas = payload.get("personas")
    if not isinstance(personas, dict) or set(personas) != REQUIRED_PERSONAS:
        raise PersonaRegistryError(
            f"persona registry must contain exactly {sorted(REQUIRED_PERSONAS)}"
        )

    for persona_id, record in personas.items():
        if not isinstance(record, dict):
            raise PersonaRegistryError(f"persona {persona_id!r} must be an object")
        missing = REQUIRED_FIELDS - set(record)
        if missing:
            raise PersonaRegistryError(
                f"persona {persona_id!r} missing fields: {sorted(missing)}"
            )
        if record["id"] != persona_id:
            raise PersonaRegistryError(
                f"persona key {persona_id!r} does not match id {record['id']!r}"
            )
        if not str(record["color"]).startswith("#") or len(record["color"]) != 7:
            raise PersonaRegistryError(f"persona {persona_id!r} has invalid color")

    if payload.get("aliases") != {"trinity": "council"}:
        raise PersonaRegistryError("the only V1 compatibility alias must be trinity -> council")
    return payload


def persona_records() -> Dict[str, Dict[str, Any]]:
    return load_registry()["personas"]

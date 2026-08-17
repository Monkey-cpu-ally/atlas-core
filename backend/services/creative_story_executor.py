"""ATLAS LLM-backed Story Production executor registration."""
from __future__ import annotations

import json
from typing import Mapping

from creative_intelligence.executor_registry import registry
from creative_intelligence.story_production import StoryProductionService, story_create_executor
from services.llm_provider import send


SYSTEM_MESSAGE = (
    "You are ATLAS Story Production. Produce polished, original narrative writing at a professional level. "
    "Follow the supplied brief and craft principles. Never imitate a living creator's distinctive style, "
    "never recycle protected expression, and do not explain your process unless asked."
)


async def _generate_story(spec: Mapping) -> str:
    prompt = (
        "Create the requested story artifact from this production specification.\n\n"
        + json.dumps(spec, ensure_ascii=False, indent=2)
    )
    result = await send("minerva", SYSTEM_MESSAGE, prompt)
    text = result.get("text", "") if isinstance(result, dict) else ""
    if not text.strip():
        raise RuntimeError("ATLAS LLM provider returned empty story output")
    return text


def register_story_executor() -> None:
    service = StoryProductionService(_generate_story)
    registry.register("create", story_create_executor(service))

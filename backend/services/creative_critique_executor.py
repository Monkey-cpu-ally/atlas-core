"""ATLAS LLM-backed Creative Critic Council executor."""
from __future__ import annotations

import json
from typing import Mapping

from creative_intelligence.craft_rubrics import STORY
from creative_intelligence.critic_council import CreativeCriticCouncil
from creative_intelligence.executor_registry import ExecutionRequest, ExecutionResult, registry
from services.llm_provider import send

SYSTEM = """You are an ATLAS specialist creative critic. Evaluate the supplied artifact rigorously, not politely. Return JSON only with keys scores, findings, revision_requests. scores must contain every supplied rubric dimension with an integer 0-100. Findings and revision_requests must be arrays of concise strings. Do not reward generic, rushed, derivative, incoherent, juvenile, or technically weak work."""


def _parse_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
    data = json.loads(cleaned.strip())
    if not isinstance(data, dict):
        raise ValueError("critic response must be an object")
    return data


async def _review(critic: str, focus: str, artifact: str) -> dict:
    dimensions = [{"name": d.name, "question": d.question, "failure_signals": list(d.failure_signals)} for d in STORY.dimensions]
    prompt = json.dumps({"critic": critic, "focus": focus, "passing_score": STORY.passing_score, "rubric": dimensions, "artifact": artifact}, ensure_ascii=False)
    result = await send(critic, SYSTEM, prompt)
    text = result.get("text", "") if isinstance(result, Mapping) else ""
    if not text.strip():
        raise RuntimeError(f"{critic} returned an empty critique")
    return _parse_json(text)


async def execute_critique(request: ExecutionRequest) -> ExecutionResult:
    payload = request.payload or {}
    artifact = str(payload.get("artifact") or payload.get("text") or "").strip()
    if not artifact:
        raise ValueError("critique requires artifact text")

    council = CreativeCriticCouncil()
    critic_scores = {}
    findings = {}
    revisions = {}
    for critic, focus in council.CRITIC_FOCUS.items():
        review = await _review(critic, focus, artifact)
        critic_scores[critic] = review.get("scores", {})
        findings[critic] = list(review.get("findings", []))
        revisions[critic] = list(review.get("revision_requests", []))

    decision = council.review(rubric=STORY, critic_scores=critic_scores, findings=findings, revision_requests=revisions)
    output = {
        "approved": decision.approved,
        "blockers": list(decision.blockers),
        "revision_plan": list(decision.revision_plan),
        "reviews": [
            {"critic": r.critic, "focus": r.focus, "scores": r.scores, "average": r.average, "findings": list(r.findings), "revision_requests": list(r.revision_requests)}
            for r in decision.reviews
        ],
    }
    return ExecutionResult(request.artifact_id, output, "creative-critic-council")


def register_critique_executor() -> None:
    registry.register("critique", execute_critique)

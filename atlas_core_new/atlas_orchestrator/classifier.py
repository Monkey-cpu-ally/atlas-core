"""Intent classification and pipeline stage resolution for Atlas."""

from __future__ import annotations

from .models import IntentType, PipelineStage


class IntentClassifier:
    _intent_keywords: dict[IntentType, tuple[str, ...]] = {
        "blueprint_request": (
            "blueprint",
            "spec",
            "bom",
            "bill of materials",
            "component",
            "layout",
            "diagram",
            "assembly",
            "build plan",
            "resonance scanner",
            "wearable scanner",
            "prototype",
        ),
        "learning_request": (
            "teach",
            "explain",
            "learn",
            "lesson",
            "tutorial",
            "understand",
            "break down",
        ),
        "security_request": (
            "security",
            "guardrail",
            "safety",
            "privacy",
            "threat",
            "policy",
            "compliance",
            "risk",
        ),
        "image_blueprint_extraction": (
            "image",
            "photo",
            "screenshot",
            "scan",
            "extract blueprint",
            "from picture",
            "camera",
        ),
        "general_planning": (
            "plan",
            "roadmap",
            "project",
            "milestone",
            "organize",
            "scope",
            "strategy",
        ),
    }

    def classify(self, user_input: str) -> tuple[IntentType, str]:
        lowered = user_input.lower()
        best_intent: IntentType = "general_planning"
        best_score = -1

        for intent, keywords in self._intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in lowered)
            if score > best_score:
                best_intent = intent
                best_score = score

        if best_score <= 0:
            return "general_planning", "No strong keyword match, defaulted to general planning."

        return best_intent, f"Matched {best_score} keyword(s) for {best_intent}."


def infer_pipeline_stage(
    user_input: str,
    intent: IntentType,
    explicit_stage: PipelineStage | None = None,
) -> PipelineStage:
    if explicit_stage:
        return explicit_stage

    lowered = user_input.lower()
    modify_terms = ("modify", "improve", "iterate", "debug", "fix", "failure", "version")
    build_terms = ("build", "assemble", "wire", "fabricate", "parts", "bom", "tools")

    if any(term in lowered for term in modify_terms):
        return "modify"
    if any(term in lowered for term in build_terms):
        return "build"

    if intent in {"blueprint_request", "image_blueprint_extraction"}:
        return "blueprint"
    if intent == "learning_request":
        return "build"
    if intent == "security_request":
        return "modify"
    return "blueprint"


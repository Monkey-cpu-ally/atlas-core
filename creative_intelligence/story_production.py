"""Story Production Service for ATLAS Creative Studio.

This service constructs a production-grade story-generation specification from an
explicit brief and curated reference principles. It does not fabricate prose by
itself: a text-generation provider must be injected before an artifact can exist.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, asdict
from typing import Callable, Mapping, Sequence

from .executor_registry import ExecutionRequest, ExecutionResult
from .reference_library.loader import CreativeReferenceLibrary


@dataclass(frozen=True)
class StoryBrief:
    premise: str
    audience: str
    medium: str
    tone: str
    genre: str = ""
    constraints: tuple[str, ...] = ()
    emotional_target: str = ""
    reference_queries: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, payload: Mapping):
        required = ("premise", "audience", "medium", "tone")
        missing = [key for key in required if not str(payload.get(key, "")).strip()]
        if missing:
            raise ValueError(f"missing story brief fields: {', '.join(missing)}")
        return cls(
            premise=str(payload["premise"]).strip(), audience=str(payload["audience"]).strip(),
            medium=str(payload["medium"]).strip(), tone=str(payload["tone"]).strip(),
            genre=str(payload.get("genre", "")).strip(),
            constraints=tuple(str(x).strip() for x in payload.get("constraints", ()) if str(x).strip()),
            emotional_target=str(payload.get("emotional_target", "")).strip(),
            reference_queries=tuple(str(x).strip() for x in payload.get("reference_queries", ()) if str(x).strip()),
        )


class StoryProductionService:
    def __init__(self, generator: Callable[[Mapping], str], library: CreativeReferenceLibrary | None = None):
        if not callable(generator):
            raise ValueError("a real text-generation provider is required")
        self.generator = generator
        self.library = library or CreativeReferenceLibrary.load_default()

    def build_spec(self, brief: StoryBrief) -> dict:
        references = []
        seen = set()
        for query in brief.reference_queries:
            for ref in self.library.search(query):
                if ref.reference_id not in seen:
                    references.append({"id": ref.reference_id, "title": ref.title, "study": list(ref.study)})
                    seen.add(ref.reference_id)
        return {
            "brief": asdict(brief),
            "references": references,
            "directives": [
                "Create an original work; references supply craft principles, never copied expression.",
                "Avoid generic, rushed, juvenile, recycled, or forced-comedy writing unless the brief explicitly requires it.",
                "Prioritize causal character decisions, coherent internal logic, deliberate pacing, subtext, thematic unity, and earned emotion.",
                "Do not imitate a living creator's distinctive style; translate references into high-level craft attributes.",
                "Return polished story prose appropriate to the requested medium, not commentary about how to write it.",
            ],
        }

    def create(self, brief: StoryBrief) -> dict:
        spec = self.build_spec(brief)
        text = self.generator(spec)
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("story generator returned no artifact")
        return {"artifact_id": str(uuid.uuid4()), "kind": "story", "text": text.strip(), "spec": spec}


def story_create_executor(service: StoryProductionService):
    def execute(request: ExecutionRequest) -> ExecutionResult:
        brief = StoryBrief.from_mapping(request.payload or {})
        artifact = service.create(brief)
        return ExecutionResult(artifact["artifact_id"], artifact, "story-production-service")
    return execute

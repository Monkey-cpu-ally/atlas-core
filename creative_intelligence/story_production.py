"""Story Production Service for ATLAS Creative Studio.

Constructs a production-grade story specification from an explicit brief and
curated reference intelligence. Reference material supplies transferable craft
principles only; project identity and constraints remain authoritative.
"""
from __future__ import annotations

import inspect
import uuid
from dataclasses import asdict, dataclass
from typing import Awaitable, Callable, Mapping, Union

from .executor_registry import ExecutionRequest, ExecutionResult
from .reference_library.loader import CreativeReferenceLibrary

GeneratorResult = Union[str, Awaitable[str]]
StoryGenerator = Callable[[Mapping], GeneratorResult]


def _string_tuple(value, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes)) or not isinstance(value, (list, tuple)):
        raise ValueError(f"{field} must be a list of strings")
    result = []
    seen = set()
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field} must contain non-empty strings")
        clean = item.strip(); key = clean.casefold()
        if key not in seen:
            seen.add(key); result.append(clean)
    return tuple(result)


@dataclass(frozen=True)
class ReferenceContext:
    query: str = ""
    project_identity: str = ""
    project_constraints: tuple[str, ...] = ()
    diversity_dimensions: tuple[str, ...] = ()
    reference_ids: tuple[str, ...] = ()
    principles: tuple[str, ...] = ()
    study_targets: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, payload):
        if payload in (None, {}): return None
        if not isinstance(payload, Mapping): raise ValueError("reference_context must be an object")
        identity = payload.get("project_identity", "")
        query = payload.get("query", "")
        if not isinstance(identity, str) or not isinstance(query, str): raise ValueError("reference context identity and query must be strings")
        contract = payload.get("contract", {})
        if contract and not isinstance(contract, Mapping): raise ValueError("reference context contract must be an object")
        if contract and contract.get("principle_only") is not True: raise ValueError("reference context must enforce principle-only use")
        if contract and contract.get("project_identity_overrides_reference_influence") is not True: raise ValueError("reference context must preserve project identity authority")
        return cls(
            query=query.strip(), project_identity=identity.strip(),
            project_constraints=_string_tuple(payload.get("project_constraints", ()), "project_constraints"),
            diversity_dimensions=_string_tuple(payload.get("diversity_dimensions", ()), "diversity_dimensions"),
            reference_ids=_string_tuple(payload.get("reference_ids", ()), "reference_ids"),
            principles=_string_tuple(payload.get("principles", ()), "principles"),
            study_targets=_string_tuple(payload.get("study_targets", ()), "study_targets"),
            limitations=_string_tuple(payload.get("limitations", ()), "limitations"),
            provenance=_string_tuple(payload.get("provenance", ()), "provenance"),
        )


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
    reference_context: ReferenceContext | None = None

    @classmethod
    def from_mapping(cls, payload: Mapping):
        required = ("premise", "audience", "medium", "tone")
        missing = [key for key in required if not str(payload.get(key, "")).strip()]
        if missing: raise ValueError(f"missing story brief fields: {', '.join(missing)}")
        return cls(
            premise=str(payload["premise"]).strip(), audience=str(payload["audience"]).strip(), medium=str(payload["medium"]).strip(), tone=str(payload["tone"]).strip(),
            genre=str(payload.get("genre", "")).strip(), constraints=_string_tuple(payload.get("constraints", ()), "constraints"),
            emotional_target=str(payload.get("emotional_target", "")).strip(), reference_queries=_string_tuple(payload.get("reference_queries", ()), "reference_queries"),
            reference_context=ReferenceContext.from_mapping(payload.get("reference_context")),
        )


class StoryProductionService:
    def __init__(self, generator: StoryGenerator, library: CreativeReferenceLibrary | None = None):
        if not callable(generator): raise ValueError("a real text-generation provider is required")
        self.generator = generator; self.library = library or CreativeReferenceLibrary.load_default()

    def build_spec(self, brief: StoryBrief) -> dict:
        references = []; seen = set()
        for query in brief.reference_queries:
            for ref in self.library.search(query):
                if ref.reference_id not in seen:
                    references.append({"id": ref.reference_id, "title": ref.title, "study": list(ref.study)}); seen.add(ref.reference_id)
        context = asdict(brief.reference_context) if brief.reference_context else None
        return {
            "brief": {key: value for key, value in asdict(brief).items() if key != "reference_context"},
            "reference_context": context,
            "references": references,
            "directives": [
                "Create an original work; references supply transferable craft principles, never copied expression.",
                "Project identity and project constraints override every reference influence.",
                "Treat reference limitations as hard anti-imitation boundaries and preserve provenance for auditability.",
                "Avoid generic, rushed, juvenile, recycled, or forced-comedy writing unless the brief explicitly requires it.",
                "Prioritize causal character decisions, coherent internal logic, deliberate pacing, subtext, thematic unity, and earned emotion.",
                "Do not imitate a living creator's distinctive style; translate references into high-level craft attributes.",
                "Return polished story prose appropriate to the requested medium, not commentary about how to write it.",
            ],
        }

    async def create(self, brief: StoryBrief) -> dict:
        spec = self.build_spec(brief); text = self.generator(spec)
        if inspect.isawaitable(text): text = await text
        if not isinstance(text, str) or not text.strip(): raise RuntimeError("story generator returned no artifact")
        return {"artifact_id": str(uuid.uuid4()), "kind": "story", "text": text.strip(), "spec": spec}


def story_create_executor(service: StoryProductionService):
    async def execute(request: ExecutionRequest) -> ExecutionResult:
        brief = StoryBrief.from_mapping(request.payload or {}); artifact = await service.create(brief)
        return ExecutionResult(artifact["artifact_id"], artifact, "story-production-service")
    return execute

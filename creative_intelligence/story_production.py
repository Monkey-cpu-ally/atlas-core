"""Story Production Service for ATLAS Creative Studio."""
from __future__ import annotations
import inspect, uuid
from dataclasses import asdict, dataclass
from typing import Awaitable, Callable, Mapping, Union
from .executor_registry import ExecutionRequest, ExecutionResult
from .reference_library.loader import CreativeReferenceLibrary
from .reference_context import ReferenceContext, string_tuple
GeneratorResult=Union[str,Awaitable[str]]; StoryGenerator=Callable[[Mapping],GeneratorResult]
# Backward-compatible internal alias while callers migrate to the canonical validator.
_string_tuple=string_tuple
@dataclass(frozen=True)
class StoryBrief:
    premise:str; audience:str; medium:str; tone:str; genre:str=""; constraints:tuple[str,...]=(); emotional_target:str=""; reference_queries:tuple[str,...]=(); reference_context:ReferenceContext|None=None
    @classmethod
    def from_mapping(cls,payload:Mapping):
        required=("premise","audience","medium","tone"); missing=[k for k in required if not str(payload.get(k,"")).strip()]
        if missing: raise ValueError(f"missing story brief fields: {', '.join(missing)}")
        return cls(str(payload["premise"]).strip(),str(payload["audience"]).strip(),str(payload["medium"]).strip(),str(payload["tone"]).strip(),str(payload.get("genre","")).strip(),string_tuple(payload.get("constraints",()),"constraints"),str(payload.get("emotional_target","")).strip(),string_tuple(payload.get("reference_queries",()),"reference_queries"),ReferenceContext.from_mapping(payload.get("reference_context")))
class StoryProductionService:
    def __init__(self,generator:StoryGenerator,library:CreativeReferenceLibrary|None=None):
        if not callable(generator): raise ValueError("a real text-generation provider is required")
        self.generator=generator; self.library=library or CreativeReferenceLibrary.load_default()
    def build_spec(self,brief:StoryBrief)->dict:
        references=[]; seen=set()
        for query in brief.reference_queries:
            for ref in self.library.search(query):
                if ref.reference_id not in seen: references.append({"id":ref.reference_id,"title":ref.title,"study":list(ref.study)}); seen.add(ref.reference_id)
        return {"brief":{k:v for k,v in asdict(brief).items() if k!="reference_context"},"reference_context":asdict(brief.reference_context) if brief.reference_context else None,"references":references,"directives":["Create an original work; references supply transferable craft principles, never copied expression.","Project identity and project constraints override every reference influence.","Treat reference limitations as hard anti-imitation boundaries and preserve provenance for auditability.","Avoid generic, rushed, juvenile, recycled, or forced-comedy writing unless the brief explicitly requires it.","Prioritize causal character decisions, coherent internal logic, deliberate pacing, subtext, thematic unity, and earned emotion.","Do not imitate a living creator's distinctive style; translate references into high-level craft attributes.","Return polished story prose appropriate to the requested medium, not commentary about how to write it."]}
    async def create(self,brief:StoryBrief)->dict:
        spec=self.build_spec(brief); text=self.generator(spec)
        if inspect.isawaitable(text): text=await text
        if not isinstance(text,str) or not text.strip(): raise RuntimeError("story generator returned no artifact")
        return {"artifact_id":str(uuid.uuid4()),"kind":"story","text":text.strip(),"spec":spec}
def story_create_executor(service:StoryProductionService):
    async def execute(request:ExecutionRequest)->ExecutionResult:
        artifact=await service.create(StoryBrief.from_mapping(request.payload or {})); return ExecutionResult(artifact["artifact_id"],artifact,"story-production-service")
    return execute

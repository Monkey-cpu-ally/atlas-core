"""Atlas orchestrator service implementing intake -> route -> govern flow."""

from __future__ import annotations

from .agents import AjaniModule, HermesModule, MinervaModule
from .classifier import IntentClassifier, infer_pipeline_stage
from .knowledge import DOCTRINE_FREEZE, get_project_registry_entry
from .memory import ProjectMemoryStore
from .models import AtlasOrchestrateRequest, AtlasOrchestrateResponse, ProjectMemorySnapshot, ProjectSummary
from .policy import PolicyEngine


def _predict_next_version(current_version: str, stage: str) -> str:
    if stage != "modify":
        return current_version

    cleaned = current_version.strip().lower()
    if not cleaned.startswith("v"):
        return "v0.1"
    try:
        major_str, minor_str = cleaned[1:].split(".")
        major = int(major_str)
        minor = int(minor_str)
    except Exception:
        return "v0.1"
    return f"v{major}.{minor + 1}"


class AtlasOrchestratorService:
    def __init__(self) -> None:
        self.classifier = IntentClassifier()
        self.policy = PolicyEngine()
        self.ajani = AjaniModule()
        self.minerva = MinervaModule()
        self.hermes = HermesModule()
        self.memory = ProjectMemoryStore()

    def orchestrate(self, request: AtlasOrchestrateRequest) -> AtlasOrchestrateResponse:
        current_snapshot = self.memory.get_project(request.project)
        registry_entry = get_project_registry_entry(request.project)
        intent, intent_reason = self.classifier.classify(request.user_input)
        stage = infer_pipeline_stage(
            user_input=request.user_input,
            intent=intent,
            explicit_stage=request.pipeline_stage,
        )
        planned_version = _predict_next_version(current_snapshot.current_version, stage)
        policy_decision = self.policy.evaluate(request.user_input)
        safe_user_input = request.user_input
        if policy_decision.blocked:
            safe_user_input = (
                "Policy blocked original request. Generate only safe, defensive, high-level guidance."
            )

        context_constraints = []
        if request.context and isinstance(request.context.get("constraints"), list):
            context_constraints = [str(item) for item in request.context["constraints"]]
        constraints = [*policy_decision.enforced_constraints, *context_constraints]
        if registry_entry:
            constraints.append(
                f"Project registry reference: {registry_entry.get('name')} ({registry_entry.get('version')})"
            )
        elif not DOCTRINE_FREEZE.get("expansion_allowed", True):
            policy_decision.flagged = True
            policy_decision.flags.append("unregistered_project_under_freeze")
            constraints.append(
                "Architecture freeze active: use registered projects only until milestone complete."
            )

        # Non-negotiable routing order:
        # Ajani -> Minerva -> Hermes
        ajani_output = self.ajani.generate(
            user_input=safe_user_input,
            intent=intent,
            stage=stage,
            constraints=constraints,
            version_tag=planned_version,
            registered_project=registry_entry,
        )
        minerva_output = self.minerva.generate(
            user_input=safe_user_input,
            mode=request.mode,
            stage=stage,
            ajani_output=ajani_output,
        )
        hermes_output = self.hermes.validate(
            policy=policy_decision,
            stage=stage,
            ajani_output=ajani_output,
            minerva_output=minerva_output,
        )

        memory_snapshot = self.memory.update_after_run(
            project=request.project,
            stage=stage,
            ajani=ajani_output,
            minerva=minerva_output,
            hermes=hermes_output,
            intent=intent,
            user_input=request.user_input,
        )
        # Version in returned Ajani payload must match committed project state.
        ajani_output.version_tag = memory_snapshot.current_version

        return AtlasOrchestrateResponse(
            project=request.project,
            version=memory_snapshot.current_version,
            project_registry_entry=registry_entry,
            mode=request.mode,
            intent=intent,
            intent_reason=intent_reason,
            pipeline_stage=stage,
            validation_status=hermes_output.validation_status,
            ajani=ajani_output,
            minerva=minerva_output,
            hermes=hermes_output,
            project_memory=memory_snapshot,
        )

    def get_project_memory(self, project: str) -> ProjectMemorySnapshot:
        return self.memory.get_project(project)

    def list_projects(self) -> list[ProjectSummary]:
        return self.memory.list_projects()

    def reset_project(self, project: str) -> ProjectMemorySnapshot:
        return self.memory.reset_project(project)


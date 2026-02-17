"""
Base classes for ATLAS Project System
LEGO-style teaching: Big picture first, break into modules, one step at a time, checkpoint tests
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class ProjectStatus(Enum):
    CONCEPT = "concept"
    PROTOTYPE = "prototype"
    TESTING = "testing"
    REFINEMENT = "refinement"
    COMPLETE = "complete"


class StepType(Enum):
    LEARN = "learn"
    BUILD = "build"
    TEST = "test"
    CHECKPOINT = "checkpoint"
    REFLECT = "reflect"
    SIMULATE = "simulate"


@dataclass
class BuildStep:
    """Single instruction step - one action only, no overload"""
    id: str
    instruction: str
    step_type: StepType
    visual_ref: Optional[str] = None
    checkpoint_question: Optional[str] = None
    failure_scenario: Optional[str] = None
    parts_needed: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "instruction": self.instruction,
            "type": self.step_type.value,
            "visual_ref": self.visual_ref,
            "checkpoint_question": self.checkpoint_question,
            "failure_scenario": self.failure_scenario,
            "parts_needed": self.parts_needed
        }


@dataclass
class BuildModule:
    """Like a LEGO bag - one module at a time"""
    id: str
    name: str
    description: str
    steps: List[BuildStep]
    prerequisites: List[str] = field(default_factory=list)
    completion_test: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "prerequisites": self.prerequisites,
            "completion_test": self.completion_test,
            "step_count": len(self.steps)
        }


@dataclass
class ProjectPhase:
    """Major phase of a project (like Power Cell Phase 1-4)"""
    id: str
    name: str
    purpose: str
    modules: List[BuildModule]
    scope_notes: Optional[str] = None
    simulation_only: bool = False
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "purpose": self.purpose,
            "modules": [m.to_dict() for m in self.modules],
            "scope_notes": self.scope_notes,
            "simulation_only": self.simulation_only,
            "module_count": len(self.modules)
        }


@dataclass
class PersonaRole:
    """What each AI persona contributes to this project"""
    persona: str
    responsibilities: List[str]
    teaching_focus: List[str]
    
    def to_dict(self) -> dict:
        return {
            "persona": self.persona,
            "responsibilities": self.responsibilities,
            "teaching_focus": self.teaching_focus
        }


@dataclass
class SafetyConstraint:
    """Hard limits and boundaries for the project"""
    category: str
    constraint: str
    reason: str
    is_absolute: bool = True
    
    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "constraint": self.constraint,
            "reason": self.reason,
            "is_absolute": self.is_absolute
        }


@dataclass
class Project:
    """Complete project specification with LEGO-style build system"""
    id: str
    name: str
    purpose: str
    big_picture: str
    what_it_does_not_do: List[str]
    phases: List[ProjectPhase]
    persona_roles: List[PersonaRole]
    safety_constraints: List[SafetyConstraint]
    category: str
    status: ProjectStatus = ProjectStatus.CONCEPT
    related_fields: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "purpose": self.purpose,
            "big_picture": self.big_picture,
            "what_it_does_not_do": self.what_it_does_not_do,
            "phases": [p.to_dict() for p in self.phases],
            "persona_roles": [r.to_dict() for r in self.persona_roles],
            "safety_constraints": [c.to_dict() for c in self.safety_constraints],
            "category": self.category,
            "status": self.status.value,
            "related_fields": self.related_fields,
            "phase_count": len(self.phases)
        }
    
    def get_phase(self, phase_id: str) -> Optional[ProjectPhase]:
        for phase in self.phases:
            if phase.id == phase_id:
                return phase
        return None
    
    def get_persona_role(self, persona: str) -> Optional[PersonaRole]:
        for role in self.persona_roles:
            if role.persona.lower() == persona.lower():
                return role
        return None


class ProjectRegistry:
    """Central registry for all projects"""
    
    def __init__(self):
        self._projects: Dict[str, Project] = {}
    
    def register(self, project: Project):
        self._projects[project.id] = project
    
    def get(self, project_id: str) -> Optional[Project]:
        return self._projects.get(project_id)
    
    def list_all(self) -> List[dict]:
        return [
            {
                "id": p.id,
                "name": p.name,
                "purpose": p.purpose,
                "category": p.category,
                "status": p.status.value,
                "phase_count": len(p.phases)
            }
            for p in self._projects.values()
        ]
    
    def get_by_category(self, category: str) -> List[Project]:
        return [p for p in self._projects.values() if p.category == category]
    
    def get_for_persona(self, persona: str) -> List[Project]:
        """Get projects where this persona has a defined role"""
        results = []
        for project in self._projects.values():
            if project.get_persona_role(persona):
                results.append(project)
        return results


project_registry = ProjectRegistry()

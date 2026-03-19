"""
PRISM-7 SINGLE FILE BUILD
Paradox-Responsive Intelligence System Matrix

A monolithic, self-contained reasoning engine with 7 symbolic pillars:
  Origin   — candidate generation
  Shape    — structural formatting
  Current  — delivery routing
  Fracture — critique and challenge
  Drift    — confidence calibration
  Echo     — memory recall
  Paradox  — contradiction resolution

No external API key required. Uses internal heuristics.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


# ─────────────────────────────────────────────
# TYPES
# ─────────────────────────────────────────────

class PillarName(str, Enum):
    ORIGIN = "origin"
    SHAPE = "shape"
    CURRENT = "current"
    FRACTURE = "fracture"
    DRIFT = "drift"
    ECHO = "echo"
    PARADOX = "paradox"


@dataclass
class TaskPacket:
    id: str
    user_goal: str
    task_type: str
    constraints: List[str] = field(default_factory=list)
    urgency: str = "normal"
    emotional_context: str = "neutral"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Candidate:
    id: str
    source_pillar: PillarName
    title: str
    description: str
    novelty_score: float = 0.0
    feasibility_score: float = 0.0
    relevance_score: float = 0.0
    confidence_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChallengeReport:
    candidate_id: str
    contradictions: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    weak_points: List[str] = field(default_factory=list)
    unresolved_questions: List[str] = field(default_factory=list)


@dataclass
class MemoryShard:
    id: str
    summary: str
    semantic_tags: List[str]
    reuse_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParadoxFrame:
    issue: str
    pole_a: str
    pole_b: str
    coexistence_model: str
    recommended_resolution: str


@dataclass
class AuditEvent:
    phase: str
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionState:
    active_pillars: List[PillarName] = field(default_factory=list)
    candidates: List[Candidate] = field(default_factory=list)
    challenge_reports: List[ChallengeReport] = field(default_factory=list)
    recalled_memories: List[MemoryShard] = field(default_factory=list)
    paradox_frames: List[ParadoxFrame] = field(default_factory=list)
    audit_trail: List[AuditEvent] = field(default_factory=list)
    confidence: float = 0.0
    delivery_mode: str = "standard"
    final_output: Optional[str] = None


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def new_id() -> str:
    return str(uuid4())


def safe_lower(text: str) -> str:
    return (text or "").strip().lower()


def add_event(state: ExecutionState, phase: str, message: str, **metadata: Any) -> ExecutionState:
    state.audit_trail.append(AuditEvent(phase=phase, message=message, metadata=metadata))
    return state


def overlap_score(query: str, text: str) -> float:
    q_words = set(safe_lower(query).split())
    t_words = set(safe_lower(text).split())
    if not q_words or not t_words:
        return 0.0
    return len(q_words.intersection(t_words)) / max(len(q_words), 1)


# ─────────────────────────────────────────────
# MEMORY
# ─────────────────────────────────────────────

class MemoryStore:
    def __init__(self) -> None:
        self._items: List[MemoryShard] = [
            MemoryShard(
                id="mem-001",
                summary="A modular intelligence architecture with separate layers for idea generation, structuring, critique, and delivery.",
                semantic_tags=["architecture", "modular", "reasoning"],
                reuse_score=0.66,
            ),
            MemoryShard(
                id="mem-002",
                summary="A wheel-like cognitive system with symbolic pillars, contradiction handling, and adaptive routing.",
                semantic_tags=["wheel", "pillars", "paradox"],
                reuse_score=0.73,
            ),
            MemoryShard(
                id="mem-003",
                summary="A system that generates multiple candidate solutions, critiques them, and chooses the strongest path.",
                semantic_tags=["candidates", "critique", "selection"],
                reuse_score=0.69,
            ),
        ]

    def all(self) -> List[MemoryShard]:
        return self._items.copy()


class RecallEngine:
    def __init__(self) -> None:
        self.store = MemoryStore()

    def find_related(self, task: TaskPacket, top_k: int = 2) -> List[MemoryShard]:
        ranked: List[MemoryShard] = []
        for shard in self.store.all():
            score = max(shard.reuse_score, overlap_score(task.user_goal, shard.summary))
            ranked.append(
                MemoryShard(
                    id=shard.id,
                    summary=shard.summary,
                    semantic_tags=shard.semantic_tags,
                    reuse_score=score,
                    metadata=shard.metadata,
                )
            )
        ranked.sort(key=lambda s: s.reuse_score, reverse=True)
        return ranked[:top_k]


# ─────────────────────────────────────────────
# SCORING
# ─────────────────────────────────────────────

class CandidateScorer:
    def score(self, candidate: Candidate, task: TaskPacket) -> Candidate:
        desc = safe_lower(candidate.description)
        goal_words = safe_lower(task.user_goal).split()

        candidate.relevance_score = 0.9 if any(word in desc for word in goal_words[:6]) else 0.55
        candidate.feasibility_score = 0.82 if "workflow" in desc or "steps" in desc or "components" in desc else 0.64

        title = safe_lower(candidate.title)
        if "experimental" in title:
            candidate.novelty_score = 0.9
        elif "alternative" in title:
            candidate.novelty_score = 0.75
        else:
            candidate.novelty_score = 0.6

        risk = 0.2
        if "experimental" in desc or "unusual" in desc:
            risk = 0.42

        candidate.metadata["risk_score"] = risk
        candidate.confidence_score = round(
            (candidate.relevance_score * 0.35)
            + (candidate.feasibility_score * 0.35)
            + (candidate.novelty_score * 0.20)
            + ((1 - risk) * 0.10),
            3,
        )
        return candidate


class CritiqueAdjuster:
    def apply(self, candidate: Candidate, report: ChallengeReport) -> Candidate:
        penalty = 0.0
        penalty += min(len(report.risks) * 0.04, 0.12)
        penalty += min(len(report.weak_points) * 0.05, 0.15)
        penalty += min(len(report.contradictions) * 0.06, 0.18)
        candidate.confidence_score = round(max(0.0, candidate.confidence_score - penalty), 3)
        candidate.metadata["critique_penalty"] = round(penalty, 3)
        return candidate


# ─────────────────────────────────────────────
# PILLAR BASE
# ─────────────────────────────────────────────

class BasePillar(ABC):
    name: str = "base"

    @abstractmethod
    def run(self, task: TaskPacket, state: ExecutionState) -> ExecutionState:
        raise NotImplementedError


# ─────────────────────────────────────────────
# PILLARS
# ─────────────────────────────────────────────

class OriginPillar(BasePillar):
    name = "origin"

    def run(self, task: TaskPacket, state: ExecutionState) -> ExecutionState:
        goal = task.user_goal
        constraints = ", ".join(task.constraints) if task.constraints else "none"

        candidates = [
            Candidate(
                id=f"{task.id}-orig-1",
                source_pillar=PillarName.ORIGIN,
                title="Primary concept",
                description=(
                    f"Build a core architecture focused directly on: {goal}. "
                    f"Use a stable central controller with modular subsystems. "
                    f"Constraints considered: {constraints}."
                ),
            ),
            Candidate(
                id=f"{task.id}-orig-2",
                source_pillar=PillarName.ORIGIN,
                title="Alternative concept",
                description=(
                    f"Design an alternate route for: {goal}. "
                    f"Emphasize flexibility, layer separation, and easy expansion. "
                    f"Constraints considered: {constraints}."
                ),
            ),
            Candidate(
                id=f"{task.id}-orig-3",
                source_pillar=PillarName.ORIGIN,
                title="Experimental concept",
                description=(
                    f"Push a more unusual but still plausible architecture for: {goal}. "
                    f"Use symbolic routing, multi-pass reasoning, and inspectable states. "
                    f"Constraints considered: {constraints}."
                ),
            ),
        ]

        state.candidates.extend(candidates)
        add_event(state, self.name, f"Generated {len(candidates)} candidates.")
        return state


class ShapePillar(BasePillar):
    name = "shape"

    def run(self, task: TaskPacket, state: ExecutionState) -> ExecutionState:
        for candidate in state.candidates:
            candidate.description += (
                "\nStructured Output:"
                f"\n- concept: {candidate.title}"
                f"\n- task_type: {task.task_type}"
                f"\n- urgency: {task.urgency}"
                f"\n- components: core, routing, memory, scoring, delivery"
                f"\n- workflow: generate -> structure -> critique -> recall -> compare -> deliver"
                f"\n- next steps: prototype, test, refine"
            )
        add_event(state, self.name, "Structured all candidates.")
        return state


class FracturePillar(BasePillar):
    name = "fracture"

    def run(self, task: TaskPacket, state: ExecutionState) -> ExecutionState:
        state.challenge_reports.clear()

        for candidate in state.candidates:
            weak_points = [
                "Needs clearer success metrics.",
                "Needs a minimum viable implementation boundary.",
            ]
            risks = [
                f"May be too broad for task type '{task.task_type}'.",
                "Could become over-engineered if not scoped carefully.",
            ]
            contradictions: List[str] = []
            unresolved = [
                "Which component should be built first?",
                "How will performance be measured?",
            ]

            if "experimental" in safe_lower(candidate.title):
                risks.append("Experimental direction may reduce short-term feasibility.")
                contradictions.append("High novelty may conflict with rapid implementation.")

            state.challenge_reports.append(
                ChallengeReport(
                    candidate_id=candidate.id,
                    contradictions=contradictions,
                    risks=risks,
                    weak_points=weak_points,
                    unresolved_questions=unresolved,
                )
            )

        add_event(state, self.name, f"Produced {len(state.challenge_reports)} critique reports.")
        return state


class EchoPillar(BasePillar):
    name = "echo"

    def __init__(self) -> None:
        self.recall = RecallEngine()

    def run(self, task: TaskPacket, state: ExecutionState) -> ExecutionState:
        recalled = self.recall.find_related(task)
        state.recalled_memories.extend(recalled)
        add_event(state, self.name, f"Recalled {len(recalled)} memory shards.")
        return state


class ParadoxPillar(BasePillar):
    name = "paradox"

    def run(self, task: TaskPacket, state: ExecutionState) -> ExecutionState:
        if len(state.candidates) < 2:
            add_event(state, self.name, "Not enough candidates for paradox analysis.")
            return state

        top_titles = [c.title for c in state.candidates[:3]]
        frame = ParadoxFrame(
            issue=f"Task '{task.user_goal}' has multiple viable solution directions: {', '.join(top_titles)}.",
            pole_a="Bold novelty",
            pole_b="Practical feasibility",
            coexistence_model="Use a stable primary architecture while keeping one experimental branch for future testing.",
            recommended_resolution="Choose the highest-confidence candidate for the main build and preserve the strongest alternate as a backup path.",
        )
        state.paradox_frames.append(frame)
        add_event(state, self.name, "Created paradox frame.")
        return state


class CurrentPillar(BasePillar):
    name = "current"

    def run(self, task: TaskPacket, state: ExecutionState) -> ExecutionState:
        if task.urgency == "high":
            state.delivery_mode = "concise"
        elif task.task_type in {"design", "architecture", "system"}:
            state.delivery_mode = "structured"
        elif task.emotional_context in {"uncertain", "stressed"}:
            state.delivery_mode = "supportive"
        else:
            state.delivery_mode = "standard"

        add_event(state, self.name, f"Set delivery mode to '{state.delivery_mode}'.")
        return state


class DriftPillar(BasePillar):
    name = "drift"

    def run(self, task: TaskPacket, state: ExecutionState) -> ExecutionState:
        increment = 0.05 if state.candidates else 0.01
        state.confidence = min(1.0, state.confidence + increment)
        add_event(state, self.name, f"Adjusted system confidence to {state.confidence:.2f}.")
        return state


# ─────────────────────────────────────────────
# CORE / ROUTING
# ─────────────────────────────────────────────

class Router:
    def route(self, task: TaskPacket) -> List[PillarName]:
        route: List[PillarName] = [PillarName.ORIGIN, PillarName.SHAPE]

        if task.task_type in {"design", "planning", "architecture", "analysis", "system"}:
            route.append(PillarName.FRACTURE)

        if task.metadata.get("use_memory", True):
            route.append(PillarName.ECHO)

        route.extend([
            PillarName.PARADOX,
            PillarName.CURRENT,
            PillarName.DRIFT,
        ])
        return route


class ActivationPlanner:
    def build(self, task: TaskPacket, route: List[PillarName]) -> Dict[str, Any]:
        return {
            "task_id": task.id,
            "task_type": task.task_type,
            "route": [pillar.value for pillar in route],
            "constraint_count": len(task.constraints),
        }


class StopRules:
    def should_stop(self, state: ExecutionState) -> bool:
        return False


class Pipeline:
    def run(self, task: TaskPacket, state: ExecutionState, pillars: List[BasePillar]) -> ExecutionState:
        for pillar in pillars:
            add_event(state, "pipeline", f"Running pillar: {pillar.name}")
            state = pillar.run(task, state)
        return state


class ExecutiveCore:
    def __init__(self) -> None:
        self.router = Router()
        self.activation = ActivationPlanner()
        self.stop_rules = StopRules()
        self.pipeline = Pipeline()
        self.registry: Dict[PillarName, BasePillar] = {
            PillarName.ORIGIN: OriginPillar(),
            PillarName.SHAPE: ShapePillar(),
            PillarName.FRACTURE: FracturePillar(),
            PillarName.ECHO: EchoPillar(),
            PillarName.PARADOX: ParadoxPillar(),
            PillarName.CURRENT: CurrentPillar(),
            PillarName.DRIFT: DriftPillar(),
        }

    def run(self, task: TaskPacket) -> ExecutionState:
        state = ExecutionState()
        route = self.router.route(task)
        state.active_pillars = route.copy()

        plan = self.activation.build(task, route)
        add_event(state, "executive", "Activation plan built.", plan=plan)

        pillars = [self.registry[name] for name in route]
        state = self.pipeline.run(task, state, pillars)

        if self.stop_rules.should_stop(state):
            add_event(state, "executive", "Stop rule triggered.")

        return state


# ─────────────────────────────────────────────
# DELIVERY
# ─────────────────────────────────────────────

class ToneSelector:
    def choose(self, delivery_mode: str) -> str:
        mapping = {
            "concise": "direct",
            "structured": "architect",
            "supportive": "steady",
            "standard": "clear",
        }
        return mapping.get(delivery_mode, "clear")


class Formatter:
    def candidate_line(self, candidate: Candidate) -> str:
        risk = candidate.metadata.get("risk_score", 0.0)
        penalty = candidate.metadata.get("critique_penalty", 0.0)
        return (
            f"- {candidate.title} "
            f"(conf={candidate.confidence_score}, rel={candidate.relevance_score}, "
            f"feas={candidate.feasibility_score}, nov={candidate.novelty_score}, "
            f"risk={risk}, penalty={penalty})\n"
            f"  {candidate.description}"
        )

    def challenge_line(self, report: ChallengeReport) -> str:
        contradictions = ", ".join(report.contradictions) if report.contradictions else "none"
        return (
            f"- {report.candidate_id}\n"
            f"  Contradictions: {contradictions}\n"
            f"  Risks: {', '.join(report.risks)}\n"
            f"  Weak points: {', '.join(report.weak_points)}\n"
            f"  Open questions: {', '.join(report.unresolved_questions)}"
        )

    def memory_line(self, shard: MemoryShard) -> str:
        return f"- {shard.summary} (reuse={shard.reuse_score:.2f})"

    def paradox_line(self, frame: ParadoxFrame) -> str:
        return (
            f"- Issue: {frame.issue}\n"
            f"  Pole A: {frame.pole_a}\n"
            f"  Pole B: {frame.pole_b}\n"
            f"  Coexistence: {frame.coexistence_model}\n"
            f"  Resolution: {frame.recommended_resolution}"
        )


class Renderer:
    def __init__(self) -> None:
        self.formatter = Formatter()
        self.tone = ToneSelector()

    def render(self, task: TaskPacket, state: ExecutionState) -> str:
        tone = self.tone.choose(state.delivery_mode)
        lines: List[str] = []

        lines.append("PRISM-7 Result")
        lines.append(f"Goal: {task.user_goal}")
        lines.append(f"Task Type: {task.task_type}")
        lines.append(f"Delivery Mode: {state.delivery_mode}")
        lines.append(f"Tone Profile: {tone}")
        lines.append(f"Active Pillars: {', '.join(p.value for p in state.active_pillars)}")

        if state.candidates:
            lines.append("")
            lines.append("Candidates:")
            for candidate in state.candidates:
                lines.append(self.formatter.candidate_line(candidate))

        if state.challenge_reports:
            lines.append("")
            lines.append("Challenge Reports:")
            for report in state.challenge_reports:
                lines.append(self.formatter.challenge_line(report))

        if state.recalled_memories:
            lines.append("")
            lines.append("Echo Recall:")
            for shard in state.recalled_memories:
                lines.append(self.formatter.memory_line(shard))

        if state.paradox_frames:
            lines.append("")
            lines.append("Paradox Frames:")
            for frame in state.paradox_frames:
                lines.append(self.formatter.paradox_line(frame))

        if state.audit_trail:
            lines.append("")
            lines.append("Audit Trail:")
            for event in state.audit_trail:
                lines.append(f"- [{event.phase}] {event.message}")

        return "\n".join(lines)


class ResponseBuilder:
    def __init__(self) -> None:
        self.renderer = Renderer()

    def build(self, task: TaskPacket, state: ExecutionState) -> str:
        return self.renderer.render(task, state)


# ─────────────────────────────────────────────
# ENGINE
# ─────────────────────────────────────────────

class PrismEngine:
    def __init__(self) -> None:
        self.core = ExecutiveCore()
        self.scorer = CandidateScorer()
        self.adjuster = CritiqueAdjuster()
        self.builder = ResponseBuilder()

    def process(self, task: TaskPacket) -> str:
        state = self.core.run(task)

        for i, candidate in enumerate(state.candidates):
            state.candidates[i] = self.scorer.score(candidate, task)

        report_map = {report.candidate_id: report for report in state.challenge_reports}
        for i, candidate in enumerate(state.candidates):
            report = report_map.get(candidate.id)
            if report is not None:
                state.candidates[i] = self.adjuster.apply(candidate, report)

        state.candidates.sort(key=lambda c: c.confidence_score, reverse=True)
        output = self.builder.build(task, state)
        state.final_output = output
        return output

    def process_structured(self, task: TaskPacket) -> dict:
        """Return structured JSON instead of plain text."""
        state = self.core.run(task)

        for i, candidate in enumerate(state.candidates):
            state.candidates[i] = self.scorer.score(candidate, task)

        report_map = {r.candidate_id: r for r in state.challenge_reports}
        for i, candidate in enumerate(state.candidates):
            report = report_map.get(candidate.id)
            if report is not None:
                state.candidates[i] = self.adjuster.apply(candidate, report)

        state.candidates.sort(key=lambda c: c.confidence_score, reverse=True)

        return {
            "goal": task.user_goal,
            "task_type": task.task_type,
            "delivery_mode": state.delivery_mode,
            "confidence": state.confidence,
            "active_pillars": [p.value for p in state.active_pillars],
            "candidates": [
                {
                    "id": c.id,
                    "title": c.title,
                    "description": c.description,
                    "confidence_score": c.confidence_score,
                    "relevance_score": c.relevance_score,
                    "feasibility_score": c.feasibility_score,
                    "novelty_score": c.novelty_score,
                    "risk_score": c.metadata.get("risk_score", 0),
                    "critique_penalty": c.metadata.get("critique_penalty", 0),
                }
                for c in state.candidates
            ],
            "challenge_reports": [
                {
                    "candidate_id": r.candidate_id,
                    "contradictions": r.contradictions,
                    "risks": r.risks,
                    "weak_points": r.weak_points,
                    "unresolved_questions": r.unresolved_questions,
                }
                for r in state.challenge_reports
            ],
            "echo_recall": [
                {"id": m.id, "summary": m.summary, "reuse_score": m.reuse_score}
                for m in state.recalled_memories
            ],
            "paradox_frames": [
                {
                    "issue": f.issue,
                    "pole_a": f.pole_a,
                    "pole_b": f.pole_b,
                    "coexistence_model": f.coexistence_model,
                    "recommended_resolution": f.recommended_resolution,
                }
                for f in state.paradox_frames
            ],
            "audit_trail": [
                {"phase": e.phase, "message": e.message}
                for e in state.audit_trail
            ],
        }


# ─────────────────────────────────────────────
# STANDALONE DEMO
# ─────────────────────────────────────────────

def demo_task() -> TaskPacket:
    return TaskPacket(
        id=new_id(),
        user_goal="Design one large unified AI architecture for Cursor from all previous layered ideas",
        task_type="architecture",
        constraints=[
            "must be one big code file",
            "must be modular inside",
            "must be inspectable",
            "must be easy to expand later",
        ],
        urgency="normal",
        emotional_context="focused",
        metadata={"use_memory": True},
    )


def main() -> None:
    engine = PrismEngine()
    task = demo_task()
    result = engine.process(task)
    print(result)


if __name__ == "__main__":
    main()

"""
Task Router: Intent classification for incoming requests.

Detects what the user wants: code, debug, plan, write, design, study, build
Routes to appropriate agent pipeline.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple
import re


class TaskIntent(Enum):
    CODE = "code"
    DEBUG = "debug"
    PLAN = "plan"
    WRITE = "write"
    DESIGN = "design"
    STUDY = "study"
    BUILD = "build"
    RESEARCH = "research"
    EXECUTE = "execute"
    UNKNOWN = "unknown"


@dataclass
class ClassifiedTask:
    intent: TaskIntent
    confidence: float
    original_request: str
    keywords_matched: List[str]
    suggested_agent: str
    requires_veto: bool
    risk_level: str


class TaskRouter:
    INTENT_PATTERNS: Dict[TaskIntent, List[str]] = {
        TaskIntent.CODE: [
            r"\b(write|create|implement|code|function|class|method|script)\b",
            r"\b(python|javascript|typescript|rust|go|sql)\b",
            r"\b(api|endpoint|route|handler)\b",
        ],
        TaskIntent.DEBUG: [
            r"\b(fix|bug|error|crash|broken|issue|problem|debug)\b",
            r"\b(traceback|exception|stack|trace)\b",
            r"\b(not working|doesn't work|failed)\b",
        ],
        TaskIntent.PLAN: [
            r"\b(plan|design|architect|structure|outline|strategy)\b",
            r"\b(roadmap|timeline|breakdown|steps|phases)\b",
            r"\b(how (should|would|can) (i|we))\b",
        ],
        TaskIntent.WRITE: [
            r"\b(write|draft|compose|edit|revise|documentation)\b",
            r"\b(story|narrative|chapter|scene|dialogue)\b",
            r"\b(blog|article|essay|content)\b",
        ],
        TaskIntent.DESIGN: [
            r"\b(design|ui|ux|layout|wireframe|mockup)\b",
            r"\b(visual|aesthetic|style|theme|color)\b",
            r"\b(component|interface|screen)\b",
        ],
        TaskIntent.STUDY: [
            r"\b(learn|study|understand|explain|teach|tutorial)\b",
            r"\b(lesson|course|module|concept)\b",
            r"\b(how (does|do)|what (is|are))\b",
        ],
        TaskIntent.BUILD: [
            r"\b(build|make|construct|assemble|fabricate)\b",
            r"\b(hardware|circuit|robot|device|machine)\b",
            r"\b(3d print|cad|schematic)\b",
        ],
        TaskIntent.RESEARCH: [
            r"\b(research|find|search|look up|investigate)\b",
            r"\b(compare|analyze|evaluate|assess)\b",
            r"\b(what (options|alternatives)|which (is|are) best)\b",
        ],
        TaskIntent.EXECUTE: [
            r"\b(run|execute|perform|do|start|launch)\b",
            r"\b(test|simulate|try)\b",
            r"\b(now|immediately|go ahead)\b",
        ],
    }
    
    AGENT_MAPPING: Dict[TaskIntent, str] = {
        TaskIntent.CODE: "hermes",
        TaskIntent.DEBUG: "hermes",
        TaskIntent.PLAN: "ajani",
        TaskIntent.WRITE: "minerva",
        TaskIntent.DESIGN: "minerva",
        TaskIntent.STUDY: "ajani",
        TaskIntent.BUILD: "hermes",
        TaskIntent.RESEARCH: "ajani",
        TaskIntent.EXECUTE: "hermes",
        TaskIntent.UNKNOWN: "ajani",
    }
    
    RISK_INTENTS: set = {TaskIntent.CODE, TaskIntent.DEBUG, TaskIntent.EXECUTE, TaskIntent.BUILD}
    
    def __init__(self):
        self.compiled_patterns: Dict[TaskIntent, List[re.Pattern]] = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            self.compiled_patterns[intent] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]
    
    def classify(self, request: str) -> ClassifiedTask:
        scores: Dict[TaskIntent, Tuple[float, List[str]]] = {}
        
        for intent, patterns in self.compiled_patterns.items():
            matches = []
            for pattern in patterns:
                found = pattern.findall(request)
                matches.extend(found)
            
            if matches:
                score = len(matches) / len(patterns)
                scores[intent] = (min(score, 1.0), matches)
        
        if not scores:
            return ClassifiedTask(
                intent=TaskIntent.UNKNOWN,
                confidence=0.0,
                original_request=request,
                keywords_matched=[],
                suggested_agent=self.AGENT_MAPPING[TaskIntent.UNKNOWN],
                requires_veto=True,
                risk_level="low"
            )
        
        best_intent = max(scores.keys(), key=lambda k: scores[k][0])
        confidence, keywords = scores[best_intent]
        
        requires_veto = best_intent in self.RISK_INTENTS
        risk_level = "high" if best_intent in {TaskIntent.EXECUTE, TaskIntent.BUILD} else \
                    "medium" if best_intent in {TaskIntent.CODE, TaskIntent.DEBUG} else "low"
        
        return ClassifiedTask(
            intent=best_intent,
            confidence=confidence,
            original_request=request,
            keywords_matched=list(set(keywords))[:5],
            suggested_agent=self.AGENT_MAPPING[best_intent],
            requires_veto=requires_veto,
            risk_level=risk_level
        )
    
    def get_pipeline(self, task: ClassifiedTask) -> List[str]:
        if task.requires_veto:
            return ["ajani", "minerva", "hermes"]
        elif task.intent in {TaskIntent.PLAN, TaskIntent.RESEARCH, TaskIntent.STUDY}:
            return ["ajani", "minerva"]
        elif task.intent in {TaskIntent.WRITE, TaskIntent.DESIGN}:
            return ["minerva", "ajani"]
        else:
            return ["ajani", "minerva", "hermes"]

"""
Learning Loop: Post-task learning and memory formation.

After each task:
- Ajani compares outcome vs acceptance criteria
- Minerva scores ethical + risk alignment
- Hermes stores what worked, what broke, what to avoid

This creates a growing knowledge base that informs future decisions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
import json


class LessonType(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    NEAR_MISS = "near_miss"
    OPTIMIZATION = "optimization"
    SAFETY = "safety"
    PATTERN = "pattern"


@dataclass
class Lesson:
    lesson_id: str
    lesson_type: LessonType
    task_id: str
    title: str
    description: str
    what_worked: List[str] = field(default_factory=list)
    what_failed: List[str] = field(default_factory=list)
    what_to_avoid: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    confidence: float = 0.7
    times_applied: int = 0
    last_applied: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = "system"
    
    def to_dict(self) -> Dict:
        return {
            "lesson_id": self.lesson_id,
            "lesson_type": self.lesson_type.value,
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "what_worked": self.what_worked,
            "what_failed": self.what_failed,
            "what_to_avoid": self.what_to_avoid,
            "tags": self.tags,
            "confidence": self.confidence,
            "times_applied": self.times_applied,
            "last_applied": self.last_applied,
            "created_at": self.created_at,
            "created_by": self.created_by
        }


@dataclass
class TaskOutcome:
    task_id: str
    request: str
    acceptance_criteria: List[str]
    criteria_met: List[str]
    criteria_failed: List[str]
    overall_success: bool
    confidence_score: float
    risk_alignment: float
    ethical_score: float
    execution_results: List[Dict]
    duration_ms: float
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class LearningLoop:
    """
    Manages the learning process after each task.
    Extracts lessons and stores them for future reference.
    """
    
    def __init__(self):
        self.lessons: List[Lesson] = []
        self.outcomes: List[TaskOutcome] = []
        self._lesson_counter = 0
    
    def _generate_lesson_id(self) -> str:
        self._lesson_counter += 1
        return f"lesson_{self._lesson_counter}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def record_outcome(
        self,
        task_id: str,
        request: str,
        acceptance_criteria: List[str],
        criteria_met: List[str],
        criteria_failed: List[str],
        confidence_score: float,
        risk_alignment: float,
        ethical_score: float,
        execution_results: List[Dict],
        duration_ms: float
    ) -> TaskOutcome:
        """Record the outcome of a completed task."""
        outcome = TaskOutcome(
            task_id=task_id,
            request=request,
            acceptance_criteria=acceptance_criteria,
            criteria_met=criteria_met,
            criteria_failed=criteria_failed,
            overall_success=len(criteria_failed) == 0 and len(criteria_met) > 0,
            confidence_score=confidence_score,
            risk_alignment=risk_alignment,
            ethical_score=ethical_score,
            execution_results=execution_results,
            duration_ms=duration_ms
        )
        
        self.outcomes.append(outcome)
        return outcome
    
    def extract_lessons(self, outcome: TaskOutcome) -> List[Lesson]:
        """Extract lessons from a task outcome."""
        lessons = []
        
        if outcome.overall_success:
            lesson = Lesson(
                lesson_id=self._generate_lesson_id(),
                lesson_type=LessonType.SUCCESS,
                task_id=outcome.task_id,
                title=f"Successful approach for: {outcome.request[:50]}",
                description=f"Task completed with {len(outcome.criteria_met)} criteria met",
                what_worked=outcome.criteria_met[:5],
                what_failed=[],
                what_to_avoid=[],
                tags=self._extract_tags(outcome.request),
                confidence=outcome.confidence_score,
                created_by="learning_loop"
            )
            lessons.append(lesson)
        
        if outcome.criteria_failed:
            lesson = Lesson(
                lesson_id=self._generate_lesson_id(),
                lesson_type=LessonType.FAILURE,
                task_id=outcome.task_id,
                title=f"Failure analysis: {outcome.request[:50]}",
                description=f"{len(outcome.criteria_failed)} criteria failed",
                what_worked=outcome.criteria_met[:3],
                what_failed=outcome.criteria_failed[:5],
                what_to_avoid=self._derive_avoidance(outcome.criteria_failed),
                tags=self._extract_tags(outcome.request),
                confidence=0.8,
                created_by="learning_loop"
            )
            lessons.append(lesson)
        
        if outcome.risk_alignment < 0.7 and outcome.overall_success:
            lesson = Lesson(
                lesson_id=self._generate_lesson_id(),
                lesson_type=LessonType.NEAR_MISS,
                task_id=outcome.task_id,
                title=f"Near miss: {outcome.request[:50]}",
                description="Task succeeded but with elevated risk indicators",
                what_worked=outcome.criteria_met[:3],
                what_failed=[],
                what_to_avoid=["Proceeding with low risk alignment scores"],
                tags=["risk", "near_miss"] + self._extract_tags(outcome.request)[:3],
                confidence=0.9,
                created_by="minerva_review"
            )
            lessons.append(lesson)
        
        if outcome.ethical_score < 0.8:
            lesson = Lesson(
                lesson_id=self._generate_lesson_id(),
                lesson_type=LessonType.SAFETY,
                task_id=outcome.task_id,
                title=f"Ethical consideration: {outcome.request[:50]}",
                description="Task had ethical considerations that need attention",
                what_worked=[],
                what_failed=[],
                what_to_avoid=["Similar approaches without ethics review"],
                tags=["ethics", "safety"] + self._extract_tags(outcome.request)[:3],
                confidence=0.95,
                created_by="minerva_review"
            )
            lessons.append(lesson)
        
        for lesson in lessons:
            self.lessons.append(lesson)
        
        return lessons
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags from text."""
        keywords = [
            "code", "file", "database", "api", "security", "auth",
            "write", "read", "execute", "plan", "design", "test",
            "build", "deploy", "config", "user", "data", "error"
        ]
        
        text_lower = text.lower()
        return [kw for kw in keywords if kw in text_lower][:5]
    
    def _derive_avoidance(self, failures: List[str]) -> List[str]:
        """Derive what to avoid from failures."""
        avoidances = []
        for failure in failures[:3]:
            avoidances.append(f"Avoid: {failure[:100]}")
        return avoidances
    
    def find_relevant_lessons(
        self,
        query: str,
        limit: int = 5,
        lesson_type: Optional[LessonType] = None
    ) -> List[Lesson]:
        """Find lessons relevant to a query."""
        query_tags = self._extract_tags(query)
        query_lower = query.lower()
        
        scored_lessons = []
        for lesson in self.lessons:
            score = 0.0
            
            for tag in lesson.tags:
                if tag in query_tags:
                    score += 0.3
            
            for word in query_lower.split()[:10]:
                if word in lesson.title.lower() or word in lesson.description.lower():
                    score += 0.1
            
            score *= lesson.confidence
            
            if lesson_type and lesson.lesson_type != lesson_type:
                continue
            
            scored_lessons.append((score, lesson))
        
        scored_lessons.sort(key=lambda x: x[0], reverse=True)
        
        return [lesson for _, lesson in scored_lessons[:limit]]
    
    def get_lessons_for_ajani(self, task: str) -> str:
        """Get formatted lessons for Ajani to read before planning."""
        relevant = self.find_relevant_lessons(task, limit=3)
        
        if not relevant:
            return "No relevant past lessons found."
        
        formatted = ["Relevant lessons from past tasks:"]
        for lesson in relevant:
            formatted.append(f"""
--- {lesson.lesson_type.value.upper()}: {lesson.title} ---
What worked: {', '.join(lesson.what_worked[:3]) if lesson.what_worked else 'N/A'}
What to avoid: {', '.join(lesson.what_to_avoid[:3]) if lesson.what_to_avoid else 'N/A'}
Confidence: {lesson.confidence:.0%}
""")
        
        return "\n".join(formatted)
    
    def mark_lesson_applied(self, lesson_id: str):
        """Mark a lesson as having been applied."""
        for lesson in self.lessons:
            if lesson.lesson_id == lesson_id:
                lesson.times_applied += 1
                lesson.last_applied = datetime.now().isoformat()
                break
    
    def get_stats(self) -> Dict:
        """Get learning loop statistics."""
        type_counts = {}
        for lesson in self.lessons:
            lt = lesson.lesson_type.value
            type_counts[lt] = type_counts.get(lt, 0) + 1
        
        return {
            "total_lessons": len(self.lessons),
            "total_outcomes": len(self.outcomes),
            "lessons_by_type": type_counts,
            "avg_confidence": sum(l.confidence for l in self.lessons) / max(len(self.lessons), 1),
            "most_applied_lessons": [
                {"id": l.lesson_id, "title": l.title, "times": l.times_applied}
                for l in sorted(self.lessons, key=lambda x: x.times_applied, reverse=True)[:3]
            ]
        }


learning_loop = LearningLoop()

"""
State Tracker: Live internal model of project state.

Tracks:
- Project health score
- Task backlog
- Failure frequency
- Unresolved risks
- Confidence trends
- Technical debt indicators

Runs passively in background and feeds summaries to Ajani.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum
from collections import deque
import statistics


class HealthStatus(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class RiskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class UnresolvedRisk:
    risk_id: str
    description: str
    priority: RiskPriority
    source_task_id: str
    source_agent: str
    first_seen: str
    occurrences: int = 1
    mitigation: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "risk_id": self.risk_id,
            "description": self.description,
            "priority": self.priority.value,
            "source_task_id": self.source_task_id,
            "source_agent": self.source_agent,
            "first_seen": self.first_seen,
            "occurrences": self.occurrences,
            "mitigation": self.mitigation
        }


@dataclass
class TaskBacklogItem:
    task_id: str
    description: str
    priority: int
    created_at: str
    estimated_complexity: str
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "priority": self.priority,
            "created_at": self.created_at,
            "estimated_complexity": self.estimated_complexity,
            "dependencies": self.dependencies,
            "status": self.status
        }


@dataclass
class ConfidenceTrend:
    timestamp: str
    task_id: str
    agent: str
    confidence: float
    action: str


class StateTracker:
    """
    Maintains a live internal model of the project state.
    """
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        
        self.confidence_history: deque = deque(maxlen=max_history)
        self.failure_history: deque = deque(maxlen=max_history)
        self.success_history: deque = deque(maxlen=max_history)
        
        self.unresolved_risks: Dict[str, UnresolvedRisk] = {}
        self.task_backlog: Dict[str, TaskBacklogItem] = {}
        
        self.health_score: float = 1.0
        self.risk_trajectory: float = 0.0
        self.technical_debt_score: float = 0.0
        
        self._risk_counter = 0
        self._task_counter = 0
    
    def _generate_risk_id(self) -> str:
        self._risk_counter += 1
        return f"risk_{self._risk_counter}"
    
    def _generate_task_id(self) -> str:
        self._task_counter += 1
        return f"backlog_{self._task_counter}"
    
    def record_confidence(
        self,
        task_id: str,
        agent: str,
        confidence: float,
        action: str
    ):
        """Record a confidence data point."""
        trend = ConfidenceTrend(
            timestamp=datetime.now().isoformat(),
            task_id=task_id,
            agent=agent,
            confidence=confidence,
            action=action
        )
        self.confidence_history.append(trend)
        self._recalculate_health()
    
    def record_outcome(self, task_id: str, success: bool, details: str = ""):
        """Record task outcome for trend analysis."""
        entry = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        if success:
            self.success_history.append(entry)
        else:
            self.failure_history.append(entry)
        
        self._recalculate_health()
    
    def add_risk(
        self,
        description: str,
        priority: RiskPriority,
        source_task_id: str,
        source_agent: str,
        mitigation: Optional[str] = None
    ) -> UnresolvedRisk:
        """Add or update an unresolved risk."""
        for existing in self.unresolved_risks.values():
            if description.lower()[:50] == existing.description.lower()[:50]:
                existing.occurrences += 1
                if priority.value > existing.priority.value:
                    existing.priority = priority
                return existing
        
        risk_id = self._generate_risk_id()
        risk = UnresolvedRisk(
            risk_id=risk_id,
            description=description,
            priority=priority,
            source_task_id=source_task_id,
            source_agent=source_agent,
            first_seen=datetime.now().isoformat(),
            mitigation=mitigation
        )
        self.unresolved_risks[risk_id] = risk
        self._recalculate_health()
        return risk
    
    def resolve_risk(self, risk_id: str) -> bool:
        """Mark a risk as resolved."""
        if risk_id in self.unresolved_risks:
            del self.unresolved_risks[risk_id]
            self._recalculate_health()
            return True
        return False
    
    def add_backlog_item(
        self,
        description: str,
        priority: int = 5,
        estimated_complexity: str = "moderate",
        dependencies: List[str] = None
    ) -> TaskBacklogItem:
        """Add an item to the task backlog."""
        task_id = self._generate_task_id()
        item = TaskBacklogItem(
            task_id=task_id,
            description=description,
            priority=priority,
            created_at=datetime.now().isoformat(),
            estimated_complexity=estimated_complexity,
            dependencies=dependencies or []
        )
        self.task_backlog[task_id] = item
        return item
    
    def complete_backlog_item(self, task_id: str) -> bool:
        """Mark a backlog item as complete."""
        if task_id in self.task_backlog:
            self.task_backlog[task_id].status = "completed"
            return True
        return False
    
    def _recalculate_health(self):
        """Recalculate overall health score."""
        factors = []
        
        if self.confidence_history:
            recent_confidences = [t.confidence for t in list(self.confidence_history)[-20:]]
            avg_confidence = statistics.mean(recent_confidences)
            factors.append(("confidence", avg_confidence, 0.3))
        
        total_outcomes = len(self.success_history) + len(self.failure_history)
        if total_outcomes > 0:
            success_rate = len(self.success_history) / total_outcomes
            factors.append(("success_rate", success_rate, 0.3))
        
        risk_penalty = min(len(self.unresolved_risks) * 0.1, 0.5)
        high_risk_count = sum(1 for r in self.unresolved_risks.values() 
                             if r.priority in [RiskPriority.HIGH, RiskPriority.CRITICAL])
        risk_penalty += high_risk_count * 0.15
        factors.append(("risk_penalty", 1.0 - risk_penalty, 0.25))
        
        backlog_penalty = min(len([t for t in self.task_backlog.values() 
                                   if t.status == "pending"]) * 0.02, 0.3)
        factors.append(("backlog_health", 1.0 - backlog_penalty, 0.15))
        
        if factors:
            weighted_sum = sum(score * weight for _, score, weight in factors)
            total_weight = sum(weight for _, _, weight in factors)
            self.health_score = max(0.0, min(1.0, weighted_sum / total_weight))
        
        if len(self.confidence_history) >= 10:
            recent = [t.confidence for t in list(self.confidence_history)[-5:]]
            older = [t.confidence for t in list(self.confidence_history)[-10:-5]]
            if older:
                self.risk_trajectory = statistics.mean(older) - statistics.mean(recent)
        
        self.technical_debt_score = (
            len(self.unresolved_risks) * 0.1 +
            len([t for t in self.task_backlog.values() if t.status == "pending"]) * 0.05
        )
    
    def get_health_status(self) -> HealthStatus:
        """Get current health status category."""
        if self.health_score >= 0.9:
            return HealthStatus.EXCELLENT
        elif self.health_score >= 0.75:
            return HealthStatus.GOOD
        elif self.health_score >= 0.5:
            return HealthStatus.FAIR
        elif self.health_score >= 0.25:
            return HealthStatus.POOR
        else:
            return HealthStatus.CRITICAL
    
    def get_confidence_trend(self, window: int = 10) -> Dict:
        """Get confidence trend analysis."""
        if not self.confidence_history:
            return {"trend": "no_data", "average": 0, "variance": 0}
        
        recent = list(self.confidence_history)[-window:]
        confidences = [t.confidence for t in recent]
        
        avg = statistics.mean(confidences)
        variance = statistics.variance(confidences) if len(confidences) > 1 else 0
        
        if len(confidences) >= 3:
            first_half = statistics.mean(confidences[:len(confidences)//2])
            second_half = statistics.mean(confidences[len(confidences)//2:])
            if second_half > first_half + 0.05:
                trend = "improving"
            elif second_half < first_half - 0.05:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "trend": trend,
            "average": avg,
            "variance": variance,
            "sample_size": len(confidences)
        }
    
    def get_failure_frequency(self, hours: int = 24) -> Dict:
        """Get failure frequency over time period."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        recent_failures = [
            f for f in self.failure_history
            if datetime.fromisoformat(f["timestamp"]) > cutoff
        ]
        
        recent_successes = [
            s for s in self.success_history
            if datetime.fromisoformat(s["timestamp"]) > cutoff
        ]
        
        total = len(recent_failures) + len(recent_successes)
        
        return {
            "failures": len(recent_failures),
            "successes": len(recent_successes),
            "total": total,
            "failure_rate": len(recent_failures) / max(total, 1),
            "period_hours": hours
        }
    
    def get_summary_for_ajani(self) -> str:
        """Get a formatted summary for Ajani to use in planning."""
        health = self.get_health_status()
        trend = self.get_confidence_trend()
        failures = self.get_failure_frequency()
        
        high_risks = [r for r in self.unresolved_risks.values() 
                     if r.priority in [RiskPriority.HIGH, RiskPriority.CRITICAL]]
        
        pending_tasks = [t for t in self.task_backlog.values() if t.status == "pending"]
        
        summary = f"""
=== PROJECT STATE BRIEFING ===
Health: {health.value.upper()} ({self.health_score:.0%})
Confidence Trend: {trend['trend']} (avg: {trend['average']:.0%})
Recent Failures: {failures['failures']} in last {failures['period_hours']}h

Unresolved High-Priority Risks: {len(high_risks)}"""
        
        for risk in high_risks[:3]:
            summary += f"\n  - [{risk.priority.value}] {risk.description[:60]}"
        
        summary += f"\n\nPending Backlog Items: {len(pending_tasks)}"
        for task in sorted(pending_tasks, key=lambda t: t.priority)[:3]:
            summary += f"\n  - [P{task.priority}] {task.description[:50]}"
        
        if self.risk_trajectory > 0.1:
            summary += "\n\n⚠️ WARNING: Confidence is declining"
        
        return summary
    
    def get_full_state(self) -> Dict:
        """Get complete state for API."""
        return {
            "health": {
                "score": self.health_score,
                "status": self.get_health_status().value,
                "risk_trajectory": self.risk_trajectory,
                "technical_debt": self.technical_debt_score
            },
            "confidence_trend": self.get_confidence_trend(),
            "failure_frequency": self.get_failure_frequency(),
            "unresolved_risks": [r.to_dict() for r in self.unresolved_risks.values()],
            "task_backlog": [t.to_dict() for t in self.task_backlog.values()],
            "history_size": {
                "confidence": len(self.confidence_history),
                "successes": len(self.success_history),
                "failures": len(self.failure_history)
            }
        }


state_tracker = StateTracker()

"""
Decision Log: Structured storage for agent decisions.

Tracks:
- What decision was made
- Which agent made it
- Why (reasoning)
- What constraints were applied
- What the outcome was
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class DecisionType(Enum):
    PLAN = "plan"
    APPROVE = "approve"
    VETO = "veto"
    EXECUTE = "execute"
    CONSTRAINT = "constraint"
    DELEGATE = "delegate"
    CHECKPOINT = "checkpoint"
    ROLLBACK = "rollback"


@dataclass
class Decision:
    decision_id: str
    decision_type: DecisionType
    agent: str
    task_id: str
    description: str
    reasoning: str
    confidence: float
    constraints: List[str] = field(default_factory=list)
    outcome: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    parent_decision_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "decision_id": self.decision_id,
            "decision_type": self.decision_type.value,
            "agent": self.agent,
            "task_id": self.task_id,
            "description": self.description,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "constraints": self.constraints,
            "outcome": self.outcome,
            "created_at": self.created_at,
            "parent_decision_id": self.parent_decision_id
        }


class DecisionLog:
    def __init__(self):
        self.decisions: Dict[str, Decision] = {}
        self.task_decisions: Dict[str, List[str]] = {}
        self.agent_decisions: Dict[str, List[str]] = {}
        self.decision_count = 0
    
    def _generate_id(self) -> str:
        self.decision_count += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"dec_{timestamp}_{self.decision_count:04d}"
    
    def log(
        self,
        decision_type: DecisionType,
        agent: str,
        task_id: str,
        description: str,
        reasoning: str,
        confidence: float,
        constraints: List[str] = None,
        parent_decision_id: str = None
    ) -> Decision:
        decision_id = self._generate_id()
        
        decision = Decision(
            decision_id=decision_id,
            decision_type=decision_type,
            agent=agent,
            task_id=task_id,
            description=description,
            reasoning=reasoning,
            confidence=confidence,
            constraints=constraints or [],
            parent_decision_id=parent_decision_id
        )
        
        self.decisions[decision_id] = decision
        
        if task_id not in self.task_decisions:
            self.task_decisions[task_id] = []
        self.task_decisions[task_id].append(decision_id)
        
        if agent not in self.agent_decisions:
            self.agent_decisions[agent] = []
        self.agent_decisions[agent].append(decision_id)
        
        return decision
    
    def update_outcome(self, decision_id: str, outcome: str):
        if decision_id in self.decisions:
            self.decisions[decision_id].outcome = outcome
    
    def get_task_decisions(self, task_id: str) -> List[Decision]:
        decision_ids = self.task_decisions.get(task_id, [])
        return [self.decisions[did] for did in decision_ids]
    
    def get_agent_decisions(self, agent: str) -> List[Decision]:
        decision_ids = self.agent_decisions.get(agent, [])
        return [self.decisions[did] for did in decision_ids]
    
    def get_decision_chain(self, decision_id: str) -> List[Decision]:
        chain = []
        current_id = decision_id
        
        while current_id and current_id in self.decisions:
            decision = self.decisions[current_id]
            chain.insert(0, decision)
            current_id = decision.parent_decision_id
        
        return chain
    
    def get_vetoes(self) -> List[Decision]:
        return [
            d for d in self.decisions.values()
            if d.decision_type == DecisionType.VETO
        ]
    
    def get_stats(self) -> Dict:
        type_counts = {}
        for d in self.decisions.values():
            key = d.decision_type.value
            type_counts[key] = type_counts.get(key, 0) + 1
        
        agent_counts = {k: len(v) for k, v in self.agent_decisions.items()}
        
        return {
            "total_decisions": len(self.decisions),
            "by_type": type_counts,
            "by_agent": agent_counts,
            "tasks_tracked": len(self.task_decisions),
            "veto_count": len(self.get_vetoes())
        }
    
    def export(self) -> List[Dict]:
        return [d.to_dict() for d in self.decisions.values()]

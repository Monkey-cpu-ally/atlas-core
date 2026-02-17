"""
Action Logger: Records every operation in the multi-agent system.

Provides full audit trail for:
- Who (which agent) did what
- When it happened
- What inputs were provided
- What outputs were produced
- Whether it succeeded or failed
- Any lessons learned
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
import json
import hashlib


class ActionType(Enum):
    CLASSIFY = "classify"
    PLAN = "plan"
    REVIEW = "review"
    VETO = "veto"
    APPROVE = "approve"
    EXECUTE = "execute"
    VERIFY = "verify"
    MEMORY_WRITE = "memory_write"
    MEMORY_READ = "memory_read"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    CODE_RUN = "code_run"
    API_CALL = "api_call"


@dataclass
class ActionRecord:
    action_id: str
    action_type: ActionType
    agent: str
    timestamp: str
    session_id: str
    task_id: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    success: bool
    duration_ms: float
    error: Optional[str] = None
    parent_action_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "agent": self.agent,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "task_id": self.task_id,
            "inputs": self._safe_serialize(self.inputs),
            "outputs": self._safe_serialize(self.outputs),
            "success": self.success,
            "duration_ms": self.duration_ms,
            "error": self.error,
            "parent_action_id": self.parent_action_id,
            "metadata": self.metadata
        }
    
    def _safe_serialize(self, obj: Any, max_depth: int = 3) -> Any:
        if max_depth <= 0:
            return str(obj)[:100]
        
        if isinstance(obj, dict):
            return {k: self._safe_serialize(v, max_depth - 1) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._safe_serialize(item, max_depth - 1) for item in obj[:100]]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            if isinstance(obj, str) and len(obj) > 1000:
                return obj[:1000] + "..."
            return obj
        else:
            return str(obj)[:100]


class ActionLogger:
    def __init__(self, session_id: str = None):
        self.actions: List[ActionRecord] = []
        self.action_index: Dict[str, ActionRecord] = {}
        self.agent_stats: Dict[str, Dict[str, int]] = {}
        self.session_id = session_id or self._generate_id("session")
    
    def _generate_id(self, prefix: str) -> str:
        timestamp = datetime.now().isoformat()
        hash_input = f"{prefix}_{timestamp}_{len(self.actions)}"
        return f"{prefix}_{hashlib.sha256(hash_input.encode()).hexdigest()[:12]}"
    
    def log(
        self,
        action_type: ActionType,
        agent: str,
        task_id: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        success: bool,
        duration_ms: float,
        error: Optional[str] = None,
        parent_action_id: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> ActionRecord:
        action_id = self._generate_id("action")
        
        record = ActionRecord(
            action_id=action_id,
            action_type=action_type,
            agent=agent,
            timestamp=datetime.now().isoformat(),
            session_id=self.session_id,
            task_id=task_id,
            inputs=inputs,
            outputs=outputs,
            success=success,
            duration_ms=duration_ms,
            error=error,
            parent_action_id=parent_action_id,
            metadata=metadata or {}
        )
        
        self.actions.append(record)
        self.action_index[action_id] = record
        
        if agent not in self.agent_stats:
            self.agent_stats[agent] = {"total": 0, "success": 0, "failed": 0}
        
        self.agent_stats[agent]["total"] += 1
        if success:
            self.agent_stats[agent]["success"] += 1
        else:
            self.agent_stats[agent]["failed"] += 1
        
        return record
    
    def get_task_trace(self, task_id: str) -> List[ActionRecord]:
        return [a for a in self.actions if a.task_id == task_id]
    
    def get_agent_actions(self, agent: str) -> List[ActionRecord]:
        return [a for a in self.actions if a.agent == agent]
    
    def get_failed_actions(self) -> List[ActionRecord]:
        return [a for a in self.actions if not a.success]
    
    def get_action_chain(self, action_id: str) -> List[ActionRecord]:
        chain = []
        current = self.action_index.get(action_id)
        
        while current:
            chain.insert(0, current)
            if current.parent_action_id:
                current = self.action_index.get(current.parent_action_id)
            else:
                break
        
        return chain
    
    def get_session_summary(self) -> Dict:
        total_actions = len(self.actions)
        successful = sum(1 for a in self.actions if a.success)
        failed = total_actions - successful
        
        action_type_counts = {}
        for action in self.actions:
            key = action.action_type.value
            action_type_counts[key] = action_type_counts.get(key, 0) + 1
        
        total_duration = sum(a.duration_ms for a in self.actions)
        
        return {
            "session_id": self.session_id,
            "total_actions": total_actions,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total_actions if total_actions > 0 else 1.0,
            "action_types": action_type_counts,
            "agent_stats": self.agent_stats,
            "total_duration_ms": total_duration,
            "first_action": self.actions[0].timestamp if self.actions else None,
            "last_action": self.actions[-1].timestamp if self.actions else None
        }
    
    def export_log(self) -> str:
        return json.dumps([a.to_dict() for a in self.actions], indent=2)
    
    def get_lessons_learned(self) -> List[Dict]:
        lessons = []
        
        failed_actions = self.get_failed_actions()
        for action in failed_actions:
            lessons.append({
                "type": "failure",
                "action_type": action.action_type.value,
                "agent": action.agent,
                "error": action.error,
                "context": {
                    "task_id": action.task_id,
                    "inputs_summary": list(action.inputs.keys())
                }
            })
        
        for agent, stats in self.agent_stats.items():
            if stats["total"] > 0:
                success_rate = stats["success"] / stats["total"]
                if success_rate < 0.8:
                    lessons.append({
                        "type": "performance",
                        "agent": agent,
                        "success_rate": success_rate,
                        "recommendation": f"Agent {agent} has low success rate, consider reviewing its prompts or capabilities"
                    })
        
        return lessons

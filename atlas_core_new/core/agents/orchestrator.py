"""
Agent Orchestrator: The core execution loop.

Implements the full pipeline:
1. Intake: User request → classify (code/research/design/story/build)
2. Ajani: Breaks into steps + acceptance criteria
3. Minerva: Risk check + veto or approve with constraints
4. Hermes: Executes tools, commits changes, produces artifacts
5. Review: Ajani verifies outputs match criteria
6. Memory write: Store what worked, what failed, decisions, version tags

The "never break this" rules:
- Minerva must be able to veto
- Hermes can't run dangerous actions without Ajani + Minerva sign-off
- Every action gets logged
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
import json

from .base_agent import AgentRole, AgentResponse
from .ajani import AjaniAgent
from .minerva import MinervaAgent
from .hermes import HermesAgent
from ..kernel.task_router import TaskRouter, ClassifiedTask
from ..kernel.action_logger import ActionLogger, ActionType
from ..kernel.tool_runner import ToolRunner
from ..kernel.checkpoint import GitCheckpointSystem, CheckpointType, checkpoint_system
from ..kernel.file_ops import FileOperations
from ..memory.decision_log import DecisionLog, DecisionType
from ..memory.learning_loop import LearningLoop, learning_loop
from ..memory.state_tracker import StateTracker, state_tracker, RiskPriority


class ExecutionStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    REVIEWING = "reviewing"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMPLETE = "complete"
    VETOED = "vetoed"
    FAILED = "failed"


@dataclass
class TaskExecution:
    task_id: str
    original_request: str
    classification: ClassifiedTask
    status: ExecutionStatus
    responses: List[AgentResponse] = field(default_factory=list)
    artifacts: List[Dict] = field(default_factory=list)
    lessons_learned: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    veto_reason: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "original_request": self.original_request,
            "classification": {
                "intent": self.classification.intent.value,
                "confidence": self.classification.confidence,
                "risk_level": self.classification.risk_level
            },
            "status": self.status.value,
            "responses": [r.to_dict() for r in self.responses],
            "artifacts": self.artifacts,
            "lessons_learned": self.lessons_learned,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "veto_reason": self.veto_reason
        }


class AgentOrchestrator:
    def __init__(self, session_id: str = None):
        self.task_router = TaskRouter()
        self.action_logger = ActionLogger(session_id)
        self.decision_log = DecisionLog()
        self.tool_runner = ToolRunner()
        self.file_ops = FileOperations()
        
        self.ajani = AjaniAgent()
        self.minerva = MinervaAgent()
        self.hermes = HermesAgent()
        
        self.hermes.attach_tools(self.tool_runner, self.file_ops, self.action_logger)
        
        self.agents = {
            AgentRole.AJANI: self.ajani,
            AgentRole.MINERVA: self.minerva,
            AgentRole.HERMES: self.hermes
        }
        
        self.executions: Dict[str, TaskExecution] = {}
        self.memory_store: List[Dict] = []
        self.execution_count = 0
    
    def _generate_task_id(self) -> str:
        self.execution_count += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"task_{timestamp}_{self.execution_count:04d}"
    
    async def execute(self, request: str, user_context: Dict[str, Any] = None) -> TaskExecution:
        task_id = self._generate_task_id()
        
        start_time = datetime.now()
        classification = self.task_router.classify(request)
        
        self.action_logger.log(
            action_type=ActionType.CLASSIFY,
            agent="router",
            task_id=task_id,
            inputs={"request": request},
            outputs={"intent": classification.intent.value, "confidence": classification.confidence},
            success=True,
            duration_ms=(datetime.now() - start_time).total_seconds() * 1000
        )
        
        execution = TaskExecution(
            task_id=task_id,
            original_request=request,
            classification=classification,
            status=ExecutionStatus.PENDING
        )
        self.executions[task_id] = execution
        
        relevant_lessons = learning_loop.get_lessons_for_ajani(request)
        project_state = state_tracker.get_summary_for_ajani()
        
        context = {
            "intent": classification.intent.value,
            "risk_level": classification.risk_level,
            "keywords": classification.keywords_matched,
            "requires_approval": classification.requires_veto,
            "past_lessons": relevant_lessons,
            "project_state": project_state,
            "has_similar_tasks": "No relevant" not in relevant_lessons,
            **(user_context or {})
        }
        
        pipeline = self.task_router.get_pipeline(classification)
        
        try:
            execution.status = ExecutionStatus.PLANNING
            ajani_response = await self._run_agent(
                AgentRole.AJANI, request, context, execution, []
            )
            execution.responses.append(ajani_response)
            
            self.decision_log.log(
                decision_type=DecisionType.PLAN,
                agent="ajani",
                task_id=task_id,
                description=f"Created plan for: {request[:100]}",
                reasoning=ajani_response.reasoning,
                confidence=ajani_response.confidence
            )
            
            if ajani_response.veto:
                execution.status = ExecutionStatus.VETOED
                execution.veto_reason = ajani_response.veto_reason
                execution.completed_at = datetime.now().isoformat()
                return execution
            
            execution.status = ExecutionStatus.REVIEWING
            minerva_response = await self._run_agent(
                AgentRole.MINERVA, request, context, execution, execution.responses
            )
            execution.responses.append(minerva_response)
            
            if minerva_response.veto:
                execution.status = ExecutionStatus.VETOED
                execution.veto_reason = minerva_response.veto_reason
                execution.completed_at = datetime.now().isoformat()
                
                self.decision_log.log(
                    decision_type=DecisionType.VETO,
                    agent="minerva",
                    task_id=task_id,
                    description=f"Vetoed: {minerva_response.veto_reason}",
                    reasoning=minerva_response.reasoning,
                    confidence=minerva_response.confidence
                )
                
                self._write_to_memory(execution, "vetoed")
                return execution
            
            minerva_approved = not minerva_response.veto
            minerva_constraints = minerva_response.constraints
            
            self.decision_log.log(
                decision_type=DecisionType.APPROVE,
                agent="minerva",
                task_id=task_id,
                description="Approved for execution",
                reasoning=minerva_response.reasoning,
                confidence=minerva_response.confidence,
                constraints=minerva_constraints
            )
            
            requires_hermes = (
                "hermes" in pipeline or
                classification.intent.value in ["code", "debug", "execute", "build"]
            )
            
            if requires_hermes and minerva_approved:
                execution.status = ExecutionStatus.EXECUTING
                
                context["minerva_approved"] = True
                context["minerva_constraints"] = minerva_constraints
                
                hermes_response = await self._run_agent(
                    AgentRole.HERMES, request, context, execution, execution.responses
                )
                execution.responses.append(hermes_response)
                
                self.decision_log.log(
                    decision_type=DecisionType.EXECUTE,
                    agent="hermes",
                    task_id=task_id,
                    description=hermes_response.action,
                    reasoning=hermes_response.reasoning,
                    confidence=hermes_response.confidence,
                    constraints=minerva_constraints
                )
                
                if hermes_response.veto:
                    execution.status = ExecutionStatus.VETOED
                    execution.veto_reason = hermes_response.veto_reason
                    execution.completed_at = datetime.now().isoformat()
                    return execution
                
                for artifact in hermes_response.artifacts:
                    execution.artifacts.append(artifact)
            
            execution.status = ExecutionStatus.VERIFYING
            verify_context = {**context, "mode": "verify"}
            verify_response = await self._run_agent(
                AgentRole.AJANI, request, verify_context, execution, execution.responses
            )
            execution.responses.append(verify_response)
            
            execution.status = ExecutionStatus.COMPLETE
            execution.completed_at = datetime.now().isoformat()
            
            checkpoint = checkpoint_system.create_checkpoint(
                task_id=task_id,
                description=f"Completed: {request[:100]}",
                checkpoint_type=CheckpointType.TASK_SUCCESS,
                agent="orchestrator",
                create_tag=True
            )
            
            if checkpoint:
                execution.lessons_learned.append(f"Checkpoint created: {checkpoint.tag}")
                self.decision_log.log(
                    decision_type=DecisionType.CHECKPOINT,
                    agent="orchestrator",
                    task_id=task_id,
                    description=f"Created checkpoint {checkpoint.tag}",
                    reasoning=f"Task completed successfully, {len(checkpoint.files_changed)} files changed",
                    confidence=1.0
                )
            
            self._run_learning_loop(execution, request, context)
            
            state_tracker.record_outcome(task_id, True, f"Completed: {request[:100]}")
            
            self._write_to_memory(execution, "complete")
            
            return execution
            
        except Exception as e:
            execution.status = ExecutionStatus.FAILED
            execution.lessons_learned.append(f"Execution failed: {str(e)}")
            execution.completed_at = datetime.now().isoformat()
            
            self.action_logger.log(
                action_type=ActionType.EXECUTE,
                agent="orchestrator",
                task_id=task_id,
                inputs={"request": request},
                outputs={"error": str(e)},
                success=False,
                duration_ms=0,
                error=str(e)
            )
            
            return execution
    
    async def _run_agent(
        self,
        role: AgentRole,
        task: str,
        context: Dict[str, Any],
        execution: TaskExecution,
        previous_responses: List[AgentResponse]
    ) -> AgentResponse:
        agent = self.agents[role]
        start_time = datetime.now()
        
        try:
            response = await agent.process(task, context, previous_responses)
            
            action_type = ActionType.PLAN if role == AgentRole.AJANI else \
                         ActionType.REVIEW if role == AgentRole.MINERVA else \
                         ActionType.EXECUTE
            
            if response.veto:
                action_type = ActionType.VETO
            
            self.action_logger.log(
                action_type=action_type,
                agent=role.value,
                task_id=execution.task_id,
                inputs={"task": task[:500], "context_keys": list(context.keys())},
                outputs={"action": response.action, "confidence": response.confidence},
                success=not response.veto,
                duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                error=response.veto_reason if response.veto else None
            )
            
            state_tracker.record_confidence(
                task_id=execution.task_id,
                agent=role.value,
                confidence=response.confidence,
                action=response.action
            )
            
            if response.veto and response.veto_reason:
                state_tracker.add_risk(
                    description=response.veto_reason,
                    priority=RiskPriority.MEDIUM if role != AgentRole.MINERVA else RiskPriority.HIGH,
                    source_task_id=execution.task_id,
                    source_agent=role.value
                )
            
            return response
            
        except Exception as e:
            self.action_logger.log(
                action_type=ActionType.EXECUTE,
                agent=role.value,
                task_id=execution.task_id,
                inputs={"task": task[:500]},
                outputs={"error": str(e)},
                success=False,
                duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                error=str(e)
            )
            
            state_tracker.record_outcome(execution.task_id, False, str(e))
            
            return AgentResponse(
                agent=role,
                action="error",
                content=f"Agent error: {str(e)}",
                confidence=0,
                reasoning=f"Exception during processing: {str(e)}",
                veto=True,
                veto_reason=f"Agent {role.value} failed: {str(e)}"
            )
    
    def _write_to_memory(self, execution: TaskExecution, outcome: str):
        memory_entry = {
            "task_id": execution.task_id,
            "request_summary": execution.original_request[:200],
            "intent": execution.classification.intent.value,
            "outcome": outcome,
            "agents_involved": [r.agent.value for r in execution.responses],
            "key_decisions": [],
            "lessons": execution.lessons_learned,
            "timestamp": datetime.now().isoformat()
        }
        
        for resp in execution.responses:
            if resp.veto:
                memory_entry["key_decisions"].append({
                    "agent": resp.agent.value,
                    "decision": "veto",
                    "reason": resp.veto_reason
                })
            elif resp.constraints:
                memory_entry["key_decisions"].append({
                    "agent": resp.agent.value,
                    "decision": "approve_with_constraints",
                    "constraints": resp.constraints
                })
        
        self.memory_store.append(memory_entry)
        
        self.action_logger.log(
            action_type=ActionType.MEMORY_WRITE,
            agent="orchestrator",
            task_id=execution.task_id,
            inputs={"memory_type": "execution_record"},
            outputs={"entry_count": len(self.memory_store)},
            success=True,
            duration_ms=0
        )
    
    def get_session_summary(self) -> Dict:
        return {
            "total_executions": len(self.executions),
            "completed": sum(1 for e in self.executions.values() if e.status == ExecutionStatus.COMPLETE),
            "vetoed": sum(1 for e in self.executions.values() if e.status == ExecutionStatus.VETOED),
            "failed": sum(1 for e in self.executions.values() if e.status == ExecutionStatus.FAILED),
            "action_log_summary": self.action_logger.get_session_summary(),
            "memory_entries": len(self.memory_store),
            "lessons_learned": self.action_logger.get_lessons_learned()
        }
    
    def get_execution(self, task_id: str) -> Optional[TaskExecution]:
        return self.executions.get(task_id)
    
    def _run_learning_loop(
        self,
        execution: TaskExecution,
        request: str,
        context: Dict[str, Any]
    ):
        """Run the learning loop after task completion."""
        criteria_met = []
        criteria_failed = []
        confidence_scores = []
        risk_alignment = 0.7
        ethical_score = 0.8
        execution_results = []
        
        for resp in execution.responses:
            if resp.confidence_score:
                confidence_scores.append(resp.confidence_score.overall)
            else:
                confidence_scores.append(resp.confidence)
            
            if resp.agent == AgentRole.AJANI and resp.action == "verify":
                try:
                    import json
                    verification = json.loads(resp.content)
                    criteria_met.extend(verification.get("criteria_met", []))
                    criteria_failed.extend(verification.get("criteria_failed", []))
                except:
                    pass
            
            if resp.agent == AgentRole.MINERVA:
                try:
                    import json
                    review = json.loads(resp.content)
                    risk_assessment = review.get("risk_assessment", {})
                    risk_alignment = risk_assessment.get("safety_score", 0.7)
                    ethical_score = risk_assessment.get("ethics_score", 0.8)
                except:
                    pass
            
            if resp.agent == AgentRole.HERMES:
                try:
                    import json
                    exec_data = json.loads(resp.content)
                    execution_results.extend(exec_data.get("results", []))
                except:
                    pass
        
        avg_confidence = sum(confidence_scores) / max(len(confidence_scores), 1)
        
        acceptance_criteria = context.get("acceptance_criteria", criteria_met + criteria_failed)
        
        outcome = learning_loop.record_outcome(
            task_id=execution.task_id,
            request=request,
            acceptance_criteria=acceptance_criteria if acceptance_criteria else ["Task completion"],
            criteria_met=criteria_met if criteria_met else ["Task executed"],
            criteria_failed=criteria_failed,
            confidence_score=avg_confidence,
            risk_alignment=risk_alignment,
            ethical_score=ethical_score,
            execution_results=execution_results,
            duration_ms=0
        )
        
        lessons = learning_loop.extract_lessons(outcome)
        
        for lesson in lessons:
            execution.lessons_learned.append(f"[{lesson.lesson_type.value}] {lesson.title}")
    
    def search_memory(self, query: str) -> List[Dict]:
        results = []
        query_lower = query.lower()
        
        for entry in self.memory_store:
            if query_lower in entry.get("request_summary", "").lower():
                results.append(entry)
            elif query_lower in entry.get("intent", "").lower():
                results.append(entry)
        
        return results

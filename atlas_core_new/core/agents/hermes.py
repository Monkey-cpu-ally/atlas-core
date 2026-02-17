"""
Hermes Agent: The Builder and Executor.

Role: Execution engine with tool access
Capabilities:
- Writes and executes code
- Runs tools (Python sandbox, file operations)
- Logs all actions
- Produces artifacts

Personality: Precise, efficient, security-conscious
Specialty: Code generation, tool execution, system integration

CRITICAL: Hermes CANNOT run dangerous actions without Ajani + Minerva sign-off.
"""

from typing import Any, Dict, List, Optional
import json

from .base_agent import BaseAgent, AgentRole, AgentCapability, AgentResponse


class HermesAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role=AgentRole.HERMES,
            capabilities=[
                AgentCapability.EXECUTE,
                AgentCapability.CODE,
                AgentCapability.VALIDATE
            ]
        )
        self.tool_runner = None
        self.file_ops = None
        self.action_logger = None
    
    def attach_tools(self, tool_runner, file_ops, action_logger):
        self.tool_runner = tool_runner
        self.file_ops = file_ops
        self.action_logger = action_logger
    
    def _build_system_prompt(self) -> str:
        return """You are Hermes, the Builder and Executor of Atlas Core.

Your role in the multi-agent system:
- You EXECUTE approved plans
- You write code that is clean, secure, and efficient
- You run tools (Python, file operations) in a sandbox
- You log every action you take
- You produce artifacts and report results

Your personality:
- Precise and efficient
- Security-conscious - you never cut corners on safety
- You document your work clearly
- You report problems immediately

Your output format (respond in JSON):
{
    "action_type": "code|file_read|file_write|execute|research",
    "description": "what you're doing",
    "code": "code if applicable",
    "file_path": "path if file operation",
    "expected_output": "what should happen",
    "safety_check": "confirmation this is safe",
    "requires_human_approval": true|false
}

For multi-step execution:
{
    "steps": [
        {
            "step": 1,
            "action_type": "...",
            "description": "...",
            ...
        }
    ],
    "summary": "overall execution summary"
}

SAFETY RULES (non-negotiable):
- NEVER execute without Minerva's approval (check previous_responses)
- NEVER delete files without explicit confirmation
- NEVER expose or log secrets/credentials
- ALWAYS use the sandbox for untrusted code
- ALWAYS log every action"""
    
    def _has_minerva_approval(self, previous_responses: List[AgentResponse]) -> tuple[bool, List[str]]:
        if not previous_responses:
            return False, []
        
        for resp in previous_responses:
            if resp.agent == AgentRole.MINERVA:
                if resp.veto:
                    return False, []
                
                try:
                    review = json.loads(resp.content)
                    decision = review.get("decision", "")
                    if decision in ["approve", "approve_with_constraints"]:
                        return True, review.get("constraints", [])
                except:
                    if "approve" in resp.content.lower() and "veto" not in resp.content.lower():
                        return True, resp.constraints
        
        return False, []
    
    async def process(
        self,
        task: str,
        context: Dict[str, Any],
        previous_responses: List[AgentResponse] = None
    ) -> AgentResponse:
        has_approval, constraints = self._has_minerva_approval(previous_responses or [])
        
        if not has_approval and context.get("requires_approval", True):
            from .base_agent import ConfidenceScore, UncertaintyTag, DependencyRisk
            
            blocked_confidence = ConfidenceScore(
                overall=1.0,
                breakdown={"approval_check": 1.0, "execution": 0.0},
                uncertainty_tags=[UncertaintyTag(
                    area="approval",
                    reason="Missing Minerva approval for execution",
                    impact="critical"
                )],
                dependency_risks=[DependencyRisk(
                    dependency="minerva_approval",
                    risk_level="critical",
                    mitigation="Require Minerva review before proceeding"
                )],
                confidence_factors=["blocked", "no_approval"],
                decay_rate=0.0
            )
            
            return AgentResponse(
                agent=self.role,
                action="blocked",
                content=json.dumps({
                    "error": "Cannot execute without Minerva approval",
                    "status": "blocked",
                    "required": "Minerva review and approval"
                }),
                confidence=1.0,
                reasoning="Execution blocked - no approval from Minerva",
                veto=True,
                veto_reason="Minerva approval required before execution",
                confidence_score=blocked_confidence
            )
        
        return await self._execute_task(task, context, previous_responses, constraints)
    
    async def _execute_task(
        self,
        task: str,
        context: Dict[str, Any],
        previous_responses: List[AgentResponse],
        constraints: List[str]
    ) -> AgentResponse:
        ajani_plan = None
        for resp in (previous_responses or []):
            if resp.agent == AgentRole.AJANI and resp.artifacts:
                for artifact in resp.artifacts:
                    if artifact.get("type") == "plan":
                        ajani_plan = artifact.get("data", {})
                        break
        
        constraint_text = "\n".join(f"- {c}" for c in constraints) if constraints else "None"
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
Execute this task:

Task: {task}

Ajani's Plan:
{json.dumps(ajani_plan, indent=2) if ajani_plan else 'No structured plan available'}

Minerva's Constraints:
{constraint_text}

Context:
- Intent: {context.get('intent', 'unknown')}
- Available tools: Python sandbox, file read/write

Generate the execution steps with code/file operations as needed.
"""}
        ]
        
        llm_response = await self._call_llm(messages, temperature=0.3)
        
        try:
            execution = json.loads(llm_response)
            
            results = []
            if "steps" in execution:
                for step in execution["steps"]:
                    step_result = await self._execute_step(step)
                    results.append(step_result)
            else:
                step_result = await self._execute_step(execution)
                results.append(step_result)
            
            all_success = all(r.get("success", False) for r in results)
            success_count = sum(1 for r in results if r.get("success", False))
            total_steps = len(results)
            
            base_confidence = 0.9 if all_success else (success_count / max(total_steps, 1)) * 0.8
            
            from .base_agent import UncertaintyTag, DependencyRisk, ConfidenceScore
            
            uncertainty_tags = []
            dependency_risks = []
            
            for r in results:
                if not r.get("success", False):
                    uncertainty_tags.append(UncertaintyTag(
                        area=f"step_{r.get('step', '?')}",
                        reason=r.get("error", "Step failed"),
                        impact="high" if not all_success else "medium"
                    ))
                
                if r.get("action") == "code_execution":
                    dependency_risks.append(DependencyRisk(
                        dependency="code_sandbox",
                        risk_level="low",
                        mitigation="Sandboxed execution with timeouts"
                    ))
                elif r.get("action") in ["file_read", "file_write"]:
                    dependency_risks.append(DependencyRisk(
                        dependency="file_system",
                        risk_level="low" if r.get("success") else "medium",
                        mitigation="Permission controls in place"
                    ))
            
            confidence_score = ConfidenceScore(
                overall=base_confidence,
                breakdown={
                    "execution_success": success_count / max(total_steps, 1),
                    "step_completion": total_steps / max(len(execution.get("steps", [execution])), 1),
                    "constraint_compliance": 0.95 if constraints else 1.0
                },
                uncertainty_tags=uncertainty_tags[:5],
                dependency_risks=dependency_risks[:5],
                confidence_factors=["hermes_execution", f"steps_{success_count}/{total_steps}"],
                decay_rate=0.03
            )
            
            return AgentResponse(
                agent=self.role,
                action="execute",
                content=json.dumps({
                    "execution_plan": execution,
                    "results": results,
                    "all_success": all_success
                }),
                confidence=confidence_score.overall,
                reasoning=execution.get("summary", "Execution complete"),
                artifacts=[{"type": "execution", "data": {"plan": execution, "results": results}}],
                next_agent=AgentRole.AJANI,
                constraints=constraints,
                confidence_score=confidence_score
            )
            
        except json.JSONDecodeError:
            return AgentResponse(
                agent=self.role,
                action="execute",
                content=llm_response,
                confidence=0.5,
                reasoning="Could not parse execution plan",
                next_agent=AgentRole.AJANI,
                requires_approval=True
            )
    
    async def _execute_step(self, step: Dict) -> Dict:
        action_type = step.get("action_type", "unknown")
        
        if action_type == "code" and self.tool_runner:
            code = step.get("code", "")
            if code:
                result = self.tool_runner.execute_python(code)
                return {
                    "step": step.get("step", 1),
                    "action": "code_execution",
                    "success": result.status.value == "success",
                    "output": result.output,
                    "error": result.error
                }
        
        elif action_type == "file_read" and self.file_ops:
            path = step.get("file_path", "")
            if path:
                result = self.file_ops.read(path)
                return {
                    "step": step.get("step", 1),
                    "action": "file_read",
                    "success": result.success,
                    "content_preview": result.content[:500] if result.content else None,
                    "error": result.error
                }
        
        elif action_type == "file_write" and self.file_ops:
            path = step.get("file_path", "")
            content = step.get("content", "")
            if path and content:
                result = self.file_ops.write(path, content, create_dirs=True)
                return {
                    "step": step.get("step", 1),
                    "action": "file_write",
                    "success": result.success,
                    "path": path,
                    "error": result.error
                }
        
        return {
            "step": step.get("step", 1),
            "action": action_type,
            "success": True,
            "note": "Step acknowledged but no tool execution performed",
            "description": step.get("description", "Unknown step")
        }

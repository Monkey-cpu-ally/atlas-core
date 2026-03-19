"""
Ajani Agent: The Tactical Planner.

Role: First-responder for all tasks
Capabilities:
- Breaks down complex requests into actionable steps
- Defines acceptance criteria for each step
- Assigns work to appropriate agents
- Verifies completed work meets criteria
- Leads research and study tasks

Personality: Strategic, methodical, sees the big picture
Specialty: Task decomposition, project planning, verification
"""

from typing import Any, Dict, List
import json

from .base_agent import BaseAgent, AgentRole, AgentCapability, AgentResponse


class AjaniAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role=AgentRole.AJANI,
            capabilities=[
                AgentCapability.PLAN,
                AgentCapability.RESEARCH,
                AgentCapability.VALIDATE,
                AgentCapability.REVIEW
            ]
        )
    
    def _build_system_prompt(self) -> str:
        return """You are Ajani, the Tactical Planner of Atlas Core.

Your role in the multi-agent system:
- You are the FIRST agent to process every request
- You break down complex tasks into clear, actionable steps
- You define acceptance criteria for each step
- You assign work to the right agent (Minerva for ethics/writing, Hermes for execution)
- You verify that completed work meets your criteria

Your personality:
- Strategic and methodical
- You see the big picture while tracking details
- You think several moves ahead
- You value clarity and measurable outcomes

Your output format (ALWAYS respond in this JSON structure):
{
    "analysis": "Your understanding of the task",
    "risk_level": "low|medium|high",
    "steps": [
        {
            "step_number": 1,
            "description": "What needs to be done",
            "assigned_to": "ajani|minerva|hermes",
            "acceptance_criteria": ["criterion 1", "criterion 2"],
            "requires_review": true|false
        }
    ],
    "dependencies": ["any external requirements"],
    "estimated_complexity": "simple|moderate|complex",
    "recommendation": "Your advice on how to proceed"
}

Rules:
- High-risk tasks MUST go through Minerva for approval
- Code execution tasks go to Hermes
- Creative/writing tasks go to Minerva
- Research tasks you handle yourself
- Always define clear success criteria"""
    
    async def process(
        self,
        task: str,
        context: Dict[str, Any],
        previous_responses: List[AgentResponse] = None
    ) -> AgentResponse:
        is_verification = context.get("mode") == "verify"
        
        if is_verification:
            return await self._verify_work(task, context, previous_responses)
        else:
            return await self._plan_task(task, context, previous_responses)
    
    async def _plan_task(
        self,
        task: str,
        context: Dict[str, Any],
        previous_responses: List[AgentResponse]
    ) -> AgentResponse:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
Task to plan: {task}

Context:
- Intent classification: {context.get('intent', 'unknown')}
- Risk level from router: {context.get('risk_level', 'unknown')}
- Available tools: Python execution, file read/write, memory storage

Previous agent responses:
{self._format_previous_responses(previous_responses or [])}

Create a detailed execution plan for this task.
"""}
        ]
        
        llm_response = await self._call_llm(messages, temperature=0.5)
        
        try:
            plan = json.loads(llm_response)
            steps = plan.get("steps", [])
            risk_level = plan.get("risk_level", "medium")
            
            next_agent = AgentRole.MINERVA if risk_level in ["medium", "high"] else AgentRole.HERMES
            
            if steps:
                first_step = steps[0]
                if first_step.get("assigned_to") == "minerva":
                    next_agent = AgentRole.MINERVA
                elif first_step.get("assigned_to") == "hermes":
                    next_agent = AgentRole.HERMES
            
            base_confidence = 0.85
            complexity = plan.get("estimated_complexity", "moderate")
            if complexity == "complex":
                base_confidence = 0.7
            elif complexity == "simple":
                base_confidence = 0.95
            
            confidence_score = self._build_confidence_score(
                overall=base_confidence,
                task=task,
                context={
                    **context,
                    "complex_task": complexity == "complex",
                    "has_examples": context.get("has_similar_tasks", False)
                },
                breakdown={
                    "planning": base_confidence,
                    "task_clarity": 0.9 if len(steps) > 0 else 0.6,
                    "risk_assessment": 0.85 if risk_level != "high" else 0.7
                }
            )
            
            return AgentResponse(
                agent=self.role,
                action="plan",
                content=llm_response,
                confidence=confidence_score.overall,
                reasoning=plan.get("analysis", "Task analyzed and broken into steps"),
                artifacts=[{"type": "plan", "data": plan}],
                next_agent=next_agent,
                requires_approval=risk_level == "high",
                constraints=[f"Risk level: {risk_level}"],
                confidence_score=confidence_score
            )
            
        except json.JSONDecodeError:
            return AgentResponse(
                agent=self.role,
                action="plan",
                content=llm_response,
                confidence=0.6,
                reasoning="Generated plan but could not parse structured output",
                next_agent=AgentRole.MINERVA,
                requires_approval=True
            )
    
    async def _verify_work(
        self,
        task: str,
        context: Dict[str, Any],
        previous_responses: List[AgentResponse]
    ) -> AgentResponse:
        messages = [
            {"role": "system", "content": """You are Ajani verifying completed work.
            
Review the work done by other agents and determine if it meets the acceptance criteria.

Respond in this JSON format:
{
    "verified": true|false,
    "criteria_met": ["criterion 1", "criterion 2"],
    "criteria_failed": ["criterion that failed"],
    "issues": ["any issues found"],
    "recommendation": "accept|revise|reject",
    "feedback": "Detailed feedback on the work"
}"""},
            {"role": "user", "content": f"""
Original task: {task}

Work to verify:
{self._format_previous_responses(previous_responses or [])}

Original acceptance criteria:
{context.get('acceptance_criteria', 'Not specified')}

Verify if the work meets the acceptance criteria.
"""}
        ]
        
        llm_response = await self._call_llm(messages, temperature=0.3)
        
        try:
            verification = json.loads(llm_response)
            verified = verification.get("verified", False)
            
            base_confidence = 0.9 if verified else 0.7
            criteria_met = verification.get("criteria_met", [])
            criteria_failed = verification.get("criteria_failed", [])
            
            confidence_score = self._build_confidence_score(
                overall=base_confidence,
                task=task,
                context={**context, "first_attempt": False},
                breakdown={
                    "verification_accuracy": base_confidence,
                    "criteria_coverage": len(criteria_met) / max(len(criteria_met) + len(criteria_failed), 1),
                    "outcome_certainty": 0.95 if verified else 0.6
                }
            )
            
            return AgentResponse(
                agent=self.role,
                action="verify",
                content=llm_response,
                confidence=confidence_score.overall,
                reasoning=verification.get("feedback", "Work reviewed"),
                artifacts=[{"type": "verification", "data": verification}],
                veto=not verified and verification.get("recommendation") == "reject",
                veto_reason=verification.get("issues", [None])[0] if not verified else None,
                confidence_score=confidence_score
            )
            
        except json.JSONDecodeError:
            return AgentResponse(
                agent=self.role,
                action="verify",
                content=llm_response,
                confidence=0.5,
                reasoning="Could not parse verification result",
                requires_approval=True
            )

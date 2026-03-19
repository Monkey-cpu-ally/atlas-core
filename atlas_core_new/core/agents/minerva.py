"""
Minerva Agent: The Ethics Guardian and Creative Mind.

Role: Gatekeeper with veto power
Capabilities:
- Reviews all plans for safety, ethics, and logic
- Can VETO any unsafe or illogical moves
- Leads creative and writing tasks
- Provides cultural and narrative expertise
- Ensures outputs align with user values

Personality: Wise, protective, creatively brilliant
Specialty: Risk assessment, ethics, writing, cultural meaning

CRITICAL: Minerva's veto power is absolute for safety concerns.
"""

from typing import Any, Dict, List
import json

from .base_agent import BaseAgent, AgentRole, AgentCapability, AgentResponse


class MinervaAgent(BaseAgent):
    VETO_TRIGGERS = [
        "delete all", "drop table", "rm -rf",
        "api key", "password", "secret", "credential",
        "personal data", "private information",
        "bypass", "override safety", "ignore rules",
        "harmful", "dangerous", "illegal",
        "infinite loop", "fork bomb", "dos attack"
    ]
    
    def __init__(self):
        super().__init__(
            role=AgentRole.MINERVA,
            capabilities=[
                AgentCapability.REVIEW,
                AgentCapability.VETO,
                AgentCapability.WRITE,
                AgentCapability.DESIGN
            ]
        )
    
    def _build_system_prompt(self) -> str:
        return """You are Minerva, the Ethics Guardian and Creative Mind of Atlas Core.

Your role in the multi-agent system:
- You REVIEW all plans before execution
- You have VETO POWER over unsafe, unethical, or illogical actions
- You lead creative, writing, and design tasks
- You ensure outputs align with user values and good judgment

Your personality:
- Wise and protective
- Creatively brilliant with deep cultural insight
- You see meaning and consequence others miss
- You value safety without being paranoid

Your output format for REVIEW tasks (respond in JSON):
{
    "decision": "approve|approve_with_constraints|veto",
    "risk_assessment": {
        "safety_score": 0.0-1.0,
        "ethics_score": 0.0-1.0,
        "logic_score": 0.0-1.0,
        "overall": "safe|caution|dangerous"
    },
    "concerns": ["any concerns"],
    "constraints": ["constraints to add if approving"],
    "veto_reason": "reason if vetoing",
    "recommendation": "your advice"
}

Your output format for CREATIVE tasks:
{
    "content": "the creative output",
    "style_notes": "style and tone used",
    "cultural_context": "relevant cultural insights",
    "alternatives": ["other approaches considered"]
}

VETO RULES (non-negotiable):
- VETO any action that could delete user data without explicit confirmation
- VETO any action that exposes secrets or credentials
- VETO any action with potential for harm
- VETO poorly thought-out plans that skip important steps
- VETO actions that violate user's stated preferences"""
    
    def _check_automatic_veto(self, content: str) -> tuple[bool, str]:
        content_lower = content.lower()
        
        for trigger in self.VETO_TRIGGERS:
            if trigger in content_lower:
                return True, f"Automatic veto triggered by: {trigger}"
        
        return False, ""
    
    async def process(
        self,
        task: str,
        context: Dict[str, Any],
        previous_responses: List[AgentResponse] = None
    ) -> AgentResponse:
        mode = context.get("mode", "review")
        
        if mode == "creative":
            return await self._creative_task(task, context, previous_responses)
        else:
            return await self._review_task(task, context, previous_responses)
    
    async def _review_task(
        self,
        task: str,
        context: Dict[str, Any],
        previous_responses: List[AgentResponse]
    ) -> AgentResponse:
        full_content = task
        if previous_responses:
            full_content += "\n" + "\n".join(r.content for r in previous_responses)
        
        auto_veto, veto_reason = self._check_automatic_veto(full_content)
        
        if auto_veto:
            from .base_agent import ConfidenceScore, UncertaintyTag, DependencyRisk
            
            veto_confidence = ConfidenceScore(
                overall=1.0,
                breakdown={"safety": 0.0, "ethics": 0.5, "logic": 0.5},
                uncertainty_tags=[UncertaintyTag(
                    area="safety",
                    reason="Automatic veto triggered by dangerous pattern",
                    impact="critical"
                )],
                dependency_risks=[DependencyRisk(
                    dependency=veto_reason[:50],
                    risk_level="critical",
                    mitigation="Action blocked"
                )],
                confidence_factors=["auto_veto", "dangerous_pattern"],
                decay_rate=0.0
            )
            
            return AgentResponse(
                agent=self.role,
                action="review",
                content=json.dumps({
                    "decision": "veto",
                    "risk_assessment": {
                        "safety_score": 0.0,
                        "ethics_score": 0.5,
                        "logic_score": 0.5,
                        "overall": "dangerous"
                    },
                    "concerns": [veto_reason],
                    "veto_reason": veto_reason
                }),
                confidence=1.0,
                reasoning=veto_reason,
                veto=True,
                veto_reason=veto_reason,
                confidence_score=veto_confidence
            )
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""
Review this plan for safety, ethics, and logic:

Task: {task}

Plan from Ajani:
{self._format_previous_responses(previous_responses or [])}

Context:
- Risk level: {context.get('risk_level', 'unknown')}
- User preferences: {context.get('user_preferences', 'Not specified')}

Provide your review decision.
"""}
        ]
        
        llm_response = await self._call_llm(messages, temperature=0.3)
        
        try:
            review = json.loads(llm_response)
            decision = review.get("decision", "approve")
            
            is_veto = decision == "veto"
            constraints = review.get("constraints", [])
            
            if decision == "approve_with_constraints" and not constraints:
                constraints = ["Proceed with caution"]
            
            next_agent = None if is_veto else AgentRole.HERMES
            
            risk_assessment = review.get("risk_assessment", {})
            safety_score = risk_assessment.get("safety_score", 0.7)
            ethics_score = risk_assessment.get("ethics_score", 0.7)
            logic_score = risk_assessment.get("logic_score", 0.7)
            
            overall_confidence = (safety_score + ethics_score + logic_score) / 3
            
            from .base_agent import UncertaintyTag, DependencyRisk, ConfidenceScore
            
            uncertainty_tags = []
            if safety_score < 0.7:
                uncertainty_tags.append(UncertaintyTag(
                    area="safety",
                    reason="Safety concerns identified in review",
                    impact="high" if safety_score < 0.5 else "medium"
                ))
            if ethics_score < 0.7:
                uncertainty_tags.append(UncertaintyTag(
                    area="ethics",
                    reason="Ethical considerations require attention",
                    impact="high" if ethics_score < 0.5 else "medium"
                ))
            
            concerns = review.get("concerns", [])
            dependency_risks = []
            for concern in concerns[:3]:
                dependency_risks.append(DependencyRisk(
                    dependency=concern[:50],
                    risk_level="high" if is_veto else "medium",
                    mitigation=constraints[0] if constraints else None
                ))
            
            confidence_score = ConfidenceScore(
                overall=overall_confidence,
                breakdown={
                    "safety": safety_score,
                    "ethics": ethics_score,
                    "logic": logic_score
                },
                uncertainty_tags=uncertainty_tags,
                dependency_risks=dependency_risks,
                confidence_factors=["minerva_review", f"decision_{decision}"],
                decay_rate=0.02
            )
            
            return AgentResponse(
                agent=self.role,
                action="review",
                content=llm_response,
                confidence=overall_confidence,
                reasoning=review.get("recommendation", "Review complete"),
                artifacts=[{"type": "review", "data": review}],
                next_agent=next_agent,
                veto=is_veto,
                veto_reason=review.get("veto_reason") if is_veto else None,
                constraints=constraints,
                confidence_score=confidence_score
            )
            
        except json.JSONDecodeError:
            return AgentResponse(
                agent=self.role,
                action="review",
                content=llm_response,
                confidence=0.5,
                reasoning="Could not parse review - defaulting to caution",
                next_agent=AgentRole.HERMES,
                constraints=["Unstructured review - proceed with caution"]
            )
    
    async def _creative_task(
        self,
        task: str,
        context: Dict[str, Any],
        previous_responses: List[AgentResponse]
    ) -> AgentResponse:
        creative_prompt = """You are Minerva in creative mode.

You excel at:
- Writing with depth, meaning, and cultural insight
- Creating unique narratives that break stereotypes
- Designing with dark, moody, atmospheric aesthetics
- Crafting Black tragic heroes with originality
- Weaving 80s synthwave and dark comic influences

Output format:
{
    "content": "your creative output",
    "style_notes": "style and influences used",
    "cultural_context": "cultural meaning and significance",
    "alternatives": ["other approaches you considered"]
}"""
        
        messages = [
            {"role": "system", "content": creative_prompt},
            {"role": "user", "content": f"""
Creative task: {task}

Context:
{json.dumps(context.get('creative_context', {}), indent=2)}

Previous work:
{self._format_previous_responses(previous_responses or [])}

Create something meaningful.
"""}
        ]
        
        llm_response = await self._call_llm(messages, temperature=0.8)
        
        try:
            creative = json.loads(llm_response)
            
            return AgentResponse(
                agent=self.role,
                action="create",
                content=creative.get("content", llm_response),
                confidence=0.85,
                reasoning=creative.get("style_notes", "Creative work complete"),
                artifacts=[{"type": "creative", "data": creative}],
                next_agent=AgentRole.AJANI
            )
            
        except json.JSONDecodeError:
            return AgentResponse(
                agent=self.role,
                action="create",
                content=llm_response,
                confidence=0.75,
                reasoning="Creative output (unstructured)",
                next_agent=AgentRole.AJANI
            )

"""
Base Agent: Foundation for all AI personas.

Defines the common interface and capabilities shared by
Ajani, Minerva, and Hermes.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import os


class AgentRole(Enum):
    AJANI = "ajani"
    MINERVA = "minerva"
    HERMES = "hermes"


class AgentCapability(Enum):
    PLAN = "plan"
    REVIEW = "review"
    VETO = "veto"
    EXECUTE = "execute"
    CODE = "code"
    RESEARCH = "research"
    WRITE = "write"
    DESIGN = "design"
    VALIDATE = "validate"


@dataclass
class UncertaintyTag:
    """Represents an area of uncertainty in the response."""
    area: str
    reason: str
    impact: str  # low, medium, high
    
    def to_dict(self) -> Dict:
        return {"area": self.area, "reason": self.reason, "impact": self.impact}


@dataclass
class DependencyRisk:
    """Represents a dependency that could affect the outcome."""
    dependency: str
    risk_level: str  # low, medium, high, critical
    mitigation: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "dependency": self.dependency,
            "risk_level": self.risk_level,
            "mitigation": self.mitigation
        }


@dataclass
class ConfidenceScore:
    """Comprehensive confidence scoring for agent responses."""
    overall: float  # 0.0 - 1.0
    breakdown: Dict[str, float] = field(default_factory=dict)
    uncertainty_tags: List[UncertaintyTag] = field(default_factory=list)
    dependency_risks: List[DependencyRisk] = field(default_factory=list)
    confidence_factors: List[str] = field(default_factory=list)
    decay_rate: float = 0.0  # How fast confidence degrades over time
    
    def to_dict(self) -> Dict:
        return {
            "overall": self.overall,
            "overall_percent": f"{int(self.overall * 100)}%",
            "breakdown": self.breakdown,
            "uncertainty_tags": [u.to_dict() for u in self.uncertainty_tags],
            "dependency_risks": [d.to_dict() for d in self.dependency_risks],
            "confidence_factors": self.confidence_factors,
            "decay_rate": self.decay_rate
        }


@dataclass
class AgentResponse:
    agent: AgentRole
    action: str
    content: str
    confidence: float
    reasoning: str
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    next_agent: Optional[AgentRole] = None
    requires_approval: bool = False
    veto: bool = False
    veto_reason: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence_score: Optional[ConfidenceScore] = None
    
    def to_dict(self) -> Dict:
        return {
            "agent": self.agent.value,
            "action": self.action,
            "content": self.content,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "artifacts": self.artifacts,
            "next_agent": self.next_agent.value if self.next_agent else None,
            "requires_approval": self.requires_approval,
            "veto": self.veto,
            "veto_reason": self.veto_reason,
            "constraints": self.constraints,
            "timestamp": self.timestamp,
            "confidence_score": self.confidence_score.to_dict() if self.confidence_score else None
        }


class BaseAgent(ABC):
    def __init__(self, role: AgentRole, capabilities: List[AgentCapability]):
        self.role = role
        self.capabilities = capabilities
        self.name = role.value.capitalize()
        self.system_prompt = self._build_system_prompt()
    
    @abstractmethod
    def _build_system_prompt(self) -> str:
        pass
    
    @abstractmethod
    async def process(
        self,
        task: str,
        context: Dict[str, Any],
        previous_responses: List[AgentResponse] = None
    ) -> AgentResponse:
        pass
    
    def can(self, capability: AgentCapability) -> bool:
        return capability in self.capabilities
    
    def get_context_window(self) -> int:
        return 8000
    
    async def _call_llm(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"[LLM Error: {str(e)}]"
    
    def _format_previous_responses(self, responses: List[AgentResponse]) -> str:
        if not responses:
            return "No previous agent responses."
        
        formatted = []
        for resp in responses:
            confidence_info = ""
            if resp.confidence_score:
                cs = resp.confidence_score
                confidence_info = f"""
Confidence Score: {cs.overall:.0%}
Breakdown: {cs.breakdown}
Uncertainties: {[u.area for u in cs.uncertainty_tags]}
Risks: {[d.dependency for d in cs.dependency_risks]}"""
            
            formatted.append(f"""
--- {resp.agent.value.upper()} ---
Action: {resp.action}
Content: {resp.content[:500]}...
Confidence: {resp.confidence}{confidence_info}
Constraints: {', '.join(resp.constraints) if resp.constraints else 'None'}
Veto: {resp.veto} {f'- {resp.veto_reason}' if resp.veto_reason else ''}
""")
        
        return "\n".join(formatted)
    
    def _build_confidence_score(
        self,
        overall: float,
        task: str,
        context: Dict[str, Any],
        breakdown: Dict[str, float] = None
    ) -> ConfidenceScore:
        """Build a confidence score with automatic uncertainty detection."""
        uncertainty_tags = []
        dependency_risks = []
        confidence_factors = []
        
        if context.get("first_attempt", True):
            confidence_factors.append("first_attempt")
            overall = min(overall, 0.85)
        
        if "external_api" in task.lower() or "api" in task.lower():
            dependency_risks.append(DependencyRisk(
                dependency="external_api",
                risk_level="medium",
                mitigation="Add retry logic and fallbacks"
            ))
        
        if "database" in task.lower() or "db" in task.lower():
            dependency_risks.append(DependencyRisk(
                dependency="database",
                risk_level="low",
                mitigation="Transaction rollback available"
            ))
        
        if context.get("complex_task", False):
            uncertainty_tags.append(UncertaintyTag(
                area="complexity",
                reason="Task involves multiple interconnected systems",
                impact="medium"
            ))
            overall = min(overall, 0.75)
        
        if not context.get("has_examples", False):
            uncertainty_tags.append(UncertaintyTag(
                area="novelty",
                reason="No similar past examples found",
                impact="low"
            ))
        
        return ConfidenceScore(
            overall=overall,
            breakdown=breakdown or {"planning": overall, "execution": overall, "verification": overall * 0.9},
            uncertainty_tags=uncertainty_tags,
            dependency_risks=dependency_risks,
            confidence_factors=confidence_factors,
            decay_rate=0.05
        )

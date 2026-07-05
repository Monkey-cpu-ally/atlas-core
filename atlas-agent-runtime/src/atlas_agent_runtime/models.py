"""Agent models for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class AgentType(str, Enum):
    SPECIALIST = "specialist_agent"
    REVIEW = "review_agent"
    COUNCIL = "council_agent"
    TEACHING = "teaching_agent"
    RESEARCH = "research_agent"
    KNOWLEDGE = "knowledge_agent"
    OPERATIONS = "operations_agent"


@dataclass(slots=True)
class AgentIdentity:
    """Identity and operating scope for an ATLAS agent."""

    name: str
    role: str
    agent_type: AgentType
    primary_domains: list[str]
    permissions: list[str] = field(default_factory=list)
    available_tools: list[str] = field(default_factory=list)
    memory_scope: list[str] = field(default_factory=list)
    review_rules: list[str] = field(default_factory=list)
    agent_id: str = field(default_factory=lambda: str(uuid4()))


HERMES = AgentIdentity(
    name="Hermes",
    role="Engineering, software, robotics, manufacturing, and systems architect",
    agent_type=AgentType.SPECIALIST,
    primary_domains=["engineering", "software", "robotics", "electronics", "manufacturing"],
)

MINERVA = AgentIdentity(
    name="Minerva",
    role="Science, botany, medicine, environment, design, story, and education scholar",
    agent_type=AgentType.SPECIALIST,
    primary_domains=["biology", "botany", "medicine", "environment", "design", "storytelling"],
)

AJANI = AgentIdentity(
    name="Ajani",
    role="Strategy, risk, business, operations, economics, and mission planning lead",
    agent_type=AgentType.SPECIALIST,
    primary_domains=["strategy", "risk", "business", "operations", "economics", "planning"],
)

COUNCIL = AgentIdentity(
    name="Council",
    role="Final review and synthesis layer for major ATLAS decisions",
    agent_type=AgentType.COUNCIL,
    primary_domains=["review", "synthesis", "confidence", "tradeoffs", "next_action"],
)

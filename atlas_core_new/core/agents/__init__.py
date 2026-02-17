"""
Multi-Agent System: Ajani, Minerva, Hermes orchestration.

Role Authority Ladder (Wakanda rules):
- User (Root) - All authority
- Ajani (Planner/Architect) - Proposes plans, decomposes tasks, assigns work  
- Minerva (Ethics/Meaning/Veto) - Can block unsafe/illogical moves
- Hermes (Builder/Security/Execution) - Writes code, runs tools, logs results

Core Loop:
1. Intake: user request → classify
2. Ajani: breaks into steps + acceptance criteria
3. Minerva: risk check + veto or approve with constraints
4. Hermes: executes tools, commits changes, produces artifacts
5. Review: Ajani verifies outputs match criteria
6. Memory write: store what worked, what failed, decisions
"""

from .base_agent import BaseAgent, AgentRole, AgentResponse
from .ajani import AjaniAgent
from .minerva import MinervaAgent
from .hermes import HermesAgent
from .orchestrator import AgentOrchestrator, TaskExecution

__all__ = [
    "BaseAgent", "AgentRole", "AgentResponse",
    "AjaniAgent", "MinervaAgent", "HermesAgent",
    "AgentOrchestrator", "TaskExecution"
]

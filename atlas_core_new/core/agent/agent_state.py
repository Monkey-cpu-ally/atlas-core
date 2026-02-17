"""
atlas_core/core/agent/agent_state.py

Agent state and orchestration loop.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class AgentState:
    last_persona: str = "ajani"
    last_style: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


class AgentLoop:
    """
    Orchestrates: input -> runner -> memory -> output
    """
    def __init__(self, state: AgentState, runners: Dict[str, Any]):
        self.state = state
        self.runners = runners

    def step(
        self,
        persona: str,
        user_text: str,
        style: Optional[str],
        mode: str,
        use_tools: bool,
        image_bytes: bytes | None = None,
    ) -> Dict[str, Any]:
        persona = persona.lower().strip()
        if persona not in self.runners:
            persona = "ajani"

        self.state.last_persona = persona
        self.state.last_style = style

        runner = self.runners[persona]
        return runner.run(user_text=user_text, style=style, mode=mode, use_tools=use_tools, image_bytes=image_bytes)

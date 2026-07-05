"""Agent runtime service for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass, field

try:
    from atlas_core_runtime.service import HealthReport, ServiceStatus
except ImportError:
    HealthReport = object  # type: ignore
    ServiceStatus = None  # type: ignore

from .models import AJANI, COUNCIL, HERMES, MINERVA, AgentIdentity


@dataclass
class AgentRuntimeService:
    """Registers and exposes ATLAS agent identities.

    This is not yet a full LLM runtime. It is the first service boundary for
    Hermes, Minerva, Ajani, and the Council.
    """

    name: str = "atlas-agent-runtime"
    version: str = "0.1.0"
    _agents: dict[str, AgentIdentity] = field(default_factory=dict)
    _running: bool = False

    def start(self) -> None:
        self._running = True
        for agent in (HERMES, MINERVA, AJANI, COUNCIL):
            self.register_agent(agent)

    def stop(self) -> None:
        self._running = False

    def register_agent(self, agent: AgentIdentity) -> AgentIdentity:
        self._agents.setdefault(agent.name, agent)
        return self._agents[agent.name]

    def get_agent(self, name: str) -> AgentIdentity:
        return self._agents[name]

    def list_agents(self) -> list[AgentIdentity]:
        return list(self._agents.values())

    def health_check(self):
        if ServiceStatus is None:
            return {"service_name": self.name, "status": "healthy" if self._running else "offline"}
        return HealthReport(
            service_name=self.name,
            status=ServiceStatus.HEALTHY if self._running else ServiceStatus.OFFLINE,
            message=f"{len(self._agents)} agents registered",
        )

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class MessageKind(str, Enum):
    STATUS = "status"
    REQUEST = "request"
    RESPONSE = "response"
    REVIEW = "review"
    DECISION = "decision"


@dataclass(slots=True, frozen=True)
class AgentMessage:
    sender: str
    recipient: str
    kind: MessageKind
    subject: str
    body: str
    project_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CouncilBus:
    def __init__(self) -> None:
        self._messages: list[AgentMessage] = []

    def publish(self, message: AgentMessage) -> AgentMessage:
        self._messages.append(message)
        return message

    def inbox(self, recipient: str, project_id: str | None = None) -> list[AgentMessage]:
        return [
            item for item in self._messages
            if item.recipient in {recipient, "Council"}
            and (project_id is None or item.project_id == project_id)
        ]

    def project_log(self, project_id: str) -> list[AgentMessage]:
        return [item for item in self._messages if item.project_id == project_id]

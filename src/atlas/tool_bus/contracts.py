"""ATLAS Tool Bus contracts.

These contracts define the safe interface between ATLAS agents and external tool
adapters. This module is scaffold-only and does not connect to live services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol
from uuid import uuid4


class ToolJobStatus(str, Enum):
    """Lifecycle status for a Tool Bus job."""

    CREATED = "created"
    VALIDATED = "validated"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class ToolSafetyLevel(str, Enum):
    """Safety level for a tool job."""

    READ_ONLY = "read_only"
    GENERATE_ONLY = "generate_only"
    SIMULATION_ONLY = "simulation_only"
    WRITE_LOCAL = "write_local"
    WRITE_REMOTE = "write_remote"
    DESTRUCTIVE = "destructive"


@dataclass(frozen=True)
class ToolCapability:
    """A capability exposed by a tool adapter."""

    name: str
    description: str
    safety_level: ToolSafetyLevel = ToolSafetyLevel.READ_ONLY
    requires_secret: bool = False
    enabled_by_default: bool = False


@dataclass
class ToolJob:
    """A request sent through the Tool Bus."""

    tool_name: str
    capability: str
    payload: Dict[str, Any]
    requested_by: str
    safety_level: ToolSafetyLevel = ToolSafetyLevel.READ_ONLY
    job_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolArtifact:
    """A file or structured object produced by a tool job."""

    name: str
    artifact_type: str
    path: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    """Standard result returned by every tool adapter."""

    success: bool
    status: ToolJobStatus
    job_id: str
    tool_name: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    execution_time_ms: Optional[int] = None
    logs: List[str] = field(default_factory=list)
    artifacts: List[ToolArtifact] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ToolAdapter(Protocol):
    """Protocol all Tool Bus adapters must follow."""

    name: str

    def initialize(self) -> None:
        """Initialize local adapter state without connecting to live tools."""

    def connect(self) -> None:
        """Connect to the underlying tool if the adapter is enabled."""

    def verify(self) -> bool:
        """Verify whether the tool is available and safe to use."""

    def get_capabilities(self) -> List[ToolCapability]:
        """Return the capabilities exposed by the adapter."""

    def get_status(self) -> Dict[str, Any]:
        """Return adapter status."""

    def execute(self, job: ToolJob) -> ToolResult:
        """Execute a Tool Bus job."""

    def cancel(self, job_id: str) -> ToolResult:
        """Cancel a running job if supported."""

    def disconnect(self) -> None:
        """Disconnect from the underlying tool."""

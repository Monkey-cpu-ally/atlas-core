"""Executor boundary for ATLAS Creative Studio.

Executors are registered explicitly by creative stage and capability. The registry
fails closed when a real executor is unavailable; queued jobs must never be marked
complete by fallback/placeholder generation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping


class ExecutorUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class ExecutionRequest:
    job_id: str
    project_id: str
    stage: str
    artifact_id: str | None = None
    payload: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class ExecutionResult:
    artifact_id: str | None
    output: Mapping[str, Any]
    executor: str


Executor = Callable[[ExecutionRequest], ExecutionResult]


class CreativeExecutorRegistry:
    """Small dependency-injection registry for real creative production services."""

    def __init__(self):
        self._executors: Dict[str, Executor] = {}

    def register(self, stage: str, executor: Executor) -> None:
        if not stage or not callable(executor):
            raise ValueError("stage and callable executor are required")
        self._executors[stage] = executor

    def unregister(self, stage: str) -> None:
        self._executors.pop(stage, None)

    def available(self, stage: str) -> bool:
        return stage in self._executors

    def capabilities(self) -> Dict[str, bool]:
        return {stage: self.available(stage) for stage in ("create", "critique", "revision", "master")}

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        executor = self._executors.get(request.stage)
        if executor is None:
            raise ExecutorUnavailable(f"no real creative executor registered for stage: {request.stage}")
        result = executor(request)
        if not isinstance(result, ExecutionResult):
            raise TypeError("creative executor must return ExecutionResult")
        return result


registry = CreativeExecutorRegistry()

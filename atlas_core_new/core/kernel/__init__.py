"""
Tool-Use Kernel: The execution gateway for Atlas Core multi-agent system.

This kernel transforms the AI personas from "talkers" into "doers" by providing:
- Task Router: Classifies intent (code, debug, plan, write, design, study)
- Safe Tool Runner: Python sandbox with timeouts and restrictions
- Action Logger: Records every operation with timestamps
- File Operations: Read/write with permissions
- Memory Writeback: Store decisions and lessons learned
"""

from .task_router import TaskRouter, TaskIntent
from .tool_runner import ToolRunner, ExecutionResult
from .action_logger import ActionLogger, ActionRecord
from .file_ops import FileOperations

__all__ = [
    "TaskRouter", "TaskIntent",
    "ToolRunner", "ExecutionResult",
    "ActionLogger", "ActionRecord",
    "FileOperations"
]

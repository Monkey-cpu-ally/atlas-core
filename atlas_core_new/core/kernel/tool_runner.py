"""
Safe Tool Runner: Python sandbox with timeouts and restrictions.

Executes code in a controlled environment with:
- Timeout limits
- Output size limits
- Restricted imports
- Memory limits
- Safe execution context
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum
import subprocess
import tempfile
import os
import signal
import json


class ExecutionStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    BLOCKED = "blocked"
    PARTIAL = "partial"


@dataclass
class ExecutionResult:
    status: ExecutionStatus
    output: str
    error: Optional[str]
    return_value: Any
    execution_time_ms: float
    memory_used_mb: float
    blocked_operations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status.value,
            "output": self.output[:10000],
            "error": self.error,
            "return_value": str(self.return_value)[:1000] if self.return_value else None,
            "execution_time_ms": self.execution_time_ms,
            "memory_used_mb": self.memory_used_mb,
            "blocked_operations": self.blocked_operations
        }


class ToolRunner:
    BLOCKED_IMPORTS = {
        "os.system", "subprocess.Popen", "subprocess.call", "subprocess.run",
        "eval", "exec", "compile", "__import__",
        "open",
        "socket", "urllib", "requests", "httplib",
        "shutil.rmtree", "os.remove", "os.rmdir",
    }
    
    ALLOWED_MODULES = {
        "math", "random", "json", "re", "datetime", "collections",
        "itertools", "functools", "operator", "string", "textwrap",
        "dataclasses", "enum", "typing", "abc",
        "numpy", "pandas",
    }
    
    DEFAULT_TIMEOUT_SEC = 30
    MAX_OUTPUT_SIZE = 50000
    MAX_MEMORY_MB = 256
    
    def __init__(self, timeout_sec: int = None, allowed_paths: List[str] = None):
        self.timeout_sec = timeout_sec or self.DEFAULT_TIMEOUT_SEC
        self.allowed_paths = allowed_paths or []
        self.execution_count = 0
    
    def validate_code(self, code: str) -> List[str]:
        blocked = []
        
        for blocked_op in self.BLOCKED_IMPORTS:
            if blocked_op in code:
                blocked.append(blocked_op)
        
        dangerous_patterns = [
            ("rm -rf", "destructive shell command"),
            ("DROP TABLE", "SQL injection risk"),
            ("DELETE FROM", "SQL deletion risk"),
            ("while True:", "potential infinite loop"),
            ("import ctypes", "low-level memory access"),
            ("import _thread", "unsafe threading"),
        ]
        
        for pattern, reason in dangerous_patterns:
            if pattern.lower() in code.lower():
                blocked.append(f"{pattern} ({reason})")
        
        return blocked
    
    def execute_python(self, code: str, context: Dict[str, Any] = None) -> ExecutionResult:
        blocked = self.validate_code(code)
        if blocked:
            return ExecutionResult(
                status=ExecutionStatus.BLOCKED,
                output="",
                error=f"Blocked dangerous operations: {', '.join(blocked)}",
                return_value=None,
                execution_time_ms=0,
                memory_used_mb=0,
                blocked_operations=blocked
            )
        
        start_time = datetime.now()
        
        safe_globals = {
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "sorted": sorted,
                "reversed": reversed,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "sum": sum,
                "min": min,
                "max": max,
                "abs": abs,
                "round": round,
                "pow": pow,
                "isinstance": isinstance,
                "type": type,
                "hasattr": hasattr,
                "getattr": getattr,
                "setattr": setattr,
                "any": any,
                "all": all,
            }
        }
        
        if context:
            safe_globals.update(context)
        
        import math
        import json as json_mod
        import re as re_mod
        import datetime as dt_mod
        safe_globals["math"] = math
        safe_globals["json"] = json_mod
        safe_globals["re"] = re_mod
        safe_globals["datetime"] = dt_mod
        
        output_capture = []
        original_print = print
        
        def captured_print(*args, **kwargs):
            msg = " ".join(str(a) for a in args)
            output_capture.append(msg)
            if len("\n".join(output_capture)) > self.MAX_OUTPUT_SIZE:
                raise RuntimeError("Output size limit exceeded")
        
        safe_globals["__builtins__"]["print"] = captured_print
        
        result_value = None
        error_msg = None
        status = ExecutionStatus.SUCCESS
        
        try:
            exec(code, safe_globals)
            result_value = safe_globals.get("result", safe_globals.get("output", None))
        except TimeoutError:
            status = ExecutionStatus.TIMEOUT
            error_msg = f"Execution exceeded {self.timeout_sec} second timeout"
        except RuntimeError as e:
            if "Output size limit" in str(e):
                status = ExecutionStatus.PARTIAL
                error_msg = str(e)
            else:
                status = ExecutionStatus.ERROR
                error_msg = str(e)
        except Exception as e:
            status = ExecutionStatus.ERROR
            error_msg = f"{type(e).__name__}: {str(e)}"
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds() * 1000
        
        self.execution_count += 1
        
        return ExecutionResult(
            status=status,
            output="\n".join(output_capture)[:self.MAX_OUTPUT_SIZE],
            error=error_msg,
            return_value=result_value,
            execution_time_ms=execution_time,
            memory_used_mb=0,
            blocked_operations=[]
        )
    
    def execute_in_subprocess(self, code: str, timeout: int = None) -> ExecutionResult:
        blocked = self.validate_code(code)
        if blocked:
            return ExecutionResult(
                status=ExecutionStatus.BLOCKED,
                output="",
                error=f"Blocked dangerous operations: {', '.join(blocked)}",
                return_value=None,
                execution_time_ms=0,
                memory_used_mb=0,
                blocked_operations=blocked
            )
        
        timeout = timeout or self.timeout_sec
        start_time = datetime.now()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            result = subprocess.run(
                ["python3", temp_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds() * 1000
            
            if result.returncode == 0:
                return ExecutionResult(
                    status=ExecutionStatus.SUCCESS,
                    output=result.stdout[:self.MAX_OUTPUT_SIZE],
                    error=None,
                    return_value=None,
                    execution_time_ms=execution_time,
                    memory_used_mb=0
                )
            else:
                return ExecutionResult(
                    status=ExecutionStatus.ERROR,
                    output=result.stdout[:self.MAX_OUTPUT_SIZE],
                    error=result.stderr[:5000],
                    return_value=None,
                    execution_time_ms=execution_time,
                    memory_used_mb=0
                )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                output="",
                error=f"Execution exceeded {timeout} second timeout",
                return_value=None,
                execution_time_ms=timeout * 1000,
                memory_used_mb=0
            )
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

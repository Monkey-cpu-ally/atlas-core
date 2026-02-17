"""
File Operations: Safe file read/write with permissions.

Provides controlled file access with:
- Allowed paths whitelist
- Blocked paths blacklist
- Size limits
- Extension restrictions
- Full audit logging
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from pathlib import Path
from datetime import datetime
import os
import hashlib


@dataclass
class FileOpResult:
    success: bool
    operation: str
    path: str
    content: Optional[str]
    error: Optional[str]
    size_bytes: int
    timestamp: str
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "operation": self.operation,
            "path": self.path,
            "content_preview": self.content[:500] if self.content else None,
            "content_length": len(self.content) if self.content else 0,
            "error": self.error,
            "size_bytes": self.size_bytes,
            "timestamp": self.timestamp
        }


class FileOperations:
    BLOCKED_PATHS = {
        "/etc", "/var", "/usr", "/bin", "/sbin", "/boot",
        "/root", "/home", "/sys", "/proc", "/dev",
        ".env", ".git", "node_modules", "__pycache__",
        ".ssh", ".aws", ".config"
    }
    
    BLOCKED_EXTENSIONS = {
        ".exe", ".dll", ".so", ".dylib",
        ".sh", ".bash", ".zsh",
        ".key", ".pem", ".crt", ".p12",
        ".env", ".secrets"
    }
    
    ALLOWED_EXTENSIONS = {
        ".py", ".js", ".ts", ".jsx", ".tsx",
        ".json", ".yaml", ".yml", ".toml",
        ".md", ".txt", ".rst",
        ".html", ".css", ".scss",
        ".sql", ".graphql",
        ".xml", ".csv",
        ".v", ".sv"
    }
    
    MAX_FILE_SIZE = 1024 * 1024
    MAX_READ_SIZE = 100 * 1024
    
    def __init__(self, base_path: str = None, allowed_paths: List[str] = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.allowed_paths = set(allowed_paths) if allowed_paths else set()
        self.operation_log: List[FileOpResult] = []
    
    def _is_path_allowed(self, path: str) -> tuple[bool, str]:
        try:
            resolved = Path(path).resolve()
            path_str = str(resolved)
            
            for blocked in self.BLOCKED_PATHS:
                if blocked in path_str:
                    return False, f"Path contains blocked directory: {blocked}"
            
            suffix = resolved.suffix.lower()
            if suffix in self.BLOCKED_EXTENSIONS:
                return False, f"File extension blocked: {suffix}"
            
            if suffix and suffix not in self.ALLOWED_EXTENSIONS:
                return False, f"File extension not in allowed list: {suffix}"
            
            if self.allowed_paths:
                allowed = False
                for allowed_base in self.allowed_paths:
                    if path_str.startswith(str(Path(allowed_base).resolve())):
                        allowed = True
                        break
                if not allowed:
                    return False, "Path not in allowed directories"
            
            return True, ""
            
        except Exception as e:
            return False, f"Path validation error: {str(e)}"
    
    def read(self, path: str) -> FileOpResult:
        allowed, error = self._is_path_allowed(path)
        
        if not allowed:
            result = FileOpResult(
                success=False,
                operation="read",
                path=path,
                content=None,
                error=error,
                size_bytes=0,
                timestamp=datetime.now().isoformat()
            )
            self.operation_log.append(result)
            return result
        
        try:
            resolved = Path(path).resolve()
            
            if not resolved.exists():
                result = FileOpResult(
                    success=False,
                    operation="read",
                    path=path,
                    content=None,
                    error="File does not exist",
                    size_bytes=0,
                    timestamp=datetime.now().isoformat()
                )
                self.operation_log.append(result)
                return result
            
            size = resolved.stat().st_size
            
            if size > self.MAX_READ_SIZE:
                with open(resolved, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read(self.MAX_READ_SIZE)
                content += f"\n... [TRUNCATED - file is {size} bytes, showing first {self.MAX_READ_SIZE}]"
            else:
                with open(resolved, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
            
            result = FileOpResult(
                success=True,
                operation="read",
                path=path,
                content=content,
                error=None,
                size_bytes=size,
                timestamp=datetime.now().isoformat()
            )
            self.operation_log.append(result)
            return result
            
        except Exception as e:
            result = FileOpResult(
                success=False,
                operation="read",
                path=path,
                content=None,
                error=str(e),
                size_bytes=0,
                timestamp=datetime.now().isoformat()
            )
            self.operation_log.append(result)
            return result
    
    def write(self, path: str, content: str, create_dirs: bool = False) -> FileOpResult:
        allowed, error = self._is_path_allowed(path)
        
        if not allowed:
            result = FileOpResult(
                success=False,
                operation="write",
                path=path,
                content=None,
                error=error,
                size_bytes=0,
                timestamp=datetime.now().isoformat()
            )
            self.operation_log.append(result)
            return result
        
        if len(content) > self.MAX_FILE_SIZE:
            result = FileOpResult(
                success=False,
                operation="write",
                path=path,
                content=None,
                error=f"Content exceeds maximum size ({len(content)} > {self.MAX_FILE_SIZE})",
                size_bytes=0,
                timestamp=datetime.now().isoformat()
            )
            self.operation_log.append(result)
            return result
        
        try:
            resolved = Path(path).resolve()
            
            if create_dirs:
                resolved.parent.mkdir(parents=True, exist_ok=True)
            
            with open(resolved, 'w', encoding='utf-8') as f:
                f.write(content)
            
            result = FileOpResult(
                success=True,
                operation="write",
                path=path,
                content=content[:500],
                error=None,
                size_bytes=len(content),
                timestamp=datetime.now().isoformat()
            )
            self.operation_log.append(result)
            return result
            
        except Exception as e:
            result = FileOpResult(
                success=False,
                operation="write",
                path=path,
                content=None,
                error=str(e),
                size_bytes=0,
                timestamp=datetime.now().isoformat()
            )
            self.operation_log.append(result)
            return result
    
    def list_dir(self, path: str) -> FileOpResult:
        allowed, error = self._is_path_allowed(path)
        
        if not allowed:
            result = FileOpResult(
                success=False,
                operation="list",
                path=path,
                content=None,
                error=error,
                size_bytes=0,
                timestamp=datetime.now().isoformat()
            )
            self.operation_log.append(result)
            return result
        
        try:
            resolved = Path(path).resolve()
            
            if not resolved.is_dir():
                result = FileOpResult(
                    success=False,
                    operation="list",
                    path=path,
                    content=None,
                    error="Not a directory",
                    size_bytes=0,
                    timestamp=datetime.now().isoformat()
                )
                self.operation_log.append(result)
                return result
            
            entries = []
            for entry in resolved.iterdir():
                entry_type = "dir" if entry.is_dir() else "file"
                size = entry.stat().st_size if entry.is_file() else 0
                entries.append(f"{entry_type}: {entry.name} ({size} bytes)")
            
            content = "\n".join(entries)
            
            result = FileOpResult(
                success=True,
                operation="list",
                path=path,
                content=content,
                error=None,
                size_bytes=len(content),
                timestamp=datetime.now().isoformat()
            )
            self.operation_log.append(result)
            return result
            
        except Exception as e:
            result = FileOpResult(
                success=False,
                operation="list",
                path=path,
                content=None,
                error=str(e),
                size_bytes=0,
                timestamp=datetime.now().isoformat()
            )
            self.operation_log.append(result)
            return result
    
    def get_operation_history(self) -> List[Dict]:
        return [op.to_dict() for op in self.operation_log]

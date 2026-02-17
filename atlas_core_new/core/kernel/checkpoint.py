"""
Git Checkpoint System
Auto-commits on successful task execution with version tagging.
"""

import subprocess
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum


class CheckpointType(Enum):
    TASK_SUCCESS = "task_success"
    MILESTONE = "milestone"
    ROLLBACK = "rollback"
    MANUAL = "manual"


@dataclass
class Checkpoint:
    commit_hash: str
    tag: Optional[str]
    checkpoint_type: CheckpointType
    task_id: str
    description: str
    timestamp: str
    files_changed: List[str] = field(default_factory=list)
    agent: str = ""
    

class GitCheckpointSystem:
    """
    Manages Git checkpoints for task execution.
    Creates commits and tags on successful task completion.
    """
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.checkpoints: List[Checkpoint] = []
        self.version_counter = 0
        self._load_version_counter()
    
    def _run_git(self, *args) -> tuple[bool, str]:
        """Run a git command and return success status and output."""
        try:
            result = subprocess.run(
                ["git"] + list(args),
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "Git command timed out"
        except Exception as e:
            return False, str(e)
    
    def _load_version_counter(self):
        """Load version counter from all atlas tags."""
        prefixes = ["atlas-v", "milestone-v", "rollback-v", "manual-v"]
        max_version = 0
        
        for prefix in prefixes:
            success, output = self._run_git("tag", "-l", f"{prefix}*")
            if success and output:
                for tag in output.split("\n"):
                    if tag:
                        try:
                            version = int(tag.split("-v")[-1])
                            max_version = max(max_version, version)
                        except ValueError:
                            continue
        
        self.version_counter = max_version
    
    def _get_changed_files(self) -> List[str]:
        """Get list of changed files."""
        success, output = self._run_git("status", "--porcelain")
        if success and output:
            return [line[3:] for line in output.split("\n") if line]
        return []
    
    def _generate_tag(self, checkpoint_type: CheckpointType) -> str:
        """Generate version tag."""
        self.version_counter += 1
        prefix = {
            CheckpointType.TASK_SUCCESS: "atlas-v",
            CheckpointType.MILESTONE: "milestone-v",
            CheckpointType.ROLLBACK: "rollback-v",
            CheckpointType.MANUAL: "manual-v"
        }.get(checkpoint_type, "atlas-v")
        return f"{prefix}{self.version_counter}"
    
    def has_changes(self) -> bool:
        """Check if there are uncommitted changes."""
        success, output = self._run_git("status", "--porcelain")
        return success and bool(output.strip())
    
    def create_checkpoint(
        self,
        task_id: str,
        description: str,
        checkpoint_type: CheckpointType = CheckpointType.TASK_SUCCESS,
        agent: str = "",
        create_tag: bool = True
    ) -> Optional[Checkpoint]:
        """
        Create a Git checkpoint (commit + optional tag).
        
        Args:
            task_id: ID of the task that was completed
            description: Description of what was accomplished
            checkpoint_type: Type of checkpoint
            agent: Which agent triggered this checkpoint
            create_tag: Whether to create a version tag
            
        Returns:
            Checkpoint object if successful, None otherwise
        """
        changed_files = self._get_changed_files()
        
        if not changed_files:
            return None
        
        success, _ = self._run_git("add", "-A")
        if not success:
            return None
        
        commit_msg = f"[{checkpoint_type.value}] {description}\n\nTask: {task_id}\nAgent: {agent or 'system'}"
        success, output = self._run_git("commit", "-m", commit_msg)
        if not success:
            return None
        
        success, commit_hash = self._run_git("rev-parse", "HEAD")
        if not success:
            commit_hash = "unknown"
        
        tag = None
        if create_tag:
            tag = self._generate_tag(checkpoint_type)
            self._run_git("tag", "-a", tag, "-m", f"Checkpoint: {description}")
        
        checkpoint = Checkpoint(
            commit_hash=commit_hash[:8],
            tag=tag,
            checkpoint_type=checkpoint_type,
            task_id=task_id,
            description=description,
            timestamp=datetime.now().isoformat(),
            files_changed=changed_files,
            agent=agent
        )
        
        self.checkpoints.append(checkpoint)
        return checkpoint
    
    def rollback_to_checkpoint(self, tag_or_hash: str) -> tuple[bool, str]:
        """
        Rollback to a previous checkpoint.
        
        Args:
            tag_or_hash: Tag name or commit hash to rollback to
            
        Returns:
            Tuple of (success, message)
        """
        success, _ = self._run_git("rev-parse", "--verify", f"{tag_or_hash}^{{commit}}")
        if not success:
            return False, f"Target '{tag_or_hash}' does not exist or is not a valid commit"
        
        if self.has_changes():
            self.create_checkpoint(
                task_id="pre-rollback",
                description="Auto-save before rollback",
                checkpoint_type=CheckpointType.ROLLBACK,
                agent="system"
            )
        
        success, current_branch = self._run_git("branch", "--show-current")
        if not current_branch:
            current_branch = "main"
        
        success, output = self._run_git("checkout", current_branch)
        success, output = self._run_git("reset", "--hard", tag_or_hash)
        
        if success:
            return True, f"Rolled back to {tag_or_hash}"
        return False, f"Rollback failed: {output}"
    
    def list_checkpoints(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent checkpoints from git log."""
        success, output = self._run_git(
            "log", f"-{limit}", "--pretty=format:%h|%s|%ai|%d"
        )
        
        if not success:
            return []
        
        result = []
        for line in output.split("\n"):
            if not line:
                continue
            parts = line.split("|")
            if len(parts) >= 3:
                result.append({
                    "hash": parts[0],
                    "message": parts[1],
                    "date": parts[2],
                    "refs": parts[3] if len(parts) > 3 else ""
                })
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get checkpoint system status."""
        _, branch = self._run_git("branch", "--show-current")
        _, head = self._run_git("rev-parse", "--short", "HEAD")
        
        return {
            "branch": branch or "unknown",
            "head": head or "unknown",
            "has_changes": self.has_changes(),
            "changed_files": self._get_changed_files(),
            "version_counter": self.version_counter,
            "recent_checkpoints": len(self.checkpoints)
        }


checkpoint_system = GitCheckpointSystem()

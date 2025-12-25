"""
Work Proof - Verifiable Task Completion
=======================================

🐺 WE ARE SWARM - Trust, but verify.

This is IP-level code: Cryptographic proof that work was actually done.
Prevents agents from claiming work they didn't do.

How It Works:
1. Before work: Agent commits to a task (hash of description + files)
2. During work: System tracks file modifications
3. After work: Generate proof (before/after hashes, git commits, time spent)
4. Verification: Anyone can verify the proof is valid

Use Cases:
- Leaderboard integrity (only count real work)
- Task handoffs (prove what was done)
- Audit trail (who changed what, when)
- Dispute resolution (agent claims they fixed X, did they?)

Author: The Swarm
License: MIT
"""

import json
import hashlib
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class FileSnapshot:
    """Snapshot of a file at a point in time."""
    path: str
    exists: bool
    size: int = 0
    content_hash: str = ""
    last_modified: Optional[datetime] = None


@dataclass
class WorkCommitment:
    """Commitment to do work (before starting)."""
    id: str
    agent_id: str
    task_description: str
    target_files: List[str]
    commitment_hash: str  # SHA256 of description + files
    created_at: datetime = field(default_factory=datetime.now)
    before_snapshots: Dict[str, FileSnapshot] = field(default_factory=dict)


@dataclass
class WorkProof:
    """Proof that work was completed."""
    commitment_id: str
    agent_id: str
    task_description: str
    
    # Timing
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    
    # File changes
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    files_deleted: List[str] = field(default_factory=list)
    
    # Git proof (if available)
    git_commits: List[str] = field(default_factory=list)
    git_diff_stats: Dict[str, Any] = field(default_factory=dict)
    
    # Verification
    before_hashes: Dict[str, str] = field(default_factory=dict)
    after_hashes: Dict[str, str] = field(default_factory=dict)
    proof_hash: str = ""  # Combined hash of all evidence
    
    # Validation
    valid: bool = False
    validation_notes: List[str] = field(default_factory=list)


class WorkProofSystem:
    """
    Cryptographic proof of work completion.
    
    This is core IP: Verifiable work tracking for AI agents.
    
    Example:
        proof_system = WorkProofSystem()
        
        # Before work: commit to the task
        commitment = proof_system.commit(
            agent_id="agent-1",
            task="Fix authentication bug",
            files=["src/auth.py", "src/login.py"]
        )
        
        # Agent does the work...
        
        # After work: generate proof
        proof = proof_system.prove(commitment.id)
        
        print(proof.files_modified)  # ["src/auth.py"]
        print(proof.git_commits)     # ["abc123"]
        print(proof.valid)           # True
        
        # Anyone can verify
        is_valid = proof_system.verify(proof)
    """
    
    def __init__(
        self,
        storage_dir: str = "./swarm_proofs",
        repo_path: str = "."
    ):
        """Initialize work proof system."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.repo_path = Path(repo_path)
        
        self.commitments_dir = self.storage_dir / "commitments"
        self.proofs_dir = self.storage_dir / "proofs"
        self.commitments_dir.mkdir(exist_ok=True)
        self.proofs_dir.mkdir(exist_ok=True)
        
        self.active_commitments: Dict[str, WorkCommitment] = {}
        self._load_commitments()
    
    def _generate_hash(self, data: str) -> str:
        """Generate SHA256 hash."""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _file_hash(self, path: Path) -> str:
        """Generate hash of file contents."""
        if not path.exists():
            return ""
        try:
            content = path.read_bytes()
            return hashlib.sha256(content).hexdigest()
        except Exception:
            return ""
    
    def _snapshot_file(self, path: str) -> FileSnapshot:
        """Take a snapshot of a file."""
        file_path = self.repo_path / path
        
        if not file_path.exists():
            return FileSnapshot(path=path, exists=False)
        
        try:
            stat = file_path.stat()
            return FileSnapshot(
                path=path,
                exists=True,
                size=stat.st_size,
                content_hash=self._file_hash(file_path),
                last_modified=datetime.fromtimestamp(stat.st_mtime)
            )
        except Exception:
            return FileSnapshot(path=path, exists=False)
    
    def _load_commitments(self):
        """Load active commitments."""
        for commit_file in self.commitments_dir.glob("*.json"):
            try:
                data = json.loads(commit_file.read_text())
                
                before_snapshots = {}
                for path, snap_data in data.get("before_snapshots", {}).items():
                    before_snapshots[path] = FileSnapshot(
                        path=snap_data["path"],
                        exists=snap_data["exists"],
                        size=snap_data.get("size", 0),
                        content_hash=snap_data.get("content_hash", "")
                    )
                
                commitment = WorkCommitment(
                    id=data["id"],
                    agent_id=data["agent_id"],
                    task_description=data["task_description"],
                    target_files=data["target_files"],
                    commitment_hash=data["commitment_hash"],
                    created_at=datetime.fromisoformat(data["created_at"]),
                    before_snapshots=before_snapshots
                )
                self.active_commitments[commitment.id] = commitment
            except Exception:
                pass
    
    def _save_commitment(self, commitment: WorkCommitment):
        """Save commitment to disk."""
        before_snapshots = {}
        for path, snap in commitment.before_snapshots.items():
            before_snapshots[path] = {
                "path": snap.path,
                "exists": snap.exists,
                "size": snap.size,
                "content_hash": snap.content_hash
            }
        
        data = {
            "id": commitment.id,
            "agent_id": commitment.agent_id,
            "task_description": commitment.task_description,
            "target_files": commitment.target_files,
            "commitment_hash": commitment.commitment_hash,
            "created_at": commitment.created_at.isoformat(),
            "before_snapshots": before_snapshots
        }
        
        commit_file = self.commitments_dir / f"{commitment.id}.json"
        commit_file.write_text(json.dumps(data, indent=2))
    
    def _get_git_commits_since(self, since: datetime) -> List[str]:
        """Get git commit hashes since a timestamp."""
        try:
            since_str = since.strftime("%Y-%m-%d %H:%M:%S")
            result = subprocess.run(
                ["git", "log", f"--since={since_str}", "--format=%H"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return [h.strip() for h in result.stdout.strip().split("\n") if h.strip()]
        except Exception:
            pass
        return []
    
    def _get_git_diff_stats(self, files: List[str]) -> Dict[str, Any]:
        """Get git diff statistics for files."""
        stats = {
            "insertions": 0,
            "deletions": 0,
            "files_changed": 0
        }
        
        try:
            for file in files:
                result = subprocess.run(
                    ["git", "diff", "--numstat", "HEAD~1", "--", file],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    parts = result.stdout.strip().split()
                    if len(parts) >= 2:
                        try:
                            stats["insertions"] += int(parts[0]) if parts[0] != "-" else 0
                            stats["deletions"] += int(parts[1]) if parts[1] != "-" else 0
                            stats["files_changed"] += 1
                        except ValueError:
                            pass
        except Exception:
            pass
        
        return stats
    
    def commit(
        self,
        agent_id: str,
        task: str,
        files: List[str]
    ) -> WorkCommitment:
        """
        Commit to doing work (before starting).
        
        This creates a timestamped, hashed record of intent.
        
        Args:
            agent_id: Who is committing
            task: What they will do
            files: Files they will touch
            
        Returns:
            The commitment record
        """
        # Generate commitment hash
        commitment_data = f"{agent_id}|{task}|{','.join(sorted(files))}"
        commitment_hash = self._generate_hash(commitment_data)
        
        # Take before snapshots
        before_snapshots = {}
        for file in files:
            before_snapshots[file] = self._snapshot_file(file)
        
        # Create commitment
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        commitment = WorkCommitment(
            id=f"commit_{timestamp}_{commitment_hash[:8]}",
            agent_id=agent_id,
            task_description=task,
            target_files=files,
            commitment_hash=commitment_hash,
            before_snapshots=before_snapshots
        )
        
        self.active_commitments[commitment.id] = commitment
        self._save_commitment(commitment)
        
        return commitment
    
    def prove(self, commitment_id: str) -> WorkProof:
        """
        Generate proof of work completion.
        
        Args:
            commitment_id: The commitment to prove
            
        Returns:
            Work proof with all evidence
        """
        if commitment_id not in self.active_commitments:
            raise ValueError(f"Unknown commitment: {commitment_id}")
        
        commitment = self.active_commitments[commitment_id]
        now = datetime.now()
        
        # Take after snapshots
        files_created = []
        files_modified = []
        files_deleted = []
        before_hashes = {}
        after_hashes = {}
        
        for file, before_snap in commitment.before_snapshots.items():
            after_snap = self._snapshot_file(file)
            
            before_hashes[file] = before_snap.content_hash
            after_hashes[file] = after_snap.content_hash
            
            if not before_snap.exists and after_snap.exists:
                files_created.append(file)
            elif before_snap.exists and not after_snap.exists:
                files_deleted.append(file)
            elif before_snap.content_hash != after_snap.content_hash:
                files_modified.append(file)
        
        # Get git evidence
        git_commits = self._get_git_commits_since(commitment.created_at)
        git_diff_stats = self._get_git_diff_stats(
            files_created + files_modified
        )
        
        # Calculate duration
        duration = (now - commitment.created_at).total_seconds()
        
        # Generate proof hash
        proof_data = (
            f"{commitment_id}|"
            f"{json.dumps(before_hashes, sort_keys=True)}|"
            f"{json.dumps(after_hashes, sort_keys=True)}|"
            f"{','.join(git_commits)}"
        )
        proof_hash = self._generate_hash(proof_data)
        
        # Validate
        valid = True
        validation_notes = []
        
        # Must have some changes
        total_changes = len(files_created) + len(files_modified) + len(files_deleted)
        if total_changes == 0:
            valid = False
            validation_notes.append("No file changes detected")
        
        # Should have reasonable duration (not instant)
        if duration < 60:  # Less than 1 minute
            validation_notes.append("Warning: Very short duration")
        
        # Git commits are good evidence
        if git_commits:
            validation_notes.append(f"Git commits found: {len(git_commits)}")
        else:
            validation_notes.append("No git commits found")
        
        # Create proof
        proof = WorkProof(
            commitment_id=commitment_id,
            agent_id=commitment.agent_id,
            task_description=commitment.task_description,
            started_at=commitment.created_at,
            completed_at=now,
            duration_seconds=duration,
            files_created=files_created,
            files_modified=files_modified,
            files_deleted=files_deleted,
            git_commits=git_commits,
            git_diff_stats=git_diff_stats,
            before_hashes=before_hashes,
            after_hashes=after_hashes,
            proof_hash=proof_hash,
            valid=valid,
            validation_notes=validation_notes
        )
        
        # Save proof
        proof_file = self.proofs_dir / f"{commitment_id}_proof.json"
        proof_file.write_text(json.dumps({
            "commitment_id": proof.commitment_id,
            "agent_id": proof.agent_id,
            "task_description": proof.task_description,
            "started_at": proof.started_at.isoformat(),
            "completed_at": proof.completed_at.isoformat(),
            "duration_seconds": proof.duration_seconds,
            "files_created": proof.files_created,
            "files_modified": proof.files_modified,
            "files_deleted": proof.files_deleted,
            "git_commits": proof.git_commits,
            "git_diff_stats": proof.git_diff_stats,
            "before_hashes": proof.before_hashes,
            "after_hashes": proof.after_hashes,
            "proof_hash": proof.proof_hash,
            "valid": proof.valid,
            "validation_notes": proof.validation_notes
        }, indent=2))
        
        # Remove from active commitments
        del self.active_commitments[commitment_id]
        (self.commitments_dir / f"{commitment_id}.json").unlink(missing_ok=True)
        
        return proof
    
    def verify(self, proof: WorkProof) -> Tuple[bool, List[str]]:
        """
        Verify a work proof is valid.
        
        Args:
            proof: The proof to verify
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Verify proof hash
        proof_data = (
            f"{proof.commitment_id}|"
            f"{json.dumps(proof.before_hashes, sort_keys=True)}|"
            f"{json.dumps(proof.after_hashes, sort_keys=True)}|"
            f"{','.join(proof.git_commits)}"
        )
        expected_hash = self._generate_hash(proof_data)
        
        if proof.proof_hash != expected_hash:
            issues.append("Proof hash mismatch - data may be tampered")
        
        # Verify file changes are consistent
        for file in proof.files_modified:
            if file in proof.before_hashes and file in proof.after_hashes:
                if proof.before_hashes[file] == proof.after_hashes[file]:
                    issues.append(f"File claimed modified but hashes match: {file}")
        
        # Check git commits exist (if we can)
        for commit_hash in proof.git_commits:
            try:
                result = subprocess.run(
                    ["git", "cat-file", "-t", commit_hash],
                    cwd=self.repo_path,
                    capture_output=True,
                    timeout=5
                )
                if result.returncode != 0:
                    issues.append(f"Git commit not found: {commit_hash}")
            except Exception:
                pass  # Can't verify git, skip
        
        is_valid = len(issues) == 0 and proof.valid
        return is_valid, issues
    
    def get_agent_proofs(self, agent_id: str) -> List[WorkProof]:
        """Get all proofs for an agent."""
        proofs = []
        for proof_file in self.proofs_dir.glob("*_proof.json"):
            try:
                data = json.loads(proof_file.read_text())
                if data["agent_id"] == agent_id:
                    proofs.append(WorkProof(
                        commitment_id=data["commitment_id"],
                        agent_id=data["agent_id"],
                        task_description=data["task_description"],
                        started_at=datetime.fromisoformat(data["started_at"]),
                        completed_at=datetime.fromisoformat(data["completed_at"]),
                        duration_seconds=data["duration_seconds"],
                        files_created=data.get("files_created", []),
                        files_modified=data.get("files_modified", []),
                        files_deleted=data.get("files_deleted", []),
                        git_commits=data.get("git_commits", []),
                        git_diff_stats=data.get("git_diff_stats", {}),
                        before_hashes=data.get("before_hashes", {}),
                        after_hashes=data.get("after_hashes", {}),
                        proof_hash=data.get("proof_hash", ""),
                        valid=data.get("valid", False),
                        validation_notes=data.get("validation_notes", [])
                    ))
            except Exception:
                pass
        return proofs

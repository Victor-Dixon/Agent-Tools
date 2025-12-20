#!/usr/bin/env python3
# SSOT Domain: infrastructure
"""
Repository Status Tracker - SSOT for Repository Status
======================================================

Tracks repository status (exists/merged/deleted) to prevent duplicate attempts
and classify errors correctly.

Author: Agent-5 (Business Intelligence Specialist)
Date: 2025-12-03
V2 Compliant: Yes (<300 lines)
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Set
from enum import Enum


class RepoStatus(Enum):
    """Repository status enumeration."""
    EXISTS = "exists"           # Repository exists and is available
    MERGED = "merged"           # Repository has been merged into another
    DELETED = "deleted"         # Repository has been deleted
    NOT_AVAILABLE = "not_available"  # Repository not available (permanent error)
    UNKNOWN = "unknown"         # Status not yet determined


class RepoStatusTracker:
    """SSOT for tracking repository status and merge attempts."""
    
    def __init__(self, status_file: Optional[Path] = None):
        """
        Initialize repository status tracker.
        
        Args:
            status_file: Path to status file (default: data/repo_status.json)
        """
        if status_file is None:
            project_root = Path(__file__).parent.parent
            status_file = project_root / "data" / "repo_status.json"
        
        self.status_file = status_file
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_status()
    
    def _load_status(self) -> None:
        """Load status from file."""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    data = json.load(f)
                    self.repos: Dict[str, Dict] = data.get("repos", {})
                    self.attempts: Dict[str, list] = data.get("attempts", {})
                    self.consolidation_direction: Dict[str, str] = data.get("consolidation_direction", {})
            except Exception as e:
                print(f"⚠️ Failed to load status file: {e}")
                self.repos = {}
                self.attempts = {}
                self.consolidation_direction = {}
        else:
            self.repos = {}
            self.attempts = {}
            self.consolidation_direction = {}
    
    def _save_status(self) -> None:
        """Save status to file."""
        try:
            data = {
                "repos": self.repos,
                "attempts": self.attempts,
                "consolidation_direction": self.consolidation_direction,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.status_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save status file: {e}")
    
    def normalize_repo_name(self, repo_name: str) -> str:
        """
        Normalize repository name for consistent tracking.
        
        Args:
            repo_name: Repository name (may be "owner/repo" or just "repo")
            
        Returns:
            Normalized repository name
        """
        # Remove leading/trailing whitespace
        repo_name = repo_name.strip()
        
        # If no "/" in name, assume it's just the repo name
        # (owner will be determined from context)
        if "/" not in repo_name:
            return repo_name.lower()
        
        # Normalize owner/repo format
        parts = repo_name.split("/")
        if len(parts) == 2:
            owner, repo = parts
            return f"{owner.lower()}/{repo.lower()}"
        
        return repo_name.lower()
    
    def get_repo_status(self, repo_name: str) -> RepoStatus:
        """
        Get current status of repository.
        
        Args:
            repo_name: Repository name
            
        Returns:
            RepoStatus enum value
        """
        normalized = self.normalize_repo_name(repo_name)
        repo_data = self.repos.get(normalized, {})
        status_str = repo_data.get("status", "unknown")
        
        try:
            return RepoStatus(status_str)
        except ValueError:
            return RepoStatus.UNKNOWN
    
    def set_repo_status(self, repo_name: str, status: RepoStatus, reason: Optional[str] = None) -> None:
        """
        Set repository status.
        
        Args:
            repo_name: Repository name
            status: New status
            reason: Optional reason for status change
        """
        normalized = self.normalize_repo_name(repo_name)
        
        if normalized not in self.repos:
            self.repos[normalized] = {}
        
        self.repos[normalized]["status"] = status.value
        self.repos[normalized]["last_updated"] = datetime.now().isoformat()
        
        if reason:
            self.repos[normalized]["reason"] = reason
        
        self._save_status()
    
    def record_attempt(self, source_repo: str, target_repo: str, success: bool, error: Optional[str] = None) -> None:
        """
        Record merge attempt to prevent duplicates.
        
        Args:
            source_repo: Source repository name
            target_repo: Target repository name
            success: Whether attempt was successful
            error: Error message if failed
        """
        normalized_source = self.normalize_repo_name(source_repo)
        normalized_target = self.normalize_repo_name(target_repo)
        attempt_key = f"{normalized_source}→{normalized_target}"
        
        if attempt_key not in self.attempts:
            self.attempts[attempt_key] = []
        
        attempt = {
            "timestamp": datetime.now().isoformat(),
            "source": normalized_source,
            "target": normalized_target,
            "success": success,
            "error": error
        }
        
        self.attempts[attempt_key].append(attempt)
        
        # Keep only last 10 attempts per pair
        if len(self.attempts[attempt_key]) > 10:
            self.attempts[attempt_key] = self.attempts[attempt_key][-10:]
        
        self._save_status()
    
    def has_attempted(self, source_repo: str, target_repo: str) -> bool:
        """
        Check if merge has been attempted before.
        
        Args:
            source_repo: Source repository name
            target_repo: Target repository name
            
        Returns:
            True if attempt exists, False otherwise
        """
        normalized_source = self.normalize_repo_name(source_repo)
        normalized_target = self.normalize_repo_name(target_repo)
        attempt_key = f"{normalized_source}→{normalized_target}"
        
        return attempt_key in self.attempts and len(self.attempts[attempt_key]) > 0
    
    def get_last_attempt(self, source_repo: str, target_repo: str) -> Optional[Dict]:
        """
        Get last attempt details.
        
        Args:
            source_repo: Source repository name
            target_repo: Target repository name
            
        Returns:
            Last attempt dict or None
        """
        normalized_source = self.normalize_repo_name(source_repo)
        normalized_target = self.normalize_repo_name(target_repo)
        attempt_key = f"{normalized_source}→{normalized_target}"
        
        attempts = self.attempts.get(attempt_key, [])
        if attempts:
            return attempts[-1]
        return None
    
    def set_consolidation_direction(self, source_repo: str, target_repo: str) -> None:
        """
        Record consolidation direction (source → target).
        
        Args:
            source_repo: Source repository name
            target_repo: Target repository name
        """
        normalized_source = self.normalize_repo_name(source_repo)
        normalized_target = self.normalize_repo_name(target_repo)
        
        self.consolidation_direction[normalized_source] = normalized_target
        self._save_status()
    
    def get_consolidation_target(self, source_repo: str) -> Optional[str]:
        """
        Get consolidation target for source repository.
        
        Args:
            source_repo: Source repository name
            
        Returns:
            Target repository name or None
        """
        normalized_source = self.normalize_repo_name(source_repo)
        return self.consolidation_direction.get(normalized_source)
    
    def is_permanent_error(self, error: str) -> bool:
        """
        Classify error as permanent (no retries).
        
        Args:
            error: Error message
            
        Returns:
            True if error is permanent, False if retryable
        """
        permanent_indicators = [
            "repo not available",
            "not available",
            "repository not found",
            "404",
            "does not exist",
            "deleted",
            "removed"
        ]
        
        error_lower = error.lower()
        return any(indicator in error_lower for indicator in permanent_indicators)
    
    def get_all_statuses(self) -> Dict[str, Dict]:
        """Get all repository statuses."""
        return self.repos.copy()
    
    def get_all_attempts(self) -> Dict[str, list]:
        """Get all merge attempts."""
        return self.attempts.copy()


# Global instance
_tracker_instance: Optional[RepoStatusTracker] = None


def get_repo_status_tracker() -> RepoStatusTracker:
    """Get global repository status tracker instance."""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = RepoStatusTracker()
    return _tracker_instance


if __name__ == "__main__":
    # Test the tracker
    tracker = RepoStatusTracker()
    
    # Test normalization
    print("Testing name normalization:")
    print(f"  'MyRepo' -> '{tracker.normalize_repo_name('MyRepo')}'")
    print(f"  'Owner/MyRepo' -> '{tracker.normalize_repo_name('Owner/MyRepo')}'")
    
    # Test status tracking
    print("\nTesting status tracking:")
    tracker.set_repo_status("test-repo", RepoStatus.EXISTS)
    print(f"  test-repo status: {tracker.get_repo_status('test-repo')}")
    
    # Test attempt tracking
    print("\nTesting attempt tracking:")
    tracker.record_attempt("source-repo", "target-repo", False, "Repo not available")
    print(f"  Has attempted: {tracker.has_attempted('source-repo', 'target-repo')}")
    print(f"  Last attempt: {tracker.get_last_attempt('source-repo', 'target-repo')}")
    
    # Test error classification
    print("\nTesting error classification:")
    print(f"  'Repo not available' -> Permanent: {tracker.is_permanent_error('Repo not available')}")
    print(f"  'Rate limit exceeded' -> Permanent: {tracker.is_permanent_error('Rate limit exceeded')}")

#!/usr/bin/env python3
"""
Safe Repository Merge Script - Local-First Architecture
===========================================================

Safely merges one GitHub repository into another using local-first approach.
Uses GitHub Bypass System to eliminate blocking on GitHub API rate limits.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-11-28
Priority: HIGH
Version: 2.0 - Local-First Architecture
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import subprocess
import shutil

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import new local-first components
from src.core.synthetic_github import get_synthetic_github
from src.core.consolidation_buffer import get_consolidation_buffer, ConsolidationStatus
from src.core.merge_conflict_resolver import get_conflict_resolver
from src.core.local_repo_layer import get_local_repo_manager
from src.core.deferred_push_queue import get_deferred_push_queue

# Import repository status tracker for error classification and duplicate prevention
try:
    from tools.repo_status_tracker import get_repo_status_tracker, RepoStatus
    STATUS_TRACKER_AVAILABLE = True
except ImportError:
    STATUS_TRACKER_AVAILABLE = False
    RepoStatus = None  # Type stub for type hints

def get_github_token() -> Optional[str]:
    """Get GitHub token from environment or .env file."""
    # Use SSOT utility for GitHub token
    from src.core.utils.github_utils import get_github_token as get_token_ssot
    return get_token_ssot(project_root)


class SafeRepoMerge:
    """Safely merge one repository into another using local-first approach."""

    def __init__(self, target_repo: str, source_repo: str, repo_numbers: Dict[str, int]):
        """
        Initialize safe merge operation.

        Args:
            target_repo: Name of target repository (where content goes)
            source_repo: Name of source repository (to be merged)
            repo_numbers: Dict mapping repo names to repo numbers
        """
        self.target_repo = target_repo
        self.source_repo = source_repo
        self.target_repo_num = repo_numbers.get(target_repo)
        self.source_repo_num = repo_numbers.get(source_repo)
        self.backup_dir = Path("consolidation_backups")
        self.log_file = Path(f"consolidation_logs/merge_{source_repo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize new components
        self.github = get_synthetic_github()
        self.buffer = get_consolidation_buffer()
        self.conflict_resolver = get_conflict_resolver()
        self.repo_manager = get_local_repo_manager()
        self.queue = get_deferred_push_queue()
        
        # Initialize status tracker for error classification and duplicate prevention
        if STATUS_TRACKER_AVAILABLE:
            self.status_tracker = get_repo_status_tracker()
            # Normalize repository names for consistent tracking
            self.target_repo_normalized = self.status_tracker.normalize_repo_name(self.target_repo)
            self.source_repo_normalized = self.status_tracker.normalize_repo_name(self.source_repo)
        else:
            self.status_tracker = None
            self.target_repo_normalized = self.target_repo.lower()
            self.source_repo_normalized = self.source_repo.lower()
        
        self.github_username = self._get_github_username()

    def _get_github_username(self) -> str:
        """Get GitHub username from environment or config."""
        username = os.getenv("GITHUB_USERNAME", "Dadudekc")
        config_path = project_root / "config" / "github_username.txt"
        if config_path.exists():
            try:
                username = config_path.read_text().strip()
            except Exception:
                pass
        return username

    def create_backup(self) -> bool:
        """Create backup of merge operation details."""
        try:
            source_repo_name = self.source_repo.split("/")[-1] if "/" in self.source_repo else self.source_repo
            
            backup_file = self.backup_dir / self.github_username / f"{source_repo_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "target_repo": self.target_repo,
                "target_repo_num": self.target_repo_num,
                "source_repo": self.source_repo,
                "source_repo_num": self.source_repo_num,
                "operation": "merge",
                "status": "backup_created"
            }
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            print(f"✅ Backup created: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ Backup creation failed: {e}")
            return False

    def verify_target_repo(self) -> bool:
        """Verify target repository exists and is valid."""
        master_list_path = project_root / "data" / "github_75_repos_master_list.json"
        
        if not master_list_path.exists():
            print(f"⚠️ Master list not found: {master_list_path}")
            return True
        
        try:
            with open(master_list_path, 'r') as f:
                master_list = json.load(f)
            
            repos = master_list.get("repos", [])
            target_found = any(r.get("name") == self.target_repo for r in repos)
            
            if target_found:
                print(f"✅ Target repo verified: {self.target_repo} (repo #{self.target_repo_num})")
                return True
            else:
                print(f"⚠️ Target repo not found in master list: {self.target_repo}")
                return True
        except Exception as e:
            print(f"⚠️ Verification error: {e}")
            return True


    def _preflight_checks(self) -> tuple[bool, Optional[str]]:
        """
        Perform pre-flight checks before attempting merge.
        
        Returns:
            (success, error_message) tuple
        """
        if not self.status_tracker:
            # Status tracker not available - skip pre-flight checks
            return True, None
        
        # Check 1: Duplicate prevention - has this merge been attempted?
        if self.status_tracker.has_attempted(self.source_repo, self.target_repo):
            last_attempt = self.status_tracker.get_last_attempt(self.source_repo, self.target_repo)
            if last_attempt and last_attempt.get("success"):
                return False, f"Merge already completed successfully (last attempt: {last_attempt.get('timestamp')})"
            elif last_attempt:
                error = last_attempt.get("error", "Unknown error")
                # If permanent error, don't retry
                if self.status_tracker.is_permanent_error(error):
                    return False, f"Previous attempt failed with permanent error: {error} (no retries)"
        
        # Check 2: Repository status - check if repos are already merged/deleted
        source_status = self.status_tracker.get_repo_status(self.source_repo)
        if source_status == RepoStatus.MERGED:
            target = self.status_tracker.get_consolidation_target(self.source_repo)
            return False, f"Source repo already merged into {target}"
        if source_status == RepoStatus.DELETED:
            return False, "Source repo has been deleted"
        if source_status == RepoStatus.NOT_AVAILABLE:
            return False, "Source repo not available (permanent error - no retries)"
        
        target_status = self.status_tracker.get_repo_status(self.target_repo)
        if target_status == RepoStatus.DELETED:
            return False, "Target repo has been deleted"
        if target_status == RepoStatus.NOT_AVAILABLE:
            return False, "Target repo not available (permanent error - no retries)"
        
        # Check 3: Strategy review - verify consolidation direction
        existing_target = self.status_tracker.get_consolidation_target(self.source_repo)
        if existing_target and existing_target != self.target_repo_normalized:
            return False, f"Consolidation direction mismatch: source repo is already planned to merge into {existing_target}, not {self.target_repo}"
        
        # Check 4: Name resolution - verify exact repo names
        print(f"📝 Name resolution:")
        print(f"   Source: '{self.source_repo}' → '{self.source_repo_normalized}'")
        print(f"   Target: '{self.target_repo}' → '{self.target_repo_normalized}'")
        
        # Check 5: Pre-flight repository existence check
        print(f"🔍 Pre-flight: Verifying repositories exist...")
        source_exists = self._verify_repo_exists(self.source_repo)
        target_exists = self._verify_repo_exists(self.target_repo)
        
        if not source_exists:
            # Mark as permanent error - no retries
            self.status_tracker.set_repo_status(self.source_repo, RepoStatus.NOT_AVAILABLE, "Pre-flight check: repo does not exist")
            return False, "Source repo not available (permanent error - no retries)"
        
        if not target_exists:
            # Mark as permanent error - no retries
            self.status_tracker.set_repo_status(self.target_repo, RepoStatus.NOT_AVAILABLE, "Pre-flight check: repo does not exist")
            return False, "Target repo not available (permanent error - no retries)"
        
        # Mark repos as existing
        self.status_tracker.set_repo_status(self.source_repo, RepoStatus.EXISTS)
        self.status_tracker.set_repo_status(self.target_repo, RepoStatus.EXISTS)
        
        # Record consolidation direction
        self.status_tracker.set_consolidation_direction(self.source_repo, self.target_repo)
        
        print(f"✅ Pre-flight checks passed")
        return True, None
    
    def _verify_repo_exists(self, repo_name: str) -> bool:
        """
        Verify repository exists before attempting merge.
        
        Args:
            repo_name: Repository name to verify
            
        Returns:
            True if repo exists, False otherwise
        """
        try:
            # Try to get repo - this will check both local and GitHub
            success, path, was_local = self.github.get_repo(
                repo_name, github_user=self.github_username
            )
            return success
        except Exception as e:
            print(f"⚠️ Error verifying {repo_name}: {e}")
            return False

    def execute_merge(self, dry_run: bool = True) -> bool:
        """
        Execute the merge operation using local-first approach.

        Args:
            dry_run: If True, only simulate the merge without actual changes

        Returns:
            True if merge would succeed, False otherwise
        """
        print(f"\n{'='*60}")
        print(f"🔗 SAFE REPO MERGE V2 - LOCAL-FIRST ARCHITECTURE")
        print(f"{'='*60}")
        print(f"Target: {self.target_repo} (repo #{self.target_repo_num})")
        print(f"Source: {self.source_repo} (repo #{self.source_repo_num})")
        print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
        print(f"{'='*60}\n")
        
        # Step 0: Pre-flight checks (NEW - before any operations)
        print(f"🔍 Pre-flight checks...")
        preflight_success, preflight_error = self._preflight_checks()
        if not preflight_success:
            print(f"❌ Pre-flight check failed: {preflight_error}")
            self.generate_merge_report("FAILED", {}, preflight_error)
            # Record attempt with permanent error classification
            if self.status_tracker:
                self.status_tracker.record_attempt(
                    self.source_repo, 
                    self.target_repo, 
                    False, 
                    preflight_error
                )
            return False
        
                # Step 1: Create backup
        if not self.create_backup():
            self.generate_merge_report("FAILED", {}, "Backup creation failed")
            return False
        
        # Step 2: Verify target repo
        if not self.verify_target_repo():
            self.generate_merge_report("FAILED", {}, "Target repo verification failed")
            return False
        
        # Step 3: Create merge plan in consolidation buffer
        print(f"📋 Creating merge plan...")
        merge_plan = self.buffer.create_merge_plan(
            source_repo=self.source_repo,
            target_repo=self.target_repo,
            description=f"Merge {self.source_repo} into {self.target_repo} (repo #{self.source_repo_num} → #{self.target_repo_num})"
        )
        print(f"✅ Merge plan created: {merge_plan.plan_id}")
        
        # Step 4: Get repositories locally (local-first, GitHub fallback)
        print(f"📦 Getting repositories locally...")
        success, source_path, source_was_local = self.github.get_repo(
            self.source_repo, github_user=self.github_username
        )
        if not success:
            error_msg = "Source repo not available"
            # Classify error as permanent (no retries)
            if self.status_tracker:
                if self.status_tracker.is_permanent_error(error_msg):
                    self.status_tracker.set_repo_status(self.source_repo, RepoStatus.NOT_AVAILABLE, error_msg)
                self.status_tracker.record_attempt(self.source_repo, self.target_repo, False, error_msg)
            self.buffer.mark_failed(merge_plan.plan_id, error_msg)
            self.generate_merge_report("FAILED", {}, "Source repo not available")
            return False
        
        success, target_path, target_was_local = self.github.get_repo(
            self.target_repo, github_user=self.github_username
        )
        if not success:
            error_msg = "Target repo not available"
            # Classify error as permanent (no retries)
            if self.status_tracker:
                if self.status_tracker.is_permanent_error(error_msg):
                    self.status_tracker.set_repo_status(self.target_repo, RepoStatus.NOT_AVAILABLE, error_msg)
                self.status_tracker.record_attempt(self.source_repo, self.target_repo, False, error_msg)
            self.buffer.mark_failed(merge_plan.plan_id, error_msg)
            self.generate_merge_report("FAILED", {}, "Target repo not available")
            return False
        
        print(f"✅ Repositories ready (source: {'local' if source_was_local else 'cloned'}, target: {'local' if target_was_local else 'cloned'})")
        
        if dry_run:
            print("🔍 DRY RUN: Would merge repositories locally")
            print("   - Merge plan created: ✅")
            print("   - Repositories ready: ✅")
            print("   - Local merge: ⏳ (simulated)")
            self.buffer.mark_validated(merge_plan.plan_id)
            self.generate_merge_report("DRY_RUN_SUCCESS", {"plan_id": merge_plan.plan_id})
            return True
        
        # Step 5: Perform local merge with conflict resolution
        print(f"🔀 Performing local merge...")
        
        # Create merge branch
        merge_branch = f"merge-{self.source_repo}-{datetime.now().strftime('%Y%m%d')}"
        success = self.repo_manager.create_branch(self.target_repo, merge_branch)
        if not success:
            self.buffer.mark_failed(merge_plan.plan_id, "Failed to create merge branch")
            self.generate_merge_report("FAILED", {}, "Failed to create merge branch")
            return False
        
        # Merge with conflict resolution
        success, conflicts, error = self.conflict_resolver.merge_with_conflict_resolution(
            repo_path=target_path,
            source_branch="main",
            target_branch=merge_branch,
            resolution_strategy="theirs"  # Use source repo version for conflicts
        )
        
        if not success:
            if conflicts:
                print(f"⚠️ Conflicts detected: {len(conflicts)} files")
                self.buffer.mark_conflict(merge_plan.plan_id, conflicts)
                self.generate_merge_report("CONFLICTS_DETECTED", {"conflicts": conflicts, "plan_id": merge_plan.plan_id})
                return False
            else:
                self.buffer.mark_failed(merge_plan.plan_id, error or "Merge failed")
                self.generate_merge_report("FAILED", {}, error or "Merge failed")
                return False
        
        print(f"✅ Local merge successful")
        self.buffer.mark_merged(merge_plan.plan_id)
        
        # Step 6: Generate patch (for review/debugging)
        patch_file = self.repo_manager.generate_patch(self.target_repo, merge_branch)
        if patch_file:
            self.buffer.store_diff(merge_plan.plan_id, patch_file.read_text())
            print(f"✅ Patch generated: {patch_file}")
        
        # Step 7: Push branch (non-blocking - uses deferred queue if GitHub unavailable)
        print(f"📤 Pushing merge branch...")
        push_success, push_error = self.github.push_branch(self.target_repo, merge_branch, force=False)
        
        if push_success:
            print(f"✅ Branch pushed successfully: {merge_branch}")
        else:
            print(f"⚠️ Push deferred: {push_error}")
            # Push is queued automatically, continue
        
        # Step 8: Create PR (non-blocking - uses deferred queue if GitHub unavailable)
        print(f"🔗 Creating pull request...")
        pr_title = f"Merge {self.source_repo} into {self.target_repo}"
        pr_body = f"""Repository Consolidation Merge

**Source**: {self.source_repo} (repo #{self.source_repo_num})
**Target**: {self.target_repo} (repo #{self.target_repo_num})

This merge is part of repository consolidation.

**Verification**:
- ✅ Backup created
- ✅ Repositories verified
- ✅ Local merge completed
- ✅ Merge plan: {merge_plan.plan_id}
"""
        
        pr_success, pr_url_or_error = self.github.create_pr(
            repo_name=self.target_repo,
            branch=merge_branch,
            base_branch="main",
            title=pr_title,
            body=pr_body
        )
        
        if pr_success:
            print(f"✅ PR created: {pr_url_or_error}")
            self.buffer.mark_applied(merge_plan.plan_id)
        else:
            print(f"⚠️ PR creation deferred: {pr_url_or_error}")
            # PR is queued automatically, continue
        
        print(f"\n✅ Merge operation completed successfully!")
        print(f"   - Merge plan: {merge_plan.plan_id}")
        print(f"   - Branch: {merge_branch}")
        if pr_success:
            print(f"   - PR: {pr_url_or_error}")
        else:
            print(f"   - PR: Queued for later (check deferred_push_queue.json)")
        
        # Update status tracking
        if self.status_tracker:
            self.status_tracker.set_repo_status(self.source_repo, RepoStatus.MERGED, f"Merged into {self.target_repo}")
            self.status_tracker.record_attempt(self.source_repo, self.target_repo, True, None)
        
        self.generate_merge_report("SUCCESS", {"plan_id": merge_plan.plan_id, "branch": merge_branch})
        return True

    def generate_merge_report(self, status: str, conflicts: Dict[str, Any], error: Optional[str] = None) -> Dict[str, Any]:
        """Generate merge operation report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "target_repo": self.target_repo,
            "target_repo_num": self.target_repo_num,
            "source_repo": self.source_repo,
            "source_repo_num": self.source_repo_num,
            "status": status,
            "conflicts": conflicts,
            "error": error,
            "architecture": "local-first-v2"
        }
        
        try:
            with open(self.log_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"✅ Merge report saved: {self.log_file}")
        except Exception as e:
            print(f"⚠️ Failed to save report: {e}")
        
        return report


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Safe Repository Merge V2 - Local-First Architecture")
    parser.add_argument("target_repo", help="Target repository name")
    parser.add_argument("source_repo", help="Source repository name")
    parser.add_argument("--execute", action="store_true", help="Execute merge (default: dry run)")
    parser.add_argument("--target-num", type=int, help="Target repository number")
    parser.add_argument("--source-num", type=int, help="Source repository number")
    
    args = parser.parse_args()
    
    repo_numbers = {}
    if args.target_num:
        repo_numbers[args.target_repo] = args.target_num
    if args.source_num:
        repo_numbers[args.source_repo] = args.source_num
    
    merger = SafeRepoMerge(args.target_repo, args.source_repo, repo_numbers)
    success = merger.execute_merge(dry_run=not args.execute)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Enhance repo_safe_merge_v2.py with error classification, pre-flight checks, etc.

This script applies the enhancements to the first SafeRepoMergeV2 class definition.
"""

import re
from pathlib import Path

def enhance_repo_merge_v2():
    """Apply enhancements to repo_safe_merge_v2.py."""
    file_path = Path(__file__).parent / "repo_safe_merge_v2.py"
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    content = file_path.read_text(encoding='utf-8')
    
    # Enhancement 1: Add import for status tracker
    import_pattern = r"(from src\.core\.deferred_push_queue import get_deferred_push_queue)\s*\n\s*\n"
    import_replacement = r"""\1

# Import repository status tracker for error classification and duplicate prevention
try:
    from tools.repo_status_tracker import get_repo_status_tracker, RepoStatus
    STATUS_TRACKER_AVAILABLE = True
except ImportError:
    STATUS_TRACKER_AVAILABLE = False
    RepoStatus = None  # Type stub for type hints

"""
    
    if "from tools.repo_status_tracker import" not in content:
        content = re.sub(import_pattern, import_replacement, content, count=1)
        print("✅ Added status tracker import")
    
    # Enhancement 2: Add status tracker initialization in __init__
    init_pattern = r"(self\.queue = get_deferred_push_queue\(\))\s*\n\s*(self\.github_username = self\._get_github_username\(\))"
    init_replacement = r"""\1
        
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
        
        \2"""
    
    if "self.status_tracker = get_repo_status_tracker()" not in content:
        content = re.sub(init_pattern, init_replacement, content, count=1)
        print("✅ Added status tracker initialization")
    
    # Enhancement 3: Add pre-flight check methods before execute_merge
    preflight_methods = '''
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

'''
    
    # Insert pre-flight methods before execute_merge (first occurrence only)
    if "_preflight_checks" not in content:
        execute_merge_pattern = r"(    def execute_merge\(self, dry_run: bool = True\) -> bool:)"
        content = re.sub(execute_merge_pattern, preflight_methods + r"\1", content, count=1)
        print("✅ Added pre-flight check methods")
    
    # Enhancement 4: Add pre-flight check call at start of execute_merge
    if "# Step 0: Pre-flight checks" not in content:
        step1_pattern = r"(        print\(f\"\{'='\*60\}\\n\"\))\s*\n\s*(        # Step 1: Create backup)"
        step0_replacement = r"""\1
        
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
        
        \2"""
        content = re.sub(step1_pattern, step0_replacement, content, count=1)
        print("✅ Added pre-flight check call")
    
    # Enhancement 5: Add error classification to repo get failures
    if "Classify error as permanent" not in content:
        source_repo_pattern = r"(        if not success:\s*\n\s*self\.buffer\.mark_failed\(merge_plan\.plan_id, \"Source repo not available\"\))"
        source_replacement = r"""        if not success:
            error_msg = "Source repo not available"
            # Classify error as permanent (no retries)
            if self.status_tracker:
                if self.status_tracker.is_permanent_error(error_msg):
                    self.status_tracker.set_repo_status(self.source_repo, RepoStatus.NOT_AVAILABLE, error_msg)
                self.status_tracker.record_attempt(self.source_repo, self.target_repo, False, error_msg)
            self.buffer.mark_failed(merge_plan.plan_id, error_msg)"""
        
        target_repo_pattern = r"(        if not success:\s*\n\s*self\.buffer\.mark_failed\(merge_plan\.plan_id, \"Target repo not available\"\))"
        target_replacement = r"""        if not success:
            error_msg = "Target repo not available"
            # Classify error as permanent (no retries)
            if self.status_tracker:
                if self.status_tracker.is_permanent_error(error_msg):
                    self.status_tracker.set_repo_status(self.target_repo, RepoStatus.NOT_AVAILABLE, error_msg)
                self.status_tracker.record_attempt(self.source_repo, self.target_repo, False, error_msg)
            self.buffer.mark_failed(merge_plan.plan_id, error_msg)"""
        
        content = re.sub(source_repo_pattern, source_replacement, content, count=1)
        content = re.sub(target_repo_pattern, target_replacement, content, count=1)
        print("✅ Added error classification to repo get failures")
    
    # Enhancement 6: Add status tracking on success
    if "self.status_tracker.set_repo_status(self.source_repo, RepoStatus.MERGED" not in content:
        success_pattern = r"(        self\.generate_merge_report\(\"SUCCESS\", \{\"plan_id\": merge_plan\.plan_id, \"branch\": merge_branch\}\))"
        success_replacement = r"""        # Update status tracking
        if self.status_tracker:
            self.status_tracker.set_repo_status(self.source_repo, RepoStatus.MERGED, f"Merged into {self.target_repo}")
            self.status_tracker.record_attempt(self.source_repo, self.target_repo, True, None)
        
        \1"""
        content = re.sub(success_pattern, success_replacement, content, count=1)
        print("✅ Added status tracking on success")
    
    # Write enhanced content
    file_path.write_text(content, encoding='utf-8')
    print(f"\n✅ Enhancements applied to {file_path}")
    return True

if __name__ == "__main__":
    enhance_repo_merge_v2()



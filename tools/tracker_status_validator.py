#!/usr/bin/env python3
"""
Tracker Status Validator - Agent-6 Productivity Tool

⚠️ DEPRECATED: This tool has been consolidated into unified_validator.py
Use: python tools/unified_validator.py --category tracker

Validates SSOT consistency across tracking documents to prevent status drift.
Checks PHASE1_EXECUTION_TRACKING.md and MASTER_CONSOLIDATION_TRACKER.md for:
- Consistent progress counts
- Matching completion statuses
- No 'pending' or 'in progress' references for completed items
- PR links present for completed merges

<!-- SSOT Domain: infrastructure -->

V2 Compliant: <400 lines
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class TrackerValidator:
    """Validates tracker document consistency."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.tracking_file = repo_root / "docs/organization/PHASE1_EXECUTION_TRACKING.md"
        self.master_file = repo_root / "docs/organization/MASTER_CONSOLIDATION_TRACKER.md"
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validation checks."""
        if not self.tracking_file.exists():
            self.errors.append(f"Missing: {self.tracking_file}")
            return False, self.errors, self.warnings
            
        if not self.master_file.exists():
            self.errors.append(f"Missing: {self.master_file}")
            return False, self.errors, self.warnings
            
        self._check_progress_counts()
        self._check_completion_statuses()
        self._check_pending_references()
        self._check_pr_links()
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _check_progress_counts(self):
        """Verify progress counts match between files."""
        tracking_content = self.tracking_file.read_text()
        master_content = self.master_file.read_text()
        
        # Extract Batch 2 progress (e.g., "8/12 merges COMPLETE (67% progress)")
        tracking_match = re.search(r'(\d+)/12 merges COMPLETE \((\d+)% progress\)', tracking_content)
        master_match = re.search(r'(\d+)/12 merges COMPLETE \((\d+)% progress\)', master_content)
        
        if tracking_match and master_match:
            tracking_count = int(tracking_match.group(1))
            master_count = int(master_match.group(1))
            
            if tracking_count != master_count:
                self.errors.append(
                    f"Progress count mismatch: Tracking={tracking_count}/12, "
                    f"Master={master_count}/12"
                )
    
    def _check_completion_statuses(self):
        """Check for consistent completion statuses."""
        tracking_content = self.tracking_file.read_text()
        master_content = self.master_file.read_text()
        
        # Check Sub-batch 2A completion
        tracking_2a = "Sub-batch 2A" in tracking_content and "ALL 3 COMPLETE" in tracking_content
        master_2a = "Sub-batch 2A" in master_content and "ALL 3 COMPLETE" in master_content
        
        if tracking_2a != master_2a:
            self.warnings.append(
                "Sub-batch 2A completion status inconsistent between files"
            )
    
    def _check_pending_references(self):
        """Check for 'pending' or 'in progress' references for completed items."""
        tracking_content = self.tracking_file.read_text()
        master_content = self.master_file.read_text()
        
        # Check for DigitalDreamscape pending references
        if "DigitalDreamscape" in tracking_content:
            # Should not have pending/in progress if PR #4 exists
            if "PR #4" in tracking_content:
                if re.search(r'DigitalDreamscape.*pending|DigitalDreamscape.*in progress', 
                           tracking_content, re.IGNORECASE):
                    self.errors.append(
                        "DigitalDreamscape marked as pending/in progress but PR #4 exists"
                    )
        
        if "DigitalDreamscape" in master_content:
            if "PR #4" in master_content:
                if re.search(r'DigitalDreamscape.*pending|DigitalDreamscape.*in progress',
                           master_content, re.IGNORECASE):
                    self.errors.append(
                        "DigitalDreamscape marked as pending/in progress but PR #4 exists (Master)"
                    )
    
    def _check_pr_links(self):
        """Verify PR links present for completed merges."""
        tracking_content = self.tracking_file.read_text()
        
        # Expected PRs
        expected_prs = [
            ("DigitalDreamscape", "PR #4"),
            ("Thea", "PR #3"),
            ("UltimateOptionsTradingRobot", "PR #3"),
            ("TheTradingRobotPlug", "PR #4"),
            ("MeTuber", "PR #13"),
            ("DaDudekC", "PR #1"),
            ("LSTMmodel_trainer", "PR #2"),
        ]
        
        for repo, pr in expected_prs:
            if repo in tracking_content and pr in tracking_content:
                # Check for PR link
                if f"https://github.com" not in tracking_content or pr not in tracking_content:
                    self.warnings.append(
                        f"{repo} has {pr} mentioned but may be missing full PR link"
                    )


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    
    validator = TrackerValidator(repo_root)
    is_valid, errors, warnings = validator.validate()
    
    print("🔍 Tracker Status Validator")
    print("=" * 50)
    
    if is_valid:
        print("✅ All validation checks passed!")
    else:
        print("❌ Validation errors found:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print("\n⚠️  Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    print("\n" + "=" * 50)
    
    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())


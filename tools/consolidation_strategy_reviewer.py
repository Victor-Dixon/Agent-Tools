#!/usr/bin/env python3
"""
Consolidation Strategy Reviewer
================================

Verifies consolidation direction and strategy:
- Validates source → target direction makes sense
- Checks if repos are already merged
- Validates consolidation strategy consistency
- Reviews consolidation plans before execution

V2 Compliant: <400 lines
Author: Agent-4 (Captain)
Date: 2025-12-04
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import status tracker
try:
    from tools.repo_status_tracker import RepoStatusTracker
    STATUS_TRACKER_AVAILABLE = True
except ImportError:
    STATUS_TRACKER_AVAILABLE = False


class ConsolidationStrategyReviewer:
    """Review and validate consolidation strategies."""

    def __init__(self, status_tracker: Optional[RepoStatusTracker] = None):
        """
        Initialize strategy reviewer.
        
        Args:
            status_tracker: Optional RepoStatusTracker instance
        """
        self.status_tracker = status_tracker or (
            RepoStatusTracker() if STATUS_TRACKER_AVAILABLE else None
        )
        self.master_list_path = Path("data/github_75_repos_master_list.json")

    def load_master_list(self) -> Dict:
        """Load master repository list."""
        if not self.master_list_path.exists():
            return {"repos": []}
        
        try:
            with open(self.master_list_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"repos": []}

    def validate_consolidation_direction(
        self, source_repo: str, target_repo: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate consolidation direction makes sense.
        
        Args:
            source_repo: Source repository name
            target_repo: Target repository name
        
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check if repos are the same
        source_norm = source_repo.lower().strip()
        target_norm = target_repo.lower().strip()
        if source_norm == target_norm:
            return False, "Source and target repos are the same"
        
        # Check if already merged
        if self.status_tracker:
            merge_status = self.status_tracker.get_merge_status(source_repo, target_repo)
            if merge_status:
                if merge_status["status"] == "merged":
                    return False, "Already merged - no action needed"
                if merge_status["status"] == "skipped":
                    return False, f"Skipped: {merge_status.get('skip_reason', 'Previously skipped')}"
        
        # Check master list for repo metadata
        master_list = self.load_master_list()
        repos = {r.get("name", "").lower(): r for r in master_list.get("repos", [])}
        
        source_meta = repos.get(source_norm, {})
        target_meta = repos.get(target_norm, {})
        
        # Validate goldmine repos (should extract value before merge)
        if source_meta.get("goldmine") or target_meta.get("goldmine"):
            return True, "Warning: One or both repos are goldmines - ensure value extracted"
        
        # Validate consolidation makes sense (target should be more general/main)
        source_num = source_meta.get("number")
        target_num = target_meta.get("number")
        
        if source_num and target_num:
            # Generally, lower repo numbers indicate more established repos
            if source_num < target_num:
                return True, "Note: Source repo number lower than target - verify direction"
        
        return True, None

    def review_consolidation_plan(
        self, plan: Dict
    ) -> Tuple[bool, List[str]]:
        """
        Review a consolidation plan for issues.
        
        Args:
            plan: Consolidation plan dict with merges list
        
        Returns:
            Tuple of (is_valid, issues)
        """
        issues = []
        merges = plan.get("merges", [])
        
        if not merges:
            issues.append("No merges defined in plan")
            return False, issues
        
        for merge in merges:
            source = merge.get("source")
            target = merge.get("target")
            
            if not source or not target:
                issues.append(f"Invalid merge entry: missing source or target")
                continue
            
            # Validate direction
            is_valid, reason = self.validate_consolidation_direction(source, target)
            if not is_valid:
                issues.append(f"{source} → {target}: {reason}")
            elif reason:
                issues.append(f"{source} → {target}: ⚠️ {reason}")
        
        return len(issues) == 0 or all("⚠️" in issue for issue in issues), issues

    def verify_strategy_consistency(
        self, merges: List[Dict]
    ) -> Tuple[bool, List[str]]:
        """
        Verify consolidation strategy consistency.
        
        Args:
            merges: List of merge operations
        
        Returns:
            Tuple of (is_consistent, inconsistencies)
        """
        inconsistencies = []
        
        # Check for circular dependencies (A→B and B→A)
        merge_map = {}
        for merge in merges:
            source = merge.get("source", "").lower()
            target = merge.get("target", "").lower()
            if source and target:
                if source not in merge_map:
                    merge_map[source] = []
                merge_map[source].append(target)
        
        # Check for circular references
        for source, targets in merge_map.items():
            for target in targets:
                if target in merge_map and source in merge_map[target]:
                    inconsistencies.append(
                        f"Circular dependency: {source} → {target} and {target} → {source}"
                    )
        
        # Check for duplicate merges
        seen = set()
        for merge in merges:
            source = merge.get("source", "").lower()
            target = merge.get("target", "").lower()
            if source and target:
                key = (source, target)
                if key in seen:
                    inconsistencies.append(f"Duplicate merge: {source} → {target}")
                seen.add(key)
        
        # Check for repos being merged into multiple targets
        targets_per_source = {}
        for merge in merges:
            source = merge.get("source", "").lower()
            target = merge.get("target", "").lower()
            if source and target:
                if source not in targets_per_source:
                    targets_per_source[source] = []
                targets_per_source[source].append(target)
        
        for source, targets in targets_per_source.items():
            if len(targets) > 1:
                inconsistencies.append(
                    f"Source {source} being merged into multiple targets: {', '.join(targets)}"
                )
        
        return len(inconsistencies) == 0, inconsistencies

    def generate_strategy_report(
        self, merges: List[Dict]
    ) -> Dict:
        """
        Generate comprehensive strategy review report.
        
        Args:
            merges: List of merge operations
        
        Returns:
            Strategy report dict
        """
        report = {
            "total_merges": len(merges),
            "valid_merges": 0,
            "invalid_merges": 0,
            "warnings": [],
            "errors": [],
            "consistency_check": {},
        }
        
        # Validate each merge
        for merge in merges:
            source = merge.get("source")
            target = merge.get("target")
            is_valid, reason = self.validate_consolidation_direction(source, target)
            
            if is_valid:
                report["valid_merges"] += 1
                if reason and "⚠️" not in reason:
                    report["warnings"].append(f"{source} → {target}: {reason}")
            else:
                report["invalid_merges"] += 1
                report["errors"].append(f"{source} → {target}: {reason}")
        
        # Check consistency
        is_consistent, inconsistencies = self.verify_strategy_consistency(merges)
        report["consistency_check"] = {
            "is_consistent": is_consistent,
            "inconsistencies": inconsistencies,
        }
        
        if not is_consistent:
            report["errors"].extend(inconsistencies)
        
        report["overall_valid"] = (
            report["invalid_merges"] == 0 and report["consistency_check"]["is_consistent"]
        )
        
        return report


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Consolidation Strategy Reviewer")
    parser.add_argument("--plan", type=Path, help="Path to consolidation plan JSON")
    parser.add_argument("--source", help="Source repository name")
    parser.add_argument("--target", help="Target repository name")
    parser.add_argument("--validate", action="store_true", help="Validate single merge")
    parser.add_argument("--report", action="store_true", help="Generate full report")
    
    args = parser.parse_args()
    
    reviewer = ConsolidationStrategyReviewer()
    
    if args.validate and args.source and args.target:
        is_valid, reason = reviewer.validate_consolidation_direction(args.source, args.target)
        if is_valid:
            print(f"✅ Consolidation direction valid")
            if reason:
                print(f"   Note: {reason}")
        else:
            print(f"❌ Consolidation direction invalid: {reason}")
        return 0 if is_valid else 1
    
    if args.plan and args.report:
        plan = json.loads(args.plan.read_text(encoding='utf-8'))
        report = reviewer.generate_strategy_report(plan.get("merges", []))
        print(json.dumps(report, indent=2))
        return 0 if report["overall_valid"] else 1
    
    if args.plan:
        plan = json.loads(args.plan.read_text(encoding='utf-8'))
        is_valid, issues = reviewer.review_consolidation_plan(plan)
        if is_valid:
            print("✅ Consolidation plan valid")
            if issues:
                print("\n⚠️ Warnings:")
                for issue in issues:
                    print(f"   - {issue}")
        else:
            print("❌ Consolidation plan has issues:")
            for issue in issues:
                print(f"   - {issue}")
        return 0 if is_valid else 1
    
    print("Use --help for usage")
    return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())


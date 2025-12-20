#!/usr/bin/env python3
"""
Tracker Validation Automation Tool
===================================

Validates SSOT consistency across consolidation tracker files.
Prevents status drift by comparing key metrics between trackers.

V2 Compliance: <400 lines, single responsibility
Author: Agent-6 (Coordination & Communication Specialist)
Task: A6-TRACKER-VALID-001
Date: 2025-12-03
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class TrackerSnapshot:
    """Snapshot of tracker state for comparison."""
    repos_before: Optional[int] = None
    repos_after: Optional[int] = None
    repos_reduction: Optional[int] = None
    batch1_complete: bool = False
    batch2_complete: bool = False
    batch2_progress: Optional[str] = None
    phase0_complete: bool = False
    skipped_repos: List[str] = field(default_factory=list)
    merged_count: Optional[int] = None
    open_prs_count: Optional[int] = None
    source_file: str = ""


class TrackerParser:
    """Parser for consolidation tracker markdown files."""

    @staticmethod
    def parse_repo_counts(content: str) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """Extract repository counts from tracker."""
        repos_before = None
        repos_after = None
        repos_reduction = None

        # Pattern: "Before Consolidation: 75 repositories"
        before_match = re.search(
            r'before.*consolidation[:\s]+(\d+)\s+repositor', content, re.IGNORECASE
        )
        if before_match:
            repos_before = int(before_match.group(1))

        # Pattern: "Current Count: 59 repositories" or "After...: 59"
        after_match = re.search(
            r'(?:current count|after.*progress|after.*consolidation)[:\s]+(\d+)\s+repositor',
            content, re.IGNORECASE
        )
        if after_match:
            repos_after = int(after_match.group(1))

        # Pattern: "Reduction: 16 repositories"
        reduction_match = re.search(
            r'reduction[:\s]+(\d+)\s+repositor', content, re.IGNORECASE
        )
        if reduction_match:
            repos_reduction = int(reduction_match.group(1))

        return repos_before, repos_after, repos_reduction

    @staticmethod
    def parse_batch_status(content: str) -> Dict[str, bool]:
        """Extract batch completion status."""
        status = {
            'batch1_complete': False,
            'batch2_complete': False,
            'phase0_complete': False,
        }

        # Batch 1: Look for "100% COMPLETE" or "✅ 100%"
        batch1_match = re.search(
            r'batch\s*1[:\s]+.*?100%?\s+complete', content, re.IGNORECASE
        )
        if batch1_match:
            status['batch1_complete'] = True

        # Batch 2: Look for "100% COMPLETE" (not just progress)
        batch2_match = re.search(
            r'batch\s*2[:\s]+.*?100%?\s+complete', content, re.IGNORECASE
        )
        if batch2_match:
            status['batch2_complete'] = True

        # Phase 0: Look for completion status
        phase0_match = re.search(
            r'phase\s*0[:\s]+.*?(?:100%?\s+complete|effectively\s+100%)', content, re.IGNORECASE
        )
        if phase0_match:
            status['phase0_complete'] = True

        return status

    @staticmethod
    def parse_skipped_repos(content: str) -> List[str]:
        """Extract list of skipped repositories."""
        skipped = []
        # Look for skipped repos section
        skipped_section = re.search(
            r'skipped[:\s]+.*?(?:\d+\s+repos|repositories).*?\n(.*?)(?=\n##|\n---|\Z)',
            content, re.IGNORECASE | re.DOTALL
        )
        if skipped_section:
            section_text = skipped_section.group(1)
            # Extract repo names from list items
            repo_matches = re.findall(
                r'[0-9.]+\.\s*[✅❌]?\s*([a-zA-Z0-9_-]+)', section_text
            )
            skipped.extend(repo_matches)

        # Also check for "verified 404" patterns
        verified_404 = re.findall(
            r'([a-zA-Z0-9_-]+)\s*→.*?\(404', content, re.IGNORECASE
        )
        skipped.extend(verified_404)

        return list(set(skipped))  # Remove duplicates

    @staticmethod
    def parse_pr_counts(content: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract PR counts from tracker."""
        merged_count = None
        open_prs_count = None

        # Look for "Completed Merges: 16+ merges"
        merged_match = re.search(
            r'completed\s+merges[:\s]+(\d+)', content, re.IGNORECASE
        )
        if merged_match:
            merged_count = int(merged_match.group(1))

        # Look for "Open PRs: 1 PR"
        open_prs_match = re.search(
            r'open\s+prs[:\s]+(\d+)', content, re.IGNORECASE
        )
        if open_prs_match:
            open_prs_count = int(open_prs_match.group(1))

        return merged_count, open_prs_count

    @staticmethod
    def parse_tracker(file_path: Path) -> TrackerSnapshot:
        """Parse a tracker file and create snapshot."""
        content = file_path.read_text(encoding='utf-8')

        repos_before, repos_after, repos_reduction = TrackerParser.parse_repo_counts(content)
        batch_status = TrackerParser.parse_batch_status(content)
        skipped_repos = TrackerParser.parse_skipped_repos(content)
        merged_count, open_prs_count = TrackerParser.parse_pr_counts(content)

        # Extract Batch 2 progress percentage
        batch2_progress = None
        batch2_progress_match = re.search(
            r'batch\s*2[:\s]+.*?(\d+)%', content, re.IGNORECASE
        )
        if batch2_progress_match:
            batch2_progress = batch2_progress_match.group(1) + "%"

        return TrackerSnapshot(
            repos_before=repos_before,
            repos_after=repos_after,
            repos_reduction=repos_reduction,
            batch1_complete=batch_status['batch1_complete'],
            batch2_complete=batch_status['batch2_complete'],
            batch2_progress=batch2_progress,
            phase0_complete=batch_status['phase0_complete'],
            skipped_repos=skipped_repos,
            merged_count=merged_count,
            open_prs_count=open_prs_count,
            source_file=str(file_path.name)
        )


class TrackerValidator:
    """Validates consistency between tracker files."""

    def __init__(self):
        """Initialize validator."""
        self.issues: List[str] = []
        self.warnings: List[str] = []

    def validate_snapshots(
        self, snapshot1: TrackerSnapshot, snapshot2: TrackerSnapshot
    ) -> bool:
        """Compare two tracker snapshots and report issues."""
        self.issues = []
        self.warnings = []

        # Validate repo counts
        if snapshot1.repos_before and snapshot2.repos_before:
            if snapshot1.repos_before != snapshot2.repos_before:
                self.issues.append(
                    f"❌ Repos before mismatch: {snapshot1.source_file} says {snapshot1.repos_before}, "
                    f"{snapshot2.source_file} says {snapshot2.repos_before}"
                )

        if snapshot1.repos_after and snapshot2.repos_after:
            if snapshot1.repos_after != snapshot2.repos_after:
                self.issues.append(
                    f"❌ Repos after mismatch: {snapshot1.source_file} says {snapshot1.repos_after}, "
                    f"{snapshot2.source_file} says {snapshot2.repos_after}"
                )

        if snapshot1.repos_reduction and snapshot2.repos_reduction:
            if snapshot1.repos_reduction != snapshot2.repos_reduction:
                self.issues.append(
                    f"❌ Reduction mismatch: {snapshot1.source_file} says {snapshot1.repos_reduction}, "
                    f"{snapshot2.source_file} says {snapshot2.repos_reduction}"
                )

        # Validate batch status
        if snapshot1.batch1_complete != snapshot2.batch1_complete:
            self.issues.append(
                f"❌ Batch 1 completion mismatch: {snapshot1.source_file} says "
                f"{snapshot1.batch1_complete}, {snapshot2.source_file} says {snapshot2.batch1_complete}"
            )

        if snapshot1.batch2_complete != snapshot2.batch2_complete:
            self.warnings.append(
                f"⚠️ Batch 2 completion mismatch: {snapshot1.source_file} says "
                f"{snapshot1.batch2_complete}, {snapshot2.source_file} says {snapshot2.batch2_complete}"
            )

        # Validate skipped repos (should match)
        skipped1_set = set(snapshot1.skipped_repos)
        skipped2_set = set(snapshot2.skipped_repos)
        if skipped1_set != skipped2_set:
            missing_in_2 = skipped1_set - skipped2_set
            missing_in_1 = skipped2_set - skipped1_set
            if missing_in_2:
                self.warnings.append(
                    f"⚠️ Skipped repos in {snapshot1.source_file} but not in {snapshot2.source_file}: "
                    f"{', '.join(missing_in_2)}"
                )
            if missing_in_1:
                self.warnings.append(
                    f"⚠️ Skipped repos in {snapshot2.source_file} but not in {snapshot1.source_file}: "
                    f"{', '.join(missing_in_1)}"
                )

        return len(self.issues) == 0

    def generate_report(
        self, snapshot1: TrackerSnapshot, snapshot2: TrackerSnapshot
    ) -> str:
        """Generate human-readable validation report."""
        report_lines = [
            "=" * 70,
            "📊 TRACKER VALIDATION REPORT",
            "=" * 70,
            "",
            f"**Tracker 1**: {snapshot1.source_file}",
            f"**Tracker 2**: {snapshot2.source_file}",
            "",
        ]

        # Add snapshot summaries
        report_lines.extend([
            "## 📈 Snapshot Comparison",
            "",
            f"| Metric | {snapshot1.source_file} | {snapshot2.source_file} |",
            "|--------|------------------------|------------------------|",
        ])

        if snapshot1.repos_before and snapshot2.repos_before:
            match = "✅" if snapshot1.repos_before == snapshot2.repos_before else "❌"
            report_lines.append(
                f"| Repos Before | {snapshot1.repos_before} | {snapshot2.repos_before} | {match}"
            )

        if snapshot1.repos_after and snapshot2.repos_after:
            match = "✅" if snapshot1.repos_after == snapshot2.repos_after else "❌"
            report_lines.append(
                f"| Repos After | {snapshot1.repos_after} | {snapshot2.repos_after} | {match}"
            )

        if snapshot1.repos_reduction and snapshot2.repos_reduction:
            match = "✅" if snapshot1.repos_reduction == snapshot2.repos_reduction else "❌"
            report_lines.append(
                f"| Reduction | {snapshot1.repos_reduction} | {snapshot2.repos_reduction} | {match}"
            )

        batch1_match = "✅" if snapshot1.batch1_complete == snapshot2.batch1_complete else "❌"
        report_lines.append(
            f"| Batch 1 Complete | {snapshot1.batch1_complete} | {snapshot2.batch1_complete} | {batch1_match}"
        )

        batch2_match = "✅" if snapshot1.batch2_complete == snapshot2.batch2_complete else "⚠️"
        report_lines.append(
            f"| Batch 2 Complete | {snapshot1.batch2_complete} | {snapshot2.batch2_complete} | {batch2_match}"
        )

        if snapshot1.batch2_progress and snapshot2.batch2_progress:
            match = "✅" if snapshot1.batch2_progress == snapshot2.batch2_progress else "⚠️"
            report_lines.append(
                f"| Batch 2 Progress | {snapshot1.batch2_progress} | {snapshot2.batch2_progress} | {match}"
            )

        report_lines.extend(["", "## 🔍 Validation Results", ""])

        if len(self.issues) == 0 and len(self.warnings) == 0:
            report_lines.append("✅ **NO DRIFT DETECTED** - Trackers are consistent!")
        else:
            if self.issues:
                report_lines.append("### ❌ Critical Issues:")
                for issue in self.issues:
                    report_lines.append(f"- {issue}")
                report_lines.append("")

            if self.warnings:
                report_lines.append("### ⚠️ Warnings:")
                for warning in self.warnings:
                    report_lines.append(f"- {warning}")

        report_lines.extend([
            "",
            "=" * 70,
            "🐝 WE. ARE. SWARM. ⚡🔥",
            "",
        ])

        return "\n".join(report_lines)


def main():
    """Main validation function."""
    project_root = Path(__file__).parent.parent
    docs_org = project_root / "docs" / "organization"

    # Primary tracker files
    tracker1_path = docs_org / "GITHUB_CONSOLIDATION_FINAL_TRACKER_2025-11-29.md"
    tracker2_path = docs_org / "MASTER_CONSOLIDATION_TRACKER_UPDATE_2025-11-29.md"

    print("🔍 Tracker Validation Tool")
    print("=" * 70)
    print()

    # Check if files exist
    if not tracker1_path.exists():
        print(f"❌ Tracker 1 not found: {tracker1_path}")
        return 1

    if not tracker2_path.exists():
        print(f"⚠️ Tracker 2 not found: {tracker2_path}")
        print("   Validating single tracker only...")
        tracker2_path = None

    # Parse trackers
    print(f"📖 Parsing {tracker1_path.name}...")
    snapshot1 = TrackerParser.parse_tracker(tracker1_path)

    if tracker2_path:
        print(f"📖 Parsing {tracker2_path.name}...")
        snapshot2 = TrackerParser.parse_tracker(tracker2_path)

        # Validate
        print("🔍 Validating consistency...")
        validator = TrackerValidator()
        is_valid = validator.validate_snapshots(snapshot1, snapshot2)

        # Generate report
        report = validator.generate_report(snapshot1, snapshot2)
        print()
        print(report)

        # Save report
        report_path = project_root / "docs" / "organization" / "TRACKER_VALIDATION_REPORT.md"
        report_path.write_text(report, encoding='utf-8')
        print(f"💾 Report saved to: {report_path}")

        return 0 if is_valid else 1
    else:
        # Single tracker summary
        print()
        print("📊 Single Tracker Summary:")
        print(f"   Repos Before: {snapshot1.repos_before}")
        print(f"   Repos After: {snapshot1.repos_after}")
        print(f"   Reduction: {snapshot1.repos_reduction}")
        print(f"   Batch 1 Complete: {snapshot1.batch1_complete}")
        print(f"   Batch 2 Complete: {snapshot1.batch2_complete}")
        print(f"   Batch 2 Progress: {snapshot1.batch2_progress}")
        print(f"   Skipped Repos: {len(snapshot1.skipped_repos)}")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())



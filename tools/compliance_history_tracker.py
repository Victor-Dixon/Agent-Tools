#!/usr/bin/env python3
"""
Compliance History Tracker - Trend Analysis
============================================

Tracks V2 compliance and complexity metrics over time.
Stores historical data in SQLite and generates trend reports.

Refactored into modular components:
- compliance_history_models.py: Data models
- compliance_history_database.py: DB operations
- compliance_history_reports.py: Trend analysis and reporting

Features:
- Historical compliance tracking
- Trend analysis and visualization
- Progress tracking over commits
- Improvement/degradation detection

Author: Agent-6 (VSCode Forking & Quality Gates Specialist)
Refactored: 2025-10-11 (473L → ~250L)
License: MIT
"""

from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from tools.compliance_history_database import ComplianceDatabase
    from tools.compliance_history_models import ComplianceSnapshot, TrendReport
    from tools.compliance_history_reports import ComplianceReports
except ImportError:
    # Fallback: modules may not exist yet, define minimal stubs
    class ComplianceDatabase:
        def __init__(self, *args, **kwargs):
            pass

    class ComplianceSnapshot:
        pass

    class TrendReport:
        pass

    class ComplianceReports:
        pass

try:
    from tools.complexity_analyzer import ComplexityAnalysisService
    from tools.v2_compliance_checker import V2ComplianceChecker

    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False


class ComplianceHistoryTracker:
    """Tracks compliance history and trends."""

    def __init__(self, db_path: str = "data/compliance_history.db"):
        """Initialize history tracker."""
        self.db = ComplianceDatabase(db_path)
        self.reports = ComplianceReports()

    def record_snapshot(self, directory: str, commit_hash: str | None = None) -> ComplianceSnapshot:
        """Record current compliance snapshot."""
        if not TOOLS_AVAILABLE:
            raise RuntimeError("Quality tools not available")

        print("📊 Collecting current compliance metrics...")

        # Run V2 compliance check
        v2_checker = V2ComplianceChecker(directory)
        v2_report = v2_checker.scan_directory(Path(directory), "**/*.py")

        # Run complexity analysis
        complexity_service = ComplexityAnalysisService()
        complexity_reports = complexity_service.analyze_directory(
            directory, "**/*.py")

        # Calculate metrics
        files_with_complexity = [
            r for r in complexity_reports if r.has_violations]
        complexity_rate = (
            (len(complexity_reports) - len(files_with_complexity)) /
            len(complexity_reports) * 100
            if complexity_reports
            else 100
        )

        high = sum(
            len([v for v in r.violations if v.severity == "HIGH"]) for r in files_with_complexity
        )
        medium = sum(
            len([v for v in r.violations if v.severity == "MEDIUM"]) for r in files_with_complexity
        )

        # Calculate overall score
        base_score = (v2_report.compliance_rate + complexity_rate) / 2
        penalty = (len(v2_report.critical_violations) * 5) + (high * 2)
        overall_score = max(0, base_score - penalty)

        # Create snapshot
        snapshot = ComplianceSnapshot(
            timestamp=datetime.now().isoformat(),
            commit_hash=commit_hash,
            total_files=v2_report.total_files,
            v2_compliance_rate=v2_report.compliance_rate,
            complexity_compliance_rate=complexity_rate,
            critical_violations=len(v2_report.critical_violations),
            major_violations=len(v2_report.major_violations),
            high_complexity=high,
            medium_complexity=medium,
            overall_score=round(overall_score, 1),
        )

        # Save to database
        self.db.save_snapshot(snapshot)

        print(f"✅ Snapshot recorded: Score {snapshot.overall_score}")
        return snapshot

    def get_recent_snapshots(self, limit: int = 10) -> list[ComplianceSnapshot]:
        """Get recent snapshots."""
        return self.db.get_recent_snapshots(limit)

    def get_all_snapshots(self) -> list[ComplianceSnapshot]:
        """Get all snapshots ordered by timestamp."""
        return self.db.get_all_snapshots()

    def get_trend_data(self) -> dict[str, list[Any]]:
        """Get trend data formatted for charts."""
        snapshots = self.get_all_snapshots()
        return self.reports.get_trend_data(snapshots)

    def get_week_comparison(self) -> dict[str, Any] | None:
        """Get week-over-week comparison data."""
        snapshots = self.get_all_snapshots()
        return self.reports.get_week_comparison(snapshots)

    def generate_trend_report(self, limit: int = 10) -> TrendReport | None:
        """Generate trend analysis report."""
        snapshots = self.get_recent_snapshots(limit)
        return self.reports.generate_trend_report(snapshots)

    def format_trend_report(self, report: TrendReport) -> str:
        """Format trend report as string."""
        return self.reports.format_trend_report(report)


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Compliance History Tracker")
    parser.add_argument(
        "command",
        choices=["snapshot", "report", "list"],
        help="Command: snapshot (record), report (trend), list (history)",
    )
    parser.add_argument("directory", nargs="?",
                        default="src", help="Directory to analyze")
    parser.add_argument("--commit", help="Commit hash for snapshot")
    parser.add_argument("--limit", type=int, default=10,
                        help="Number of snapshots for report")

    args = parser.parse_args()

    tracker = ComplianceHistoryTracker()

    if args.command == "snapshot":
        # Record new snapshot
        snapshot = tracker.record_snapshot(args.directory, args.commit)
        print("\n✅ Snapshot recorded!")
        print(f"Score: {snapshot.overall_score}")
        print(f"V2 Compliance: {snapshot.v2_compliance_rate:.1f}%")
        print(f"Complexity: {snapshot.complexity_compliance_rate:.1f}%")

    elif args.command == "report":
        # Generate trend report
        report = tracker.generate_trend_report(args.limit)
        if report:
            print(tracker.format_trend_report(report))
        else:
            print("⚠️ Not enough data for trend analysis (need at least 2 snapshots)")

    elif args.command == "list":
        # List recent snapshots
        snapshots = tracker.get_recent_snapshots(args.limit)
        print(f"Recent {len(snapshots)} snapshots:")
        for s in snapshots:
            date = datetime.fromisoformat(
                s.timestamp).strftime("%Y-%m-%d %H:%M")
            print(
                f"{date} - Score: {s.overall_score:.1f}, V2: {s.v2_compliance_rate:.1f}%, Complexity: {s.complexity_compliance_rate:.1f}%"
            )


if __name__ == "__main__":
    main()

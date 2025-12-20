#!/usr/bin/env python3
"""
Compliance Dashboard - Intelligent Quality Automation
======================================================

Generates visual HTML dashboards with:
- V2 compliance violations (charts and tables)
- Complexity metrics (heatmaps and trends)
- Refactoring suggestions (actionable lists)
- Overall quality score

Author: Agent-6 (VSCode Forking & Quality Gates Specialist)
License: MIT
"""

from datetime import datetime
from pathlib import Path

# Import our quality tools
try:
    from complexity_analyzer import ComplexityAnalysisService
    from compliance_history_tracker import ComplianceHistoryTracker
    from dashboard_data_aggregator import DashboardDataAggregator
    from dashboard_html_generator_refactored import DashboardHTMLGenerator
    from refactoring_suggestion_engine import RefactoringSuggestionService
    from v2_compliance_checker import V2ComplianceChecker

    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False


class ComplianceDashboard:
    """Generates compliance dashboards."""

    def __init__(self, output_dir: str = "reports/dashboards"):
        """Initialize dashboard generator."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.aggregator = DashboardDataAggregator() if TOOLS_AVAILABLE else None
        self.html_generator = DashboardHTMLGenerator() if TOOLS_AVAILABLE else None

    def generate_dashboard(
        self, directory: str, pattern: str = "**/*.py", include_history: bool = True
    ) -> str | None:
        """Generate complete compliance dashboard with optional historical trends."""
        if not TOOLS_AVAILABLE:
            print("❌ Quality tools not available")
            return None

        print("🔄 Collecting compliance data...")

        # Collect V2 compliance data
        v2_checker = V2ComplianceChecker(directory)
        v2_report = v2_checker.scan_directory(Path(directory), pattern)

        # Collect complexity data
        complexity_service = ComplexityAnalysisService()
        complexity_reports = complexity_service.analyze_directory(directory, pattern)

        # Collect refactoring suggestions
        suggestion_service = RefactoringSuggestionService()
        suggestions = suggestion_service.analyze_directory(directory, pattern)

        # Collect historical data if requested
        historical_data = None
        week_comparison = None
        if include_history:
            print("📈 Collecting historical trend data...")
            history_tracker = ComplianceHistoryTracker()
            try:
                historical_data = history_tracker.get_trend_data()
                week_comparison = history_tracker.get_week_comparison()
                if historical_data and historical_data.get("dates"):
                    print(f"   Found {len(historical_data['dates'])} historical snapshots")
                else:
                    print("   No historical data available yet")
                    historical_data = None
            except Exception as e:
                print(f"   Warning: Could not load historical data: {e}")
                historical_data = None

        print("📊 Generating dashboard...")

        # Aggregate data
        dashboard_data = self.aggregator.aggregate_data(v2_report, complexity_reports, suggestions)

        # Add historical data to dashboard
        if historical_data:
            dashboard_data.historical = historical_data
        if week_comparison:
            dashboard_data.week_comparison = week_comparison

        # Generate HTML
        html = self.html_generator.generate_html(dashboard_data)

        # Save dashboard
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"compliance_dashboard_{timestamp}.html"
        output_path.write_text(html, encoding="utf-8")

        print(f"✅ Dashboard generated: {output_path}")
        return str(output_path)


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Compliance Dashboard Generator")
    parser.add_argument("directory", nargs="?", default="src", help="Directory to analyze")
    parser.add_argument("--pattern", default="**/*.py", help="File pattern")
    parser.add_argument("--output", "-o", default="reports/dashboards", help="Output directory")
    parser.add_argument("--no-history", action="store_true", help="Disable historical trend data")

    args = parser.parse_args()

    dashboard = ComplianceDashboard(args.output)
    output_path = dashboard.generate_dashboard(
        args.directory, args.pattern, include_history=not args.no_history
    )

    if output_path:
        print(f"\n✅ Dashboard ready: {output_path}")
        print("📂 Open in browser to view")
    else:
        print("\n❌ Failed to generate dashboard")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
V2 Checker Formatters - Report Formatting
==========================================

Report formatting and display logic for V2 compliance checker.
Extracted from v2_compliance_checker.py for V2 compliance.

Author: Agent-6 (VSCode Forking & Quality Gates Specialist)
License: MIT
"""

try:
    from .v2_checker_models import ComplianceReport, ComplianceViolation
except ImportError:
    from v2_checker_models import ComplianceReport, ComplianceViolation

# Import optional tools
try:
    from refactoring_suggestion_engine import RefactoringSuggestionService

    SUGGESTIONS_AVAILABLE = True
except ImportError:
    SUGGESTIONS_AVAILABLE = False

try:
    from complexity_analyzer import ComplexityAnalyzer

    COMPLEXITY_AVAILABLE = True
except ImportError:
    COMPLEXITY_AVAILABLE = False


def get_file_suggestions(file_path: str) -> str:
    """Get refactoring suggestions for a file."""
    if not SUGGESTIONS_AVAILABLE:
        return ""

    try:
        service = RefactoringSuggestionService()
        suggestion = service.analyze_and_suggest(file_path)

        if suggestion and suggestion.suggested_modules:
            lines = ["\n  💡 REFACTORING SUGGESTIONS:"]
            lines.append(
                f"  Confidence: {suggestion.confidence * 100:.0f}% | "
                f"Estimated result: {suggestion.estimated_main_file_lines} lines"
            )

            for module in suggestion.suggested_modules[:2]:  # Show top 2
                entity_count = len(module.entities)
                lines.append(
                    f"    → Extract to {module.module_name} "
                    f"({module.estimated_lines} lines, {entity_count} entities)"
                )

            if len(suggestion.suggested_modules) > 2:
                lines.append(
                    f"    ... +{len(suggestion.suggested_modules) - 2} more suggested modules"
                )

            lines.append(
                f"  Run: python tools/refactoring_suggestion_engine.py {file_path} --detailed"
            )
            return "\n".join(lines)

        return ""
    except Exception:
        return ""


def get_complexity_analysis(file_path: str) -> str:
    """Get complexity analysis for a file."""
    if not COMPLEXITY_AVAILABLE:
        return ""

    try:
        analyzer = ComplexityAnalyzer()
        report = analyzer.analyze_file(file_path)

        if report:
            lines = ["\n  📊 COMPLEXITY METRICS:"]
            lines.append(
                f"  Avg Cyclomatic: {report.avg_cyclomatic:.1f} | "
                f"Avg Cognitive: {report.avg_cognitive:.1f} | "
                f"Max Nesting: {report.max_nesting}"
            )

            if report.has_violations:
                high = [v for v in report.violations if v.severity == "HIGH"]
                medium = [v for v in report.violations if v.severity == "MEDIUM"]
                low = [v for v in report.violations if v.severity == "LOW"]

                lines.append(
                    f"  Violations: {len(report.violations)} "
                    f"(🔴{len(high)} 🟡{len(medium)} 🟢{len(low)})"
                )

                # Show worst violation
                worst = max(report.violations, key=lambda x: x.current_value)
                lines.append(
                    f"  Worst: {worst.entity_name} "
                    f"({worst.violation_type}={worst.current_value}, threshold={worst.threshold})"
                )
            else:
                lines.append("  ✅ All functions have acceptable complexity")

            lines.append(f"  Run: python tools/complexity_analyzer.py {file_path} --verbose")
            return "\n".join(lines)

        return ""
    except Exception:
        return ""


def format_report(
    report: ComplianceReport,
    violations_by_file: dict[str, list[ComplianceViolation]],
    verbose: bool = False,
    show_suggestions: bool = False,
    show_complexity: bool = False,
) -> str:
    """Format compliance report as readable text."""
    lines = []
    lines.append("=" * 80)
    lines.append("V2 COMPLIANCE REPORT")
    lines.append("=" * 80)
    lines.append(f"Total files scanned: {report.total_files}")
    lines.append(f"Compliant files: {report.compliant_files}")
    lines.append(f"Files with violations: {report.total_files - report.compliant_files}")
    lines.append(f"Compliance rate: {report.compliance_rate:.1f}%")
    lines.append("")

    if report.violations:
        lines.append(f"VIOLATIONS FOUND: {len(report.violations)}")
        lines.append(f"  - Critical: {len(report.critical_violations)} (>600 lines)")
        lines.append(f"  - Major: {len(report.major_violations)} (>400 lines or rule violations)")
        lines.append(f"  - Minor: {len(report.minor_violations)}")
        lines.append("")

        for file_path, violations in sorted(violations_by_file.items()):
            lines.append(f"\n{file_path}:")
            for v in violations:
                severity_marker = {
                    "CRITICAL": "🔴",
                    "MAJOR": "🟡",
                    "MINOR": "🟢",
                }.get(v.severity, "⚪")

                location = f"line {v.line_number}" if v.line_number else "file"
                lines.append(f"  {severity_marker} [{v.severity}] {location}: {v.message}")

            # Add refactoring suggestions
            if show_suggestions and SUGGESTIONS_AVAILABLE:
                file_size_violations = [v for v in violations if v.violation_type == "FILE_SIZE"]
                if file_size_violations:
                    lines.append(get_file_suggestions(file_path))

            # Add complexity analysis
            if show_complexity and COMPLEXITY_AVAILABLE:
                lines.append(get_complexity_analysis(file_path))

    else:
        lines.append("✅ All files are V2 compliant!")

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Functionality Verification Tool
===============================

Comprehensive verification system for consolidation safety.
Ensures 100% functionality preservation during file consolidation.

Refactored into modular components:
- functionality_signature.py: Signature generation
- functionality_comparison.py: Baseline comparison
- functionality_tests.py: Agent-specific tests
- functionality_reports.py: Report generation

Usage:
    python tools/functionality_verification.py --baseline
    python tools/functionality_verification.py --compare
    python tools/functionality_verification.py --agent-id Agent-X
    python tools/functionality_verification.py --comprehensive

Author: Agent-6 (VSCode Forking & Quality Gates Specialist)
Refactored: 2025-10-11 (462L → ~250L)
License: MIT
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.functionality_comparison import FunctionalityComparison
from tools.functionality_reports import FunctionalityReports
from tools.functionality_signature import SignatureGenerator
from tools.functionality_tests import FunctionalityTests


class FunctionalityVerifier:
    """Comprehensive functionality verification system."""

    def __init__(self):
        """Initialize verifier with modular components."""
        self.project_root = project_root
        self.baseline_file = self.project_root / "verification_baseline.json"
        self.results_dir = self.project_root / "verification_results"
        self.results_dir.mkdir(exist_ok=True)

        # Initialize modular components
        self.signature_gen = SignatureGenerator(self.project_root)
        self.comparison = FunctionalityComparison(self.baseline_file)
        self.tests = FunctionalityTests()
        self.reports = FunctionalityReports()

    def generate_functionality_signature(self) -> dict[str, Any]:
        """Generate comprehensive functionality signature."""
        return self.signature_gen.generate_signature()

    def save_baseline(self, signature: dict[str, Any]) -> None:
        """Save functionality baseline."""
        self.comparison.save_baseline(signature)

    def load_baseline(self) -> dict[str, Any] | None:
        """Load functionality baseline."""
        return self.comparison.load_baseline()

    def compare_with_baseline(self, current_signature: dict[str, Any]) -> dict[str, Any]:
        """Compare current state with baseline."""
        return self.comparison.compare_with_baseline(current_signature)

    def run_agent_specific_verification(self, agent_id: str) -> dict[str, Any]:
        """Run agent-specific functionality verification."""
        return self.tests.run_agent_tests(agent_id)

    def generate_verification_report(
        self, comparison: dict[str, Any], agent_results: list[dict[str, Any]]
    ) -> str:
        """Generate comprehensive verification report."""
        report = []
        report.append("# 🔍 CONSOLIDATION VERIFICATION REPORT")
        report.append(f"**Generated:** {datetime.now().isoformat()}")
        report.append(f"**Risk Assessment:** {comparison.get('risk_assessment', 'UNKNOWN')}")
        report.append("")

        # Summary
        report.append("## 📊 SUMMARY")
        report.append(f"- Files Changed: {len(comparison.get('files_changed', []))}")
        report.append(f"- Functions Lost: {len(comparison.get('functions_lost', []))}")
        report.append(f"- New Functions: {len(comparison.get('new_functions', []))}")
        report.append(f"- Agents Verified: {len(agent_results)}")
        report.append("")

        # Agent Status
        report.append("## 👥 AGENT VERIFICATION STATUS")
        for agent_result in agent_results:
            status = agent_result.get("functionality_status", "UNKNOWN")
            status_icon = {
                "FULLY_FUNCTIONAL": "✅",
                "MINOR_ISSUES": "⚠️",
                "SIGNIFICANT_ISSUES": "❌",
                "NO_TESTS": "❓",
            }.get(status, "❓")

            passed = len(agent_result.get("tests_passed", []))
            total = len(agent_result.get("tests_run", []))
            report.append(
                f"- {status_icon} **{agent_result['agent_id']}**: {passed}/{total} tests passed"
            )
        report.append("")

        # Detailed Changes
        if comparison.get("functions_lost"):
            report.append("## ⚠️ FUNCTIONS/CLASSES LOST")
            for item in comparison["functions_lost"][:20]:
                report.append(f"- ❌ {item}")
            if len(comparison["functions_lost"]) > 20:
                report.append(f"- ... and {len(comparison['functions_lost']) - 20} more")
            report.append("")

        if comparison.get("files_changed"):
            report.append("## 📁 FILES CHANGED")
            for change in comparison["files_changed"][:20]:
                report.append(f"- 📄 {change}")
            if len(comparison["files_changed"]) > 20:
                report.append(f"- ... and {len(comparison['files_changed']) - 20} more")
            report.append("")

        # Recommendations
        report.append("## 🎯 RECOMMENDATIONS")
        if comparison.get("functions_lost"):
            report.append(
                "❌ **IMMEDIATE ACTION REQUIRED:** Functions/classes lost during consolidation"
            )
            report.append("   - Review consolidation approach")
            report.append("   - Consider selective rollback")
        elif comparison.get("risk_assessment") == "HIGH":
            report.append("⚠️ **HIGH RISK:** Significant changes detected")
            report.append("   - Conduct thorough manual testing")
            report.append("   - Prepare rollback procedures")
        elif comparison.get("risk_assessment") == "MEDIUM":
            report.append("🟡 **MEDIUM RISK:** Moderate changes detected")
            report.append("   - Continue with enhanced monitoring")
            report.append("   - Complete agent verification")
        else:
            report.append("✅ **LOW RISK:** Minimal changes detected")
            report.append("   - Proceed with consolidation")
            report.append("   - Maintain monitoring")

        return "\n".join(report)


def main():
    """Main verification function."""
    import argparse

    parser = argparse.ArgumentParser(description="Functionality Verification Tool")
    parser.add_argument("--baseline", action="store_true", help="Generate functionality baseline")
    parser.add_argument("--compare", action="store_true", help="Compare with baseline")
    parser.add_argument("--agent-id", help="Run agent-specific verification")
    parser.add_argument(
        "--comprehensive", action="store_true", help="Run comprehensive verification"
    )
    parser.add_argument("--report", action="store_true", help="Generate verification report")

    args = parser.parse_args()

    verifier = FunctionalityVerifier()

    if args.baseline:
        print("🔍 Generating functionality baseline...")
        signature = verifier.generate_functionality_signature()
        verifier.save_baseline(signature)
        print("✅ Baseline generated successfully")

    elif args.agent_id:
        print(f"🔍 Running verification for {args.agent_id}...")
        results = verifier.run_agent_specific_verification(args.agent_id)

        print(f"📊 {args.agent_id} Verification Results:")
        print(f"   Status: {results['functionality_status']}")
        print(f"   Tests Run: {len(results['tests_run'])}")
        print(f"   Tests Passed: {len(results['tests_passed'])}")
        print(f"   Tests Failed: {len(results['tests_failed'])}")

        if results["tests_failed"]:
            print("   Failed Tests:")
            for failure in results["tests_failed"]:
                print(f"     - {failure.get('test', 'Unknown')}: {failure.get('error', 'FAILED')}")

    elif args.comprehensive:
        print("🔍 Running comprehensive verification...")
        current_signature = verifier.generate_functionality_signature()
        comparison = verifier.compare_with_baseline(current_signature)

        # Run agent verifications
        agent_results = []
        agent_ids = ["Agent-1", "Agent-2", "Agent-3", "Agent-4", "Agent-6", "Agent-7", "Agent-8"]
        for agent_id in agent_ids:
            print(f"Verifying {agent_id}...")
            result = verifier.run_agent_specific_verification(agent_id)
            agent_results.append(result)

        # Generate report
        report = verifier.generate_verification_report(comparison, agent_results)

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = verifier.results_dir / f"verification_report_{timestamp}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print("✅ Comprehensive verification complete")
        print(f"📄 Report saved to: {report_file}")

        # Print summary
        print("\n📊 SUMMARY:")
        print(f"   Risk Assessment: {comparison.get('risk_assessment', 'UNKNOWN')}")
        print(f"   Functions Lost: {len(comparison.get('functions_lost', []))}")
        print(f"   Files Changed: {len(comparison.get('files_changed', []))}")
        print(f"   Agents Verified: {len(agent_results)}")

        functional_count = sum(
            1 for r in agent_results if r.get("functionality_status") == "FULLY_FUNCTIONAL"
        )
        print(f"   Fully Functional: {functional_count}/{len(agent_results)}")

    else:
        print("Usage:")
        print("  python tools/functionality_verification.py --baseline")
        print("  python tools/functionality_verification.py --compare")
        print("  python tools/functionality_verification.py --agent-id Agent-X")
        print("  python tools/functionality_verification.py --comprehensive")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test Pyramid Analyzer
=====================

Analyzes test distribution and compares to 60/30/10 pyramid target.
Calculates actual percentages from test counts.

Author: Agent-8 (Operations & Support Specialist)
Created: 2025-10-13
"""

import sys
from pathlib import Path


def count_tests_in_file(file_path: Path) -> int:
    """Count test cases in a file."""
    try:
        content = file_path.read_text(encoding="utf-8")

        # Count test/it blocks (Jest/Mocha)
        test_count = content.count("test(") + content.count("it(")

        return test_count
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0


def analyze_pyramid(test_dir: Path) -> dict[str, any]:
    """Analyze test pyramid distribution."""

    unit_dir = test_dir / "unit"
    integration_dir = test_dir / "integration"
    e2e_dir = test_dir / "e2e"

    unit_tests = 0
    integration_tests = 0
    e2e_tests = 0

    # Count unit tests
    if unit_dir.exists():
        for test_file in unit_dir.rglob("*.test.ts"):
            unit_tests += count_tests_in_file(test_file)
        for test_file in unit_dir.rglob("*.test.js"):
            unit_tests += count_tests_in_file(test_file)

    # Count integration tests
    if integration_dir.exists():
        for test_file in integration_dir.rglob("*.test.ts"):
            integration_tests += count_tests_in_file(test_file)
        for test_file in integration_dir.rglob("*.test.js"):
            integration_tests += count_tests_in_file(test_file)

    # Count E2E tests
    if e2e_dir.exists():
        for test_file in e2e_dir.rglob("*.test.ts"):
            e2e_tests += count_tests_in_file(test_file)
        for test_file in e2e_dir.rglob("*.test.js"):
            e2e_tests += count_tests_in_file(test_file)

    total = unit_tests + integration_tests + e2e_tests

    if total == 0:
        return {
            "unit": 0,
            "integration": 0,
            "e2e": 0,
            "total": 0,
            "unit_pct": 0,
            "integration_pct": 0,
            "e2e_pct": 0,
        }

    return {
        "unit": unit_tests,
        "integration": integration_tests,
        "e2e": e2e_tests,
        "total": total,
        "unit_pct": (unit_tests / total) * 100,
        "integration_pct": (integration_tests / total) * 100,
        "e2e_pct": (e2e_tests / total) * 100,
    }


def print_pyramid_report(analysis: dict[str, any]):
    """Print pyramid analysis report."""

    print("\n" + "=" * 80)
    print("🧪 TEST PYRAMID ANALYSIS")
    print("=" * 80)

    if analysis["total"] == 0:
        print("\n❌ No tests found!")
        print("=" * 80 + "\n")
        return

    # Actual distribution
    print("\n📊 ACTUAL DISTRIBUTION:")
    print(
        f"  Unit Tests:        {analysis['unit']:3d} ({analysis['unit_pct']:5.1f}%)")
    print(
        f"  Integration Tests: {analysis['integration']:3d} ({analysis['integration_pct']:5.1f}%)"
    )
    print(
        f"  E2E Tests:         {analysis['e2e']:3d} ({analysis['e2e_pct']:5.1f}%)")
    print(f"  {'─'*40}")
    print(f"  TOTAL:             {analysis['total']:3d} (100.0%)")

    # Target distribution
    print("\n🎯 TARGET DISTRIBUTION (60/30/10):")
    print("  Unit Tests:        60%")
    print("  Integration Tests: 30%")
    print("  E2E Tests:         10%")

    # Variance
    unit_var = analysis["unit_pct"] - 60
    int_var = analysis["integration_pct"] - 30
    e2e_var = analysis["e2e_pct"] - 10

    print("\n📈 VARIANCE FROM TARGET:")
    print(
        f"  Unit:        {unit_var:+6.1f}%  {'✅' if abs(unit_var) <= 10 else '⚠️'}")
    print(
        f"  Integration: {int_var:+6.1f}%  {'✅' if abs(int_var) <= 10 else '⚠️'}")
    print(
        f"  E2E:         {e2e_var:+6.1f}%  {'✅' if abs(e2e_var) <= 5 else '⚠️'}")

    # Overall assessment
    print("\n🏆 ASSESSMENT:")

    if abs(unit_var) <= 10 and abs(int_var) <= 10 and abs(e2e_var) <= 5:
        print("  ✅ EXCELLENT - Distribution matches 60/30/10 target!")
    elif abs(unit_var) <= 15 and abs(int_var) <= 15 and abs(e2e_var) <= 10:
        print("  ✅ GOOD - Distribution close to 60/30/10 target!")
    else:
        print("  ⚠️ NEEDS ADJUSTMENT - Distribution differs from 60/30/10 target")

        if unit_var < -10:
            print(
                f"     Suggestion: Add {int(abs(unit_var) * analysis['total'] / 100)} more unit tests"
            )
        if int_var < -10:
            print(
                f"     Suggestion: Add {int(abs(int_var) * analysis['total'] / 100)} more integration tests"
            )
        if e2e_var < -5:
            print(
                f"     Suggestion: Add {int(abs(e2e_var) * analysis['total'] / 100)} more E2E tests"
            )

    print("=" * 80 + "\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python test_pyramid_analyzer.py <test_directory>")
        print("\nExample:")
        print(
            "  python test_pyramid_analyzer.py extensions/repository-navigator/test/suite")
        sys.exit(1)

    test_dir = Path(sys.argv[1])

    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        sys.exit(1)

    analysis = analyze_pyramid(test_dir)
    print_pyramid_report(analysis)


if __name__ == "__main__":
    main()

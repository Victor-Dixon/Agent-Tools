#!/usr/bin/env python3
"""
Real Violation Scanner - Intelligent Verification
==================================================

Scans for ACTUAL V2 violations by checking current line counts.
Prevents claiming already-fixed work (Swarm Brain Pattern #1).

Author: Agent-2 - Architecture & Design Specialist
Date: 2025-10-12
License: MIT
"""

import argparse
import sys
from pathlib import Path


def scan_file(file_path: Path) -> tuple[str, int]:
    """
    Scan a file for actual line count.

    Args:
        file_path: Path to file

    Returns:
        Tuple of (file_path, line_count)
    """
    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            lines = len(f.readlines())
        return (str(file_path), lines)
    except Exception:
        return (str(file_path), 0)


def find_real_violations(threshold: int = 400) -> list[tuple[str, int]]:
    """
    Find files that are ACTUALLY over the threshold.

    Args:
        threshold: Line count threshold (default: 400)

    Returns:
        List of (file_path, line_count) tuples for violations
    """
    violations = []

    # Scan Python files
    for py_file in Path(".").rglob("*.py"):
        # Skip common excludes
        if any(x in str(py_file) for x in ["venv", "node_modules", ".git", "__pycache__"]):
            continue

        file_path, lines = scan_file(py_file)
        if lines > threshold:
            violations.append((file_path, lines))

    return sorted(violations, key=lambda x: -x[1])


def verify_claimed_files(files: list[str], threshold: int = 400) -> dict:
    """
    Verify if claimed files are actually violations.

    Args:
        files: List of file paths to verify
        threshold: Line count threshold

    Returns:
        Verification results
    """
    results = {"actual_violations": [], "already_fixed": [], "not_found": []}

    for file_path in files:
        path = Path(file_path)
        if not path.exists():
            results["not_found"].append(file_path)
            continue

        _, lines = scan_file(path)
        if lines > threshold:
            results["actual_violations"].append((file_path, lines))
        else:
            results["already_fixed"].append((file_path, lines))

    return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Real Violation Scanner - Intelligent Verification"
    )
    parser.add_argument("--threshold", type=int, default=400, help="Line count threshold")
    parser.add_argument("--verify", nargs="+", help="Verify specific files")
    parser.add_argument("--scan", action="store_true", help="Scan for all violations")
    parser.add_argument("--top", type=int, default=20, help="Show top N violations")

    args = parser.parse_args()

    if args.verify:
        # Verify specific files
        results = verify_claimed_files(args.verify, args.threshold)

        print("🔍 VERIFICATION RESULTS:")
        print(f"\n✅ Actual Violations ({len(results['actual_violations'])}):")
        for file, lines in results["actual_violations"]:
            print(f"  🔴 {file}: {lines} lines")

        print(f"\n✅ Already Fixed ({len(results['already_fixed'])}):")
        for file, lines in results["already_fixed"]:
            print(f"  ✅ {file}: {lines} lines (COMPLIANT)")

        if results["not_found"]:
            print(f"\n❌ Not Found ({len(results['not_found'])}):")
            for file in results["not_found"]:
                print(f"  ❌ {file}")

        # Return 0 if all verified files are violations, 1 if some already fixed
        return 0 if not results["already_fixed"] else 1

    elif args.scan:
        # Scan for all violations
        violations = find_real_violations(args.threshold)

        print(f"🔍 REAL V2 VIOLATIONS (>{args.threshold} lines):")
        print(f"\nTotal: {len(violations)} violations found\n")

        for file, lines in violations[: args.top]:
            severity = "CRITICAL" if lines > 600 else "MAJOR" if lines > 500 else "THRESHOLD"
            print(f"  {severity:>8} | {lines:4d} lines | {file}")

        if len(violations) > args.top:
            print(f"\n  ... and {len(violations) - args.top} more")

        return 0
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

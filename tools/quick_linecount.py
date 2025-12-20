#!/usr/bin/env python3
"""
Quick Line Count Tool
=====================

Quickly check line counts for one or more files without running full V2 checker.
Useful for rapid verification before/after refactoring.

Usage:
    python tools/quick_linecount.py file1.py file2.py
    python tools/quick_linecount.py thea_*.py
    python tools/quick_linecount.py --total  # Shows total only
"""

import argparse
import glob
import sys
from pathlib import Path


def count_lines(filepath: Path) -> tuple[int, bool]:
    """
    Count lines in a file.

    Args:
        filepath: Path to file

    Returns:
        Tuple of (line_count, exists)
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            lines = len(f.readlines())
        return lines, True
    except Exception:
        return 0, False


def format_result(filepath: Path, lines: int, show_status: bool = True) -> str:
    """
    Format line count result.

    Args:
        filepath: Path to file
        lines: Line count
        show_status: Whether to show V2 compliance status

    Returns:
        Formatted string
    """
    name = filepath.name

    if not show_status:
        return f"  {name}: {lines} lines"

    # V2 Compliance check
    if lines <= 200:
        status = "✅ EXCELLENT"
        color = ""
    elif lines <= 400:
        status = "✅ COMPLIANT"
        color = ""
    elif lines <= 600:
        status = "⚠️ MAJOR VIOLATION"
        color = ""
    else:
        status = "🚨 CRITICAL VIOLATION"
        color = ""

    return f"  {name}: {lines} lines {status}"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Quick line count tool for V2 verification")
    parser.add_argument("files", nargs="+", help="File paths or glob patterns (e.g., thea_*.py)")
    parser.add_argument(
        "--total", action="store_true", help="Show total only (no per-file breakdown)"
    )
    parser.add_argument(
        "--no-status", action="store_true", help="Show line counts only (no V2 status)"
    )

    args = parser.parse_args()

    # Expand glob patterns
    all_files = []
    for pattern in args.files:
        expanded = glob.glob(pattern)
        if expanded:
            all_files.extend([Path(f) for f in expanded])
        else:
            # Try as direct path
            all_files.append(Path(pattern))

    if not all_files:
        print("❌ No files found!")
        return 1

    # Count lines
    results = []
    total_lines = 0
    found_files = 0

    for filepath in all_files:
        lines, exists = count_lines(filepath)
        if exists:
            results.append((filepath, lines))
            total_lines += lines
            found_files += 1

    if not results:
        print("❌ No valid files found!")
        return 1

    # Display results
    print("\n" + "=" * 60)
    print("📊 QUICK LINE COUNT")
    print("=" * 60)

    if not args.total:
        for filepath, lines in results:
            print(format_result(filepath, lines, not args.no_status))

    print(f"\n📊 TOTAL: {total_lines} lines across {found_files} files")

    # V2 Summary
    if not args.no_status and not args.total:
        excellent = sum(1 for _, l in results if l <= 200)
        compliant = sum(1 for _, l in results if 200 < l <= 400)
        major = sum(1 for _, l in results if 400 < l <= 600)
        critical = sum(1 for _, l in results if l > 600)

        print("\n✅ V2 Status:")
        if excellent:
            print(f"  Excellent (≤200L): {excellent} files")
        if compliant:
            print(f"  Compliant (≤400L): {compliant} files")
        if major:
            print(f"  Major Violation (≤600L): {major} files")
        if critical:
            print(f"  Critical Violation (>600L): {critical} files")

    print("=" * 60 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

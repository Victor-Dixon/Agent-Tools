#!/usr/bin/env python3
"""
Memory Leak Scanner - Automated Detection
==========================================

Scans codebase for common memory leak patterns:
- Unbounded caches (dict/list without size limits)
- Missing LRU eviction
- Infinite loops without breaks
- Unclosed file handles

Author: Agent-8 (Operations & Support Specialist)
Created: 2025-10-13 (from session learnings)
"""

import re
import sys
from pathlib import Path
from typing import Any


class MemoryLeakPattern:
    """Memory leak pattern detector."""

    def __init__(self, name: str, pattern: str, severity: str, description: str):
        self.name = name
        self.pattern = re.compile(pattern)
        self.severity = severity  # CRITICAL, HIGH, MEDIUM, LOW
        self.description = description


LEAK_PATTERNS = [
    MemoryLeakPattern(
        "Unbounded Cache Dict",
        r"self\.(cache|_cache)\s*=\s*\{\}(?!.*max.*size)",
        "CRITICAL",
        "Cache without size limit - will grow unbounded",
    ),
    MemoryLeakPattern(
        "Unbounded List",
        r"self\.(history|log|queue|buffer)\s*=\s*\[\](?!.*maxlen)",
        "HIGH",
        "List without size limit - append() calls will grow unbounded",
    ),
    MemoryLeakPattern(
        "While True Without Break",
        r"while\s+True:(?![\s\S]{0,200}break)",
        "MEDIUM",
        "Infinite loop without visible break statement",
    ),
    MemoryLeakPattern(
        "Open Without With",
        r"(?<!with\s)open\([^)]+\)(?!\s*as)",
        "MEDIUM",
        "File open without context manager - handle may leak",
    ),
]


def scan_file(file_path: Path) -> list[dict[str, Any]]:
    """Scan single file for memory leaks."""
    issues = []

    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        for pattern in LEAK_PATTERNS:
            for match in pattern.pattern.finditer(content):
                # Find line number
                line_num = content[: match.start()].count("\n") + 1
                line_content = lines[line_num - 1].strip()

                issues.append(
                    {
                        "file": str(file_path),
                        "line": line_num,
                        "severity": pattern.severity,
                        "pattern": pattern.name,
                        "description": pattern.description,
                        "code": line_content,
                    }
                )

    except Exception as e:
        print(f"Error scanning {file_path}: {e}")

    return issues


def scan_directory(directory: Path, extensions: list[str] = [".py"]) -> dict[str, list]:
    """Scan directory recursively for memory leaks."""
    all_issues = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": []}

    for ext in extensions:
        for file_path in directory.rglob(f"*{ext}"):
            if "__pycache__" in str(file_path) or "node_modules" in str(file_path):
                continue

            issues = scan_file(file_path)
            for issue in issues:
                all_issues[issue["severity"]].append(issue)

    return all_issues


def print_report(issues: dict[str, list], show_low: bool = False):
    """Print formatted report."""
    print("\n" + "=" * 80)
    print("🛡️  MEMORY LEAK SCAN REPORT")
    print("=" * 80)

    total = sum(len(v) for v in issues.values())

    if total == 0:
        print("\n✅ NO MEMORY LEAKS DETECTED!")
        print("=" * 80 + "\n")
        return

    print(f"\n⚠️  FOUND {total} POTENTIAL MEMORY LEAKS\n")

    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if not show_low and severity == "LOW":
            continue

        severity_issues = issues[severity]
        if not severity_issues:
            continue

        emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
        print(f"\n{emoji[severity]} {severity}: {len(severity_issues)} issues")
        print("-" * 80)

        for issue in severity_issues:
            print(f"\n  File: {issue['file']}")
            print(f"  Line: {issue['line']}")
            print(f"  Pattern: {issue['pattern']}")
            print(f"  Issue: {issue['description']}")
            print(f"  Code: {issue['code']}")

    print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point."""
    # Scan src/ directory
    src_dir = Path(__file__).parent.parent / "src"

    if not src_dir.exists():
        print("❌ src/ directory not found!")
        sys.exit(1)

    print("🔍 Scanning for memory leaks...")
    print(f"📁 Directory: {src_dir}")

    issues = scan_directory(src_dir)
    print_report(issues, show_low=False)

    # Exit code based on critical issues
    if issues["CRITICAL"]:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

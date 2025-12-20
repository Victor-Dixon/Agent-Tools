#!/usr/bin/env python3
"""
File Refactor Detector - Quick Refactor History Checker
========================================================

⚠️ DEPRECATED: This tool has been consolidated into unified_validator.py
Use: python tools/unified_validator.py --category refactor --file <path>

Quickly checks if a file has already been refactored by examining headers and git history.
Based on Agent-1 session learning: Check before you start!

Usage:
    python tools/file_refactor_detector.py src/core/shared_utilities.py
    python tools/file_refactor_detector.py --scan src/services/
    python tools/file_refactor_detector.py --check-author "Agent-1"

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-10-13
License: MIT
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class RefactorDetector:
    """Detects refactor markers in files."""

    REFACTOR_MARKERS = [
        r"REFACTORED",
        r"V2\s+COMPLI(ANT|ANCE)",
        r"SOLID\s+(Compliant|Principle)",
        r"Modular\s+Refactoring",
        r"Split\s+into\s+\d+\s+modules",
        r"Extracted\s+from",
        r"Consolidation\s+Complete",
    ]

    AGENT_MARKERS = [
        r"Author:\s*(Agent-\d+)",
        r"REFACTORED\s+BY:\s*(Agent-\d+)",
        r"Refactored\s+by:\s*(Agent-\d+)",
        r"V2\s+Refactor:\s*(Agent-\d+)",
    ]

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.markers_found = []
        self.agents_found = []
        self.git_refactor_commits = []

    def check_file(self) -> dict[str, Any]:
        """Check file for refactor markers."""
        if not self.file_path.exists():
            return {"status": "NOT_FOUND", "path": str(self.file_path), "refactored": False}

        self._check_file_header()
        self._check_git_history()

        is_refactored = len(self.markers_found) > 0 or len(self.git_refactor_commits) > 0

        return {
            "status": "CHECKED",
            "path": str(self.file_path),
            "refactored": is_refactored,
            "markers": self.markers_found,
            "agents": self.agents_found,
            "git_commits": self.git_refactor_commits,
            "warning": self._get_warning() if is_refactored else None,
        }

    def _check_file_header(self):
        """Check file header for refactor markers."""
        try:
            with open(self.file_path, encoding="utf-8") as f:
                # Check first 100 lines (headers/docstrings)
                header_lines = [f.readline() for _ in range(100)]
                header_text = "".join(header_lines)

            # Check refactor markers
            for marker_pattern in self.REFACTOR_MARKERS:
                if re.search(marker_pattern, header_text, re.IGNORECASE):
                    self.markers_found.append(marker_pattern)

            # Check agent markers
            for agent_pattern in self.AGENT_MARKERS:
                matches = re.findall(agent_pattern, header_text, re.IGNORECASE)
                self.agents_found.extend(matches)

        except Exception:
            pass

    def _check_git_history(self):
        """Check git history for refactor commits."""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-n", "10", "--", str(self.file_path)],
                capture_output=True,
                text=True,
                cwd=self.file_path.parent,
            )

            if result.returncode == 0 and result.stdout:
                commits = result.stdout.strip().split("\n")

                refactor_keywords = ["refactor", "consolidat", "v2", "solid", "modular", "split"]
                for commit in commits:
                    if any(keyword in commit.lower() for keyword in refactor_keywords):
                        self.git_refactor_commits.append(commit)

        except Exception:
            pass

    def _get_warning(self) -> str:
        """Get warning message if file appears refactored."""
        warnings = []

        if self.markers_found:
            warnings.append(f"⚠️  REFACTOR MARKERS FOUND: {', '.join(set(self.markers_found))}")

        if self.agents_found:
            warnings.append(f"⚠️  REFACTORED BY: {', '.join(set(self.agents_found))}")

        if self.git_refactor_commits:
            warnings.append(f"⚠️  RECENT REFACTOR COMMITS: {len(self.git_refactor_commits)} found")

        warnings.append("🚨 FILE MAY ALREADY BE COMPLETE - VERIFY BEFORE STARTING!")

        return " | ".join(warnings)


def scan_directory(directory: Path, recursive: bool = True) -> list[dict[str, Any]]:
    """Scan directory for refactored files."""
    results = []

    pattern = "**/*.py" if recursive else "*.py"
    for file_path in directory.glob(pattern):
        if file_path.is_file():
            detector = RefactorDetector(file_path)
            result = detector.check_file()
            if result["refactored"]:
                results.append(result)

    return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="🔍 Detect if files have already been refactored",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check single file
  python tools/file_refactor_detector.py src/core/shared_utilities.py
  
  # Scan directory for refactored files
  python tools/file_refactor_detector.py --scan src/services/
  
  # Check by specific agent
  python tools/file_refactor_detector.py --check-author "Agent-1" src/
  
  # Find all refactored files
  python tools/file_refactor_detector.py --scan . --recursive

🔍 PREVENTS: Working on already-complete tasks!
        """,
    )

    parser.add_argument("path", nargs="?", help="File or directory to check")
    parser.add_argument("--scan", type=str, help="Scan directory for refactored files")
    parser.add_argument("--recursive", action="store_true", help="Recursive directory scan")
    parser.add_argument("--check-author", type=str, help="Filter by specific agent")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.path and not args.scan:
        parser.print_help()
        return 1

    target_path = Path(args.scan or args.path)

    if target_path.is_file():
        # Check single file
        detector = RefactorDetector(target_path)
        result = detector.check_file()

        if not args.json:
            print(f"\n{'='*70}")
            print(f"🔍 REFACTOR DETECTION: {target_path}")
            print(f"{'='*70}")
            print(f"Status: {result['status']}")
            print(f"Refactored: {'🔴 YES' if result['refactored'] else '🟢 NO'}")

            if result["refactored"]:
                if result["markers"]:
                    print("\n📋 Markers Found:")
                    for marker in set(result["markers"]):
                        print(f"  - {marker}")

                if result["agents"]:
                    print("\n👤 Refactored By:")
                    for agent in set(result["agents"]):
                        print(f"  - {agent}")

                if result["git_commits"]:
                    print("\n📜 Refactor Commits:")
                    for commit in result["git_commits"][:5]:
                        print(f"  - {commit}")

                print("\n⚠️  WARNING:")
                print(f"  {result['warning']}")

            print(f"{'='*70}\n")
        else:
            import json

            print(json.dumps(result, indent=2))

    elif target_path.is_dir():
        # Scan directory
        print(f"\n🔍 Scanning {target_path} for refactored files...\n")
        results = scan_directory(target_path, recursive=args.recursive)

        if args.check_author:
            results = [r for r in results if args.check_author in str(r.get("agents", []))]

        if not args.json:
            print(f"Found {len(results)} refactored file(s):\n")
            for result in results:
                print(f"🔴 {result['path']}")
                if result["agents"]:
                    print(f"   By: {', '.join(set(result['agents']))}")
                if result["git_commits"]:
                    print(f"   Last: {result['git_commits'][0]}")
                print()
        else:
            import json

            print(json.dumps(results, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Technical Debt Scanner
======================

Scans codebase for technical debt markers and generates actionable report.

Usage:
    python scan_technical_debt.py
    python scan_technical_debt.py --type TODO
    python scan_technical_debt.py --path src/services
"""

import argparse
import re
from collections import defaultdict
from pathlib import Path

# Technical debt markers to search for
DEBT_MARKERS = {
    "TODO": r"TODO[:\s]",
    "FIXME": r"FIXME[:\s]",
    "HACK": r"HACK[:\s]",
    "BUG": r"BUG[:\s]",
    "XXX": r"XXX[:\s]",
    "DEPRECATED": r"DEPRECATED[:\s]|@deprecated",
    "REFACTOR": r"REFACTOR[:\s]|needs? refactor",
}

# Extensions to scan
SCAN_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".md", ".yml", ".yaml"}

# Directories to skip
SKIP_DIRS = {"__pycache__", "node_modules", ".git", "venv", "env", ".pytest_cache", "dist", "build"}


class TechnicalDebtScanner:
    """Scans codebase for technical debt markers."""

    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.results = defaultdict(list)

    def scan(self, marker_type: str = None, target_path: str = None) -> dict[str, list]:
        """
        Scan for technical debt.

        Args:
            marker_type: Specific marker to scan for (e.g., 'TODO')
            target_path: Specific path to scan
        """
        search_path = Path(target_path) if target_path else self.root_path
        markers_to_scan = {marker_type: DEBT_MARKERS[marker_type]} if marker_type else DEBT_MARKERS

        print(f"🔍 Scanning: {search_path}")
        print(f"🎯 Looking for: {', '.join(markers_to_scan.keys())}")
        print()

        for file_path in self._get_files_to_scan(search_path):
            self._scan_file(file_path, markers_to_scan)

        return dict(self.results)

    def _get_files_to_scan(self, search_path: Path):
        """Get all files to scan."""
        if search_path.is_file():
            yield search_path
            return

        for file_path in search_path.rglob("*"):
            # Skip directories
            if file_path.is_dir():
                continue

            # Skip unwanted directories
            if any(skip_dir in file_path.parts for skip_dir in SKIP_DIRS):
                continue

            # Check extension
            if file_path.suffix in SCAN_EXTENSIONS:
                yield file_path

    def _scan_file(self, file_path: Path, markers: dict[str, str]):
        """Scan a single file for markers."""
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, 1):
                    for marker_name, marker_pattern in markers.items():
                        if re.search(marker_pattern, line, re.IGNORECASE):
                            self.results[marker_name].append(
                                {
                                    "file": str(file_path),
                                    "line": line_num,
                                    "content": line.strip(),
                                    "marker": marker_name,
                                }
                            )
        except Exception:
            pass  # Skip files that can't be read

    def generate_report(self, detailed: bool = True) -> str:
        """Generate technical debt report."""
        report = []
        report.append("# 🔧 Technical Debt Scan Report")
        report.append("")
        report.append(f"**Scan Path:** {self.root_path}")
        report.append(
            f"**Total Markers Found:** {sum(len(items) for items in self.results.values())}"
        )
        report.append("")

        # Summary table
        report.append("## 📊 Summary")
        report.append("")
        report.append("| Marker Type | Count | Priority |")
        report.append("|-------------|-------|----------|")

        priority_map = {
            "BUG": "P0 - Critical",
            "FIXME": "P0 - Critical",
            "XXX": "P1 - High",
            "TODO": "P1 - High",
            "HACK": "P2 - Medium",
            "DEPRECATED": "P2 - Medium",
            "REFACTOR": "P3 - Low",
        }

        for marker_type in sorted(
            self.results.keys(), key=lambda x: len(self.results[x]), reverse=True
        ):
            count = len(self.results[marker_type])
            priority = priority_map.get(marker_type, "P3 - Low")
            report.append(f"| {marker_type} | {count} | {priority} |")

        report.append("")

        # Detailed breakdown
        if detailed:
            for marker_type, items in sorted(
                self.results.items(), key=lambda x: len(x[1]), reverse=True
            ):
                if not items:
                    continue

                report.append(f"## {marker_type} ({len(items)} instances)")
                report.append("")

                # Group by file
                by_file = defaultdict(list)
                for item in items:
                    by_file[item["file"]].append(item)

                # Show up to 20 files
                for file_path in sorted(by_file.keys())[:20]:
                    file_items = by_file[file_path]
                    report.append(f"### `{file_path}` ({len(file_items)} instances)")
                    report.append("")

                    # Show first 5 items per file
                    for item in file_items[:5]:
                        report.append(f"**Line {item['line']}:**")
                        report.append("```")
                        report.append(f"{item['content']}")
                        report.append("```")
                        report.append("")

                    if len(file_items) > 5:
                        report.append(f"*... and {len(file_items) - 5} more*")
                        report.append("")

                if len(by_file) > 20:
                    report.append(f"*... and {len(by_file) - 20} more files*")
                    report.append("")

        return "\n".join(report)

    def generate_summary(self) -> str:
        """Generate quick summary."""
        total = sum(len(items) for items in self.results.values())

        summary = []
        summary.append("🔍 Technical Debt Summary")
        summary.append("=" * 40)

        for marker_type, items in sorted(
            self.results.items(), key=lambda x: len(x[1]), reverse=True
        ):
            summary.append(f"  {marker_type}: {len(items)}")

        summary.append("-" * 40)
        summary.append(f"  TOTAL: {total}")

        return "\n".join(summary)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Scan for technical debt markers")
    parser.add_argument(
        "--type", choices=list(DEBT_MARKERS.keys()), help="Specific marker type to scan for"
    )
    parser.add_argument("--path", default=".", help="Path to scan (default: current directory)")
    parser.add_argument("--output", default="TECHNICAL_DEBT_REPORT.md", help="Output file")
    parser.add_argument("--summary-only", action="store_true", help="Show summary only")

    args = parser.parse_args()

    # Scan
    scanner = TechnicalDebtScanner(args.path)
    results = scanner.scan(marker_type=args.type, target_path=args.path)

    # Print summary
    print(scanner.generate_summary())
    print()

    if not args.summary_only:
        # Generate and save detailed report
        report = scanner.generate_report(detailed=True)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"📄 Detailed report saved to: {args.output}")
        print()
        print("💡 Next steps:")
        print("   1. Review the report")
        print("   2. Prioritize BUG/FIXME markers")
        print("   3. Address TODO items")
        print("   4. Update or remove outdated markers")


if __name__ == "__main__":
    main()

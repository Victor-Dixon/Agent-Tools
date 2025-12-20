#!/usr/bin/env python3
"""
SSOT Tag Report & Validator
===========================

Purpose:
- Help Agent-8 (SSOT / QA) and Agent-3 (Infrastructure & DevOps) **consume SSOT tags**
  that are embedded in code via comments like:

      <!-- SSOT Domain: infrastructure -->

Capabilities:
- Scan the repo for `SSOT Domain` tags
- Produce **text / markdown / JSON** summaries for dashboards and reports
- (Optional) Act as a **soft CI check** to highlight untagged files in selected directories

Usage examples:
    # Simple text summary for all tagged files
    python tools/ssot_tag_report.py

    # Markdown report (for dashboards or docs)
    python tools/ssot_tag_report.py --format markdown > docs/SSOT_TAG_REPORT.md

    # JSON for Agent-8 / dashboards
    python tools/ssot_tag_report.py --format json > runtime/ssot_tag_report.json

    # Focus on core infrastructure files only
    python tools/ssot_tag_report.py --dirs src/core --format text

    # Soft CI-style check: list untagged files under src/core but do NOT fail
    python tools/ssot_tag_report.py --dirs src/core --report-untagged

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-12-14

<!-- SSOT Domain: infrastructure -->
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


SSOT_TAG_MARKER = "SSOT Domain:"


@dataclass
class FileTagInfo:
    """Tag information for a single file."""

    path: str
    domain: Optional[str]


@dataclass
class SSOTReport:
    """Aggregated SSOT tag report."""

    root: str
    total_files_scanned: int
    total_tagged_files: int
    total_untagged_files: int
    domains: Dict[str, List[str]]
    untagged_files: List[str]


def find_project_root(start: Optional[Path] = None) -> Path:
    """Best-effort project root detection (directory containing `tools/`)."""
    if start is None:
        start = Path(__file__).resolve()

    current = start
    for _ in range(5):
        if (current / "tools").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    # Fallback: parent of this file
    return Path(__file__).resolve().parent.parent


def extract_ssot_domain(content: str) -> Optional[str]:
    """Extract SSOT domain from file content, if present."""
    if SSOT_TAG_MARKER not in content:
        return None

    # Simple pattern: <!-- SSOT Domain: something -->
    marker_index = content.find(SSOT_TAG_MARKER)
    if marker_index == -1:
        return None

    # Take line containing the marker
    line_start = content.rfind("\n", 0, marker_index)
    line_end = content.find("\n", marker_index)
    if line_start == -1:
        line_start = 0
    else:
        line_start += 1
    if line_end == -1:
        line_end = len(content)

    line = content[line_start:line_end].strip()
    # Expect something like: <!-- SSOT Domain: infrastructure -->
    if SSOT_TAG_MARKER in line:
        after = line.split(SSOT_TAG_MARKER, 1)[1].strip()
        # Drop trailing comment terminator if present
        if after.endswith("-->"):
            after = after[:-3].strip()
        # Remove leading ":" if formatting is odd
        if after.startswith(":"):
            after = after[1:].strip()
        return after or None

    return None


def iter_target_files(root: Path, dirs: Optional[List[str]], extensions: Tuple[str, ...]) -> Iterable[Path]:
    """Yield files under root, optionally limited to specific directories and extensions."""
    if dirs:
        for rel_dir in dirs:
            base = (root / rel_dir).resolve()
            if not base.exists():
                continue
            for path in base.rglob("*"):
                if path.is_file() and path.suffix in extensions:
                    yield path
    else:
        # Full-tree scan under src/ by default
        src_root = root / "src"
        search_base = src_root if src_root.exists() else root
        for path in search_base.rglob("*"):
            if path.is_file() and path.suffix in extensions:
                yield path


def build_report(root: Path, dirs: Optional[List[str]], extensions: Tuple[str, ...]) -> SSOTReport:
    """Scan for SSOT tags and build an aggregated report."""
    domains: Dict[str, List[str]] = {}
    untagged: List[str] = []

    total_files = 0
    total_tagged = 0

    for file_path in iter_target_files(root, dirs, extensions):
        total_files += 1

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            # Skip unreadable files but keep moving
            continue

        domain = extract_ssot_domain(content)
        rel_path = str(file_path.relative_to(root))

        if domain:
            total_tagged += 1
            domains.setdefault(domain, []).append(rel_path)
        else:
            untagged.append(rel_path)

    return SSOTReport(
        root=str(root),
        total_files_scanned=total_files,
        total_tagged_files=total_tagged,
        total_untagged_files=len(untagged),
        domains={k: sorted(v) for k, v in sorted(domains.items())},
        untagged_files=sorted(untagged),
    )


def format_report_text(report: SSOTReport, include_untagged: bool) -> str:
    """Human-friendly text summary."""
    lines: List[str] = []
    lines.append("SSOT Tag Report")
    lines.append("=" * 60)
    lines.append(f"Root: {report.root}")
    lines.append(f"Total files scanned:   {report.total_files_scanned}")
    lines.append(f"Total tagged files:    {report.total_tagged_files}")
    lines.append(f"Total untagged files:  {report.total_untagged_files}")
    lines.append("")

    lines.append("By Domain:")
    if not report.domains:
        lines.append("  (no SSOT tags found)")
    else:
        for domain, files in report.domains.items():
            lines.append(f"  - {domain}: {len(files)} files")

    if include_untagged and report.untagged_files:
        lines.append("")
        lines.append("Untagged files:")
        for path in report.untagged_files:
            lines.append(f"  - {path}")

    return "\n".join(lines)


def format_report_markdown(report: SSOTReport, include_untagged: bool) -> str:
    """Markdown summary suitable for dashboards / docs."""
    lines: List[str] = []
    lines.append("# SSOT Tag Report")
    lines.append("")
    lines.append(f"- **Root**: `{report.root}`")
    lines.append(
        f"- **Total files scanned**: **{report.total_files_scanned}**")
    lines.append(f"- **Tagged files**: **{report.total_tagged_files}**")
    lines.append(f"- **Untagged files**: **{report.total_untagged_files}**")
    lines.append("")

    lines.append("## Domains")
    if not report.domains:
        lines.append("- **None** (no SSOT tags found)")
    else:
        for domain, files in report.domains.items():
            lines.append(f"- **{domain}**: {len(files)} files")

    if include_untagged and report.untagged_files:
        lines.append("")
        lines.append("## Untagged Files")
        for path in report.untagged_files:
            lines.append(f"- `{path}`")

    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SSOT Tag Report & Validator - consume <!-- SSOT Domain: ... --> tags."
    )
    parser.add_argument(
        "--root",
        help="Project root (defaults to auto-detected root containing tools/).",
    )
    parser.add_argument(
        "--dirs",
        nargs="+",
        help="Relative directories to scan (e.g. src/core src/services). "
        "If omitted, scans src/ (or the whole tree if src/ is missing).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "markdown", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--report-untagged",
        action="store_true",
        help="Include a list of untagged files in the output (for dashboards or manual review).",
    )
    # IMPORTANT: This is intentionally a soft signal for now (no default failure),
    # so we don't break CI while SSOT coverage is still being expanded.
    parser.add_argument(
        "--fail-if-untagged",
        action="store_true",
        help="Exit with status 1 if any untagged files are found in the scanned directories.",
    )

    args = parser.parse_args(argv)

    root = Path(args.root).resolve() if args.root else find_project_root()
    report = build_report(root, args.dirs, extensions=(".py",))

    if args.format == "text":
        output = format_report_text(
            report, include_untagged=args.report_untagged)
    elif args.format == "markdown":
        output = format_report_markdown(
            report, include_untagged=args.report_untagged)
    else:
        output = json.dumps(asdict(report), indent=2, sort_keys=True)

    print(output)

    if args.fail_if_untagged and report.total_untagged_files > 0:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Timeout Sweep Report
====================

Reports hardcoded timeout usages that are not using TimeoutConstants.
Intended to accelerate Phase 5 timeout SSOT cleanup.

Usage:
  python tools/timeout_sweep_report.py --paths src tools
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence


TIMEOUT_VALUES = {5, 10, 30, 60, 120, 300}
DEFAULT_PATHS = ("src", "tools")
DEFAULT_EXCLUDES = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "env",
    "venv",
    ".mypy_cache",
}
IGNORED_SUFFIXES = {
    ".md",
    ".json",
    ".lock",
    ".log",
    ".txt",
    ".yml",
    ".yaml",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".zip",
}

TIMEOUT_PATTERN = re.compile(r"timeout\\s*[:=]\\s*(\\d+(?:\\.\\d+)?)")


@dataclass
class Finding:
    path: Path
    line_no: int
    line: str
    value: str


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & DEFAULT_EXCLUDES:
        return True
    if path.suffix.lower() in IGNORED_SUFFIXES:
        return True
    return False


def scan_file(path: Path) -> List[Finding]:
    findings: List[Finding] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return findings

    if "TimeoutConstants" in text:
        return findings

    for idx, line in enumerate(text.splitlines(), start=1):
        match = TIMEOUT_PATTERN.search(line)
        if not match:
            continue
        value_str = match.group(1)
        try:
            value_num = float(value_str)
        except ValueError:
            continue
        if value_num in TIMEOUT_VALUES:
            findings.append(Finding(path=path, line_no=idx, line=line.strip(), value=value_str))
    return findings


def iter_files(paths: Sequence[str]) -> Iterable[Path]:
    for base in paths:
        root = Path(base)
        if not root.exists():
            continue
        if root.is_file():
            if not should_skip(root):
                yield root
            continue
        for file_path in root.rglob("*"):
            if file_path.is_file() and not should_skip(file_path):
                yield file_path


def print_report(findings: List[Finding]) -> int:
    if not findings:
        print("✅ No hardcoded timeouts found that match the common set.")
        return 0

    print(f"⚠️  Found {len(findings)} hardcoded timeouts (common set: {sorted(TIMEOUT_VALUES)}):")
    for f in findings:
        print(f"- {f.path}:{f.line_no} -> {f.line}")
    return 1


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report hardcoded timeout usages to replace with TimeoutConstants."
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        default=list(DEFAULT_PATHS),
        help="Paths to scan (default: src tools)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    findings: List[Finding] = []
    for file_path in iter_files(args.paths):
        findings.extend(scan_file(file_path))
    return print_report(findings)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


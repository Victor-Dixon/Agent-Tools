"""
Lightweight pytest runner + reporter (V2 compliant, <400 LOC).

Usage examples:
  python tools/pytest_quick_report.py tests/unit/gui tests/unit/infrastructure/browser/unified
  python tools/pytest_quick_report.py tests/unit/gui --output-json runtime/reports/pytest_quick_report.json
  python tools/pytest_quick_report.py tests/unit/gui --output-md devlogs/pytest_run.md -- --maxfail=1
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


SUMMARY_REGEXES = [
    re.compile(r"(?P<passed>\d+)\s+passed"),
    re.compile(r"(?P<failed>\d+)\s+failed"),
    re.compile(r"(?P<skipped>\d+)\s+skipped"),
    re.compile(r"(?P<xfail>\d+)\s+xfail"),
    re.compile(r"(?P<xpassed>\d+)\s+xpass"),
    re.compile(r"(?P<errors>\d+)\s+error"),
]


def parse_summary(output: str) -> Dict[str, int]:
    counts = {"passed": 0, "failed": 0, "skipped": 0, "xfail": 0, "xpassed": 0, "errors": 0}
    for line in output.splitlines():
        for regex in SUMMARY_REGEXES:
            match = regex.search(line)
            if match:
                for key, value in match.groupdict().items():
                    counts[key] = counts.get(key, 0) + int(value or 0)
    return counts


def build_report(
    command: List[str],
    returncode: int,
    stdout: str,
    stderr: str,
    started_at: datetime,
) -> Dict[str, object]:
    counts = parse_summary(stdout + "\n" + stderr)
    status = "pass" if returncode == 0 and counts.get("failed", 0) == 0 and counts.get("errors", 0) == 0 else "fail"
    return {
        "ts": started_at.isoformat(),
        "status": status,
        "returncode": returncode,
        "command": command,
        "counts": counts,
        "stdout": stdout,
        "stderr": stderr,
    }


def write_json(report: Dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


def write_markdown(report: Dict[str, object], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Pytest Quick Report",
        f"- Timestamp: {report['ts']}",
        f"- Status: {report['status']}",
        f"- Return code: {report['returncode']}",
        f"- Command: {' '.join(report['command'])}",
        "",
        "## Counts",
        *(f"- {k}: {v}" for k, v in report["counts"].items()),
        "",
        "## Stdout",
        "```",
        report["stdout"],
        "```",
        "",
        "## Stderr",
        "```",
        report["stderr"],
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def run_pytest(paths: List[str], extra_args: List[str]) -> Dict[str, object]:
    started_at = datetime.now(timezone.utc)
    command = [sys.executable, "-m", "pytest", *paths, *extra_args]
    result = subprocess.run(command, capture_output=True, text=True)
    return build_report(command, result.returncode, result.stdout, result.stderr, started_at)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run pytest for specified paths and emit a concise report.")
    parser.add_argument("paths", nargs="+", help="Pytest target paths (files or directories).")
    parser.add_argument("--output-json", help="Path to write JSON report.")
    parser.add_argument("--output-md", help="Path to write Markdown report.")
    parser.add_argument("--strict-exit", action="store_true", help="Exit non-zero if any failures/errors are present.")
    parser.add_argument(
        "--",
        dest="pytest_args",
        nargs=argparse.REMAINDER,
        help="Args passed through to pytest (after --).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    extra_args: List[str] = args.pytest_args or []
    report = run_pytest(args.paths, extra_args)

    if args.output_json:
        write_json(report, Path(args.output_json))
    if args.output_md:
        write_markdown(report, Path(args.output_md))

    # Print a terse one-liner for quick CLI use
    counts = report["counts"]
    print(
        f"[{report['status']}] passed={counts.get('passed',0)} "
        f"failed={counts.get('failed',0)} errors={counts.get('errors',0)} "
        f"skipped={counts.get('skipped',0)} xfail={counts.get('xfail',0)} "
        f"xpassed={counts.get('xpassed',0)}"
    )

    if args.strict_exit and report["status"] != "pass":
        return 1
    return report["returncode"]


if __name__ == "__main__":
    sys.exit(main())


#!/usr/bin/env python3
"""
Compute coverage on changed files only; gate PRs on per-file threshold.
Usage:
  python tools/coverage/changed_file_report.py --base HEAD~1 --min 95 --strict
"""

import argparse
import pathlib
import subprocess
import sys
import xml.etree.ElementTree as ET


def changed_files(base: str) -> list[str]:
    """Get list of changed Python files in src/ directory."""
    cmd = ["git", "diff", "--name-only", base, "--", "src"]
    try:
        out = subprocess.check_output(cmd, text=True).strip().splitlines()
        return [p for p in out if p.endswith(".py")]
    except subprocess.CalledProcessError as e:
        print(f"Error getting changed files: {e}")
        return []


def load_cov(xml_path: str = "coverage.xml") -> dict[str, float]:
    """Load coverage data from XML file."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        byfile = {}

        for cls in root.iter("class"):
            fname = cls.attrib["filename"]
            lines_total = lines_covered = 0

            for ln in cls.iter("line"):
                lines_total += 1
                if int(ln.attrib.get("hits", "0")) > 0:
                    lines_covered += 1

            if lines_total > 0:
                byfile[fname] = 100.0 * lines_covered / lines_total
            else:
                byfile[fname] = 0.0

        return byfile
    except (ET.ParseError, FileNotFoundError) as e:
        print(f"Error loading coverage XML: {e}")
        return {}


def main() -> int:
    """Main function to check coverage on changed files."""
    ap = argparse.ArgumentParser(description="Check coverage on changed files")
    ap.add_argument("--base", default="origin/main", help="Base branch for comparison")
    ap.add_argument("--min", type=int, default=95, help="Minimum coverage percentage")
    ap.add_argument("--strict", action="store_true", help="Fail if any file below threshold")
    args = ap.parse_args()

    # Get changed files
    changed = changed_files(args.base)
    if not changed:
        print("No changed files in src/")
        return 0

    # Load coverage data
    cov = load_cov()
    if not cov:
        print("No coverage data found. Run 'coverage run -m pytest' first.")
        return 1

    # Check each changed file
    fails: list[tuple[str, float]] = []
    print(f"Checking coverage on {len(changed)} changed files (min {args.min}%):")

    for f in changed:
        # Try exact match first, then normalized path
        key = f if f in cov else str(pathlib.Path(f))
        pct = cov.get(key, 0.0)

        status = "✅" if pct >= args.min else "❌"
        print(f"{status} {f}: {pct:.1f}% (min {args.min}%)")

        if pct < args.min:
            fails.append((f, pct))

    # Report results
    if fails:
        print(f"\n⚠️  {len(fails)} files below threshold:")
        for f, p in fails:
            print(f"   - {f}: {p:.1f}%")

        if args.strict:
            print("\n❌ FAIL: Coverage below threshold")
            return 2
        else:
            print("\n⚠️  WARNING: Coverage below threshold (use --strict to fail)")
            return 1
    else:
        print(f"\n✅ All {len(changed)} changed files meet coverage threshold")
        return 0


if __name__ == "__main__":
    sys.exit(main())

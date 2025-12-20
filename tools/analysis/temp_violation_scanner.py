#!/usr/bin/env python3
"""Quick V2 violation scanner - Agent-5"""

import os
from pathlib import Path


def scan_violations(directory, threshold=400):
    violations = []
    for root, dirs, files in os.walk(directory):
        # Skip common directories
        if any(skip in root for skip in ["__pycache__", ".git", "venv", "node_modules"]):
            continue
        for file in files:
            if file.endswith(".py"):
                filepath = Path(root) / file
                try:
                    with open(filepath, encoding="utf-8") as f:
                        lines = len(f.readlines())
                    if lines > threshold:
                        rel_path = str(filepath.relative_to(Path.cwd()))
                        violations.append((rel_path, lines))
                except Exception:
                    pass
    return sorted(violations, key=lambda x: x[1], reverse=True)


# Scan src and tools
print("=== V2 VIOLATIONS SCAN ===\n")
src_violations = scan_violations("src", 400)
tools_violations = scan_violations("tools", 400)

all_violations = src_violations + tools_violations
all_violations.sort(key=lambda x: x[1], reverse=True)

if all_violations:
    print(f"Found {len(all_violations)} V2 violations (>400 lines):\n")
    for i, (filepath, lines) in enumerate(all_violations[:25], 1):
        severity = "CRITICAL" if lines > 600 else "MAJOR" if lines > 500 else "VIOLATION"
        print(f"{i:2}. {filepath}: {lines}L [{severity}]")

    if len(all_violations) > 25:
        print(f"\n... and {len(all_violations) - 25} more violations")

    print(f"\n📊 Total: {len(all_violations)} violations")
    print(f"🔥 Critical (>600L): {len([v for v in all_violations if v[1] > 600])}")
    print(f"⚠️  Major (500-600L): {len([v for v in all_violations if 500 < v[1] <= 600])}")
    print(f"📋 Standard (400-500L): {len([v for v in all_violations if 400 < v[1] <= 500])}")
else:
    print("✅ No V2 violations found! All files <400 lines!")

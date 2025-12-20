#!/usr/bin/env python3
"""Onboarding Test Runner

Quick helper to run onboarding-related tests with a focused, infra-friendly
summary. Intended for use during refactors of hard/soft onboarding services.

Usage:
    python tools/onboarding_test_runner.py

This script:
- Runs `tests/unit/services/test_onboarding_services.py`
- Prints a short pass/fail summary
- Exits non-zero if tests fail (for easy wiring into other tools/CI)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_onboarding_tests() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    test_file = repo_root / "tests" / "unit" / \
        "services" / "test_onboarding_services.py"

    if not test_file.exists():
        print("❌ Onboarding tests not found:", test_file)
        return 1

    print("🧪 Running onboarding unit tests (lock semantics + GUI/messaging fallbacks)...")
    cmd = [sys.executable, "-m", "pytest", str(test_file), "-q"]

    try:
        result = subprocess.run(cmd, cwd=repo_root, text=True)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"❌ Failed to run pytest: {exc}")
        return 1

    if result.returncode == 0:
        print("✅ Onboarding tests passed (behavioural contract intact).")
    else:
        print("❌ Onboarding tests failed – investigate before refactoring further.")

    return result.returncode


def main() -> int:
    return run_onboarding_tests()


if __name__ == "__main__":
    raise SystemExit(main())

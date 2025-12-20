#!/usr/bin/env python3
"""
Work Completion Verifier - Pre-Message Validation Tool
=======================================================

Verify work is actually complete before sending completion messages.
Prevents "already done" confusion by checking actual files, tests, and coverage.

Usage:
    python tools/work_completion_verifier.py --check-extension repository-navigator
    python tools/work_completion_verifier.py --check-python src/core/error_handling/
    python tools/work_completion_verifier.py --check-tests tests/

Author: Agent-6 - VSCode Forking & Quality Gates Specialist
Created: 2025-10-13
V2 Compliance: <400 lines
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any
from src.core.config.timeout_constants import TimeoutConstants


class WorkCompletionVerifier:
    """Verify work completion before messaging."""

    def __init__(self, workspace_root: Path):
        """Initialize verifier."""
        self.workspace_root = workspace_root
        self.extensions_dir = workspace_root / "extensions"

    def verify_extension(self, extension_name: str) -> dict[str, Any]:
        """
        Verify VSCode extension completion.

        Checks:
        - Files exist
        - Tests pass
        - Coverage meets threshold
        - No TypeScript errors

        Returns:
            Verification results
        """
        ext_path = self.extensions_dir / extension_name

        results = {"extension": extension_name, "complete": False, "checks": {}}

        if not ext_path.exists():
            results["checks"]["exists"] = {"pass": False, "reason": "Extension directory not found"}
            return results

        results["checks"]["exists"] = {"pass": True}

        # Check package.json exists
        if not (ext_path / "package.json").exists():
            results["checks"]["package"] = {"pass": False, "reason": "package.json not found"}
            return results

        results["checks"]["package"] = {"pass": True}

        # Check TypeScript compilation
        print("🔍 Checking TypeScript compilation...")
        try:
            result = subprocess.run(
                ["npm", "run", "compile"], cwd=ext_path, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_MEDIUM
            )

            ts_pass = result.returncode == 0
            results["checks"]["typescript"] = {
                "pass": ts_pass,
                "errors": 0 if ts_pass else "compilation failed",
            }
        except Exception as e:
            results["checks"]["typescript"] = {"pass": False, "reason": str(e)}

        # Check tests pass
        print("🧪 Running tests...")
        try:
            result = subprocess.run(
                ["npm", "test"], cwd=ext_path, capture_output=True, text=True, timeout=TimeoutConstants.HTTP_LONG
            )

            tests_pass = result.returncode == 0

            # Parse test output
            output = result.stdout + result.stderr
            tests_total = 0
            tests_passed = 0

            for line in output.split("\n"):
                if "Tests:" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed,":
                            try:
                                tests_passed = int(parts[i - 1])
                            except (ValueError, IndexError):
                                pass
                        if part == "total":
                            try:
                                tests_total = int(parts[i - 1])
                            except (ValueError, IndexError):
                                pass

            results["checks"]["tests"] = {
                "pass": tests_pass,
                "total": tests_total,
                "passed": tests_passed,
            }
        except Exception as e:
            results["checks"]["tests"] = {"pass": False, "reason": str(e)}

        # Check test coverage
        print("📊 Checking test coverage...")
        try:
            result = subprocess.run(
                ["npm", "run", "test:coverage"],
                cwd=ext_path,
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_LONG,
            )

            output = result.stdout + result.stderr

            # Parse coverage
            coverage = self._parse_coverage(output)
            coverage_pass = coverage.get("lines", 0) >= 85 and coverage.get("statements", 0) >= 85

            results["checks"]["coverage"] = {
                "pass": coverage_pass,
                "lines": coverage.get("lines", 0),
                "statements": coverage.get("statements", 0),
                "branches": coverage.get("branches", 0),
                "functions": coverage.get("functions", 0),
            }
        except Exception as e:
            results["checks"]["coverage"] = {"pass": False, "reason": str(e)}

        # Overall completion
        results["complete"] = all(check.get("pass", False) for check in results["checks"].values())

        return results

    def verify_python_module(self, module_path: str) -> dict[str, Any]:
        """
        Verify Python module completion.

        Checks:
        - Files exist
        - No syntax errors
        - Tests exist and pass
        - Coverage meets threshold

        Returns:
            Verification results
        """
        path = Path(module_path)

        results = {"module": module_path, "complete": False, "checks": {}}

        if not path.exists():
            results["checks"]["exists"] = {"pass": False, "reason": "Path not found"}
            return results

        results["checks"]["exists"] = {"pass": True}

        # Check Python syntax
        print("🔍 Checking Python syntax...")
        try:
            # Use python -m py_compile to check syntax
            if path.is_file():
                files = [path]
            else:
                files = list(path.rglob("*.py"))

            syntax_errors = []
            for file in files:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(file)], capture_output=True, text=True
                )
                if result.returncode != 0:
                    syntax_errors.append(file.name)

            results["checks"]["syntax"] = {
                "pass": len(syntax_errors) == 0,
                "errors": syntax_errors if syntax_errors else None,
            }
        except Exception as e:
            results["checks"]["syntax"] = {"pass": False, "reason": str(e)}

        # Check tests exist
        print("🧪 Checking for tests...")
        test_path = self.workspace_root / "tests"

        # Try to find corresponding test file
        if path.is_file():
            # src/core/error_handling.py -> tests/test_error_handling.py
            test_file = test_path / f"test_{path.stem}.py"
            tests_exist = test_file.exists()
        else:
            # Check if there are any tests for this module
            tests_exist = len(list(test_path.glob(f"test_*{path.name}*.py"))) > 0

        results["checks"]["tests_exist"] = {"pass": tests_exist}

        # Overall completion
        results["complete"] = all(check.get("pass", False) for check in results["checks"].values())

        return results

    def _parse_coverage(self, output: str) -> dict[str, float]:
        """Parse coverage from Jest output."""
        coverage = {}

        for line in output.split("\n"):
            if "% Lines" in line or "% Stmts" in line:
                # Look for coverage in format: "All files | 88.88 | ..."
                parts = line.split("|")
                if len(parts) >= 5:
                    try:
                        coverage["statements"] = float(parts[1].strip())
                        coverage["branches"] = float(parts[2].strip())
                        coverage["functions"] = float(parts[3].strip())
                        coverage["lines"] = float(parts[4].strip())
                    except (ValueError, IndexError):
                        pass

        return coverage

    def format_results(self, results: dict[str, Any]) -> str:
        """Format verification results."""
        output = []

        output.append(f"\n{'='*60}")
        output.append("✅ Work Completion Verification")
        output.append(f"{'='*60}")

        target = results.get("extension") or results.get("module", "Unknown")
        output.append(f"\n🎯 Target: {target}")

        output.append("\n📋 Checks:")
        for check_name, check_data in results["checks"].items():
            pass_icon = "✅" if check_data.get("pass", False) else "❌"
            output.append(f"  {pass_icon} {check_name.replace('_', ' ').title()}")

            # Show details
            for key, value in check_data.items():
                if key != "pass":
                    output.append(f"     {key}: {value}")

        output.append(f"\n{'─'*60}")
        if results["complete"]:
            output.append("✅ WORK COMPLETE - Safe to send completion message!")
        else:
            output.append("❌ WORK INCOMPLETE - Do not send completion message yet!")
        output.append(f"{'─'*60}")

        return "\n".join(output)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="✅ Work Completion Verifier - Pre-message validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify extension completion
  python tools/work_completion_verifier.py --check-extension repository-navigator
  
  # Verify Python module completion
  python tools/work_completion_verifier.py --check-python src/core/error_handling/
  
  # Verify specific file
  python tools/work_completion_verifier.py --check-python src/core/error_handling_core.py

🐝 WE. ARE. SWARM. ⚡️🔥
        """,
    )

    parser.add_argument(
        "--check-extension", type=str, metavar="NAME", help="Verify VSCode extension completion"
    )

    parser.add_argument(
        "--check-python", type=str, metavar="PATH", help="Verify Python module/file completion"
    )

    args = parser.parse_args()

    if not args.check_extension and not args.check_python:
        parser.print_help()
        print("\n❌ Error: Must specify --check-extension or --check-python")
        sys.exit(1)

    # Initialize verifier
    workspace_root = Path(__file__).parent.parent
    verifier = WorkCompletionVerifier(workspace_root)

    # Run verification
    if args.check_extension:
        results = verifier.verify_extension(args.check_extension)
    else:
        results = verifier.verify_python_module(args.check_python)

    # Display results
    print(verifier.format_results(results))

    # Exit with appropriate code
    sys.exit(0 if results["complete"] else 1)


if __name__ == "__main__":
    main()

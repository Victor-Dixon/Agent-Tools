#!/usr/bin/env python3
"""
Extension Test Runner - VSCode Extension Testing Tool
======================================================

Run tests for VSCode extensions with coverage reporting.
Specialized tool for testing TypeScript/JavaScript extensions.

Usage:
    python tools/extension_test_runner.py --extension repository-navigator
    python tools/extension_test_runner.py --extension repository-navigator --coverage
    python tools/extension_test_runner.py --extension repository-navigator --unit
    python tools/extension_test_runner.py --extension repository-navigator --integration

Author: Agent-6 - VSCode Forking & Quality Gates Specialist
Created: 2025-10-13
V2 Compliance: <400 lines
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any


class ExtensionTestRunner:
    """Run tests for VSCode extensions."""

    def __init__(self, workspace_root: Path):
        """Initialize test runner."""
        self.workspace_root = workspace_root
        self.extensions_dir = workspace_root / "extensions"

    def get_extension_path(self, extension_name: str) -> Path | None:
        """Get path to extension directory."""
        ext_path = self.extensions_dir / extension_name

        if not ext_path.exists():
            return None

        # Verify it has package.json
        if not (ext_path / "package.json").exists():
            return None

        return ext_path

    def run_tests(
        self, extension_name: str, test_type: str = "all", coverage: bool = False
    ) -> dict[str, Any]:
        """
        Run tests for extension.

        Args:
            extension_name: Name of extension
            test_type: Type of tests ('all', 'unit', 'integration', 'e2e')
            coverage: Whether to generate coverage report

        Returns:
            Test results dictionary
        """
        ext_path = self.get_extension_path(extension_name)
        if not ext_path:
            return {"success": False, "error": f"Extension not found: {extension_name}"}

        print(f"\n{'='*60}")
        print(f"🧪 Running {test_type} tests for {extension_name}")
        print(f"{'='*60}\n")

        # Build npm command
        if test_type == "all":
            cmd = ["npm", "test"]
        elif test_type == "unit":
            cmd = ["npm", "run", "test:unit"]
        elif test_type == "integration":
            cmd = ["npm", "run", "test:integration"]
        elif test_type == "e2e":
            cmd = ["npm", "run", "test:e2e"]
        else:
            return {"success": False, "error": f"Unknown test type: {test_type}"}

        # Add coverage if requested
        if coverage and test_type in ["all", "unit"]:
            cmd = ["npm", "run", "test:coverage"]

        # Run tests
        try:
            result = subprocess.run(cmd, cwd=ext_path, capture_output=True, text=True)

            output = result.stdout + result.stderr

            # Parse results
            results = self._parse_test_output(output, coverage)
            results["success"] = result.returncode == 0
            results["extension"] = extension_name
            results["test_type"] = test_type

            return results

        except Exception as e:
            return {"success": False, "error": str(e), "extension": extension_name}

    def _parse_test_output(self, output: str, coverage: bool) -> dict[str, Any]:
        """Parse test output for results."""
        results = {
            "output": output,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_total": 0,
            "suites_passed": 0,
            "suites_total": 0,
        }

        # Parse Jest output
        for line in output.split("\n"):
            # Test suites
            if "Test Suites:" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed,":
                        try:
                            results["suites_passed"] = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass
                    if part == "total":
                        try:
                            results["suites_total"] = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass

            # Tests
            if "Tests:" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed,":
                        try:
                            results["tests_passed"] = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass
                    if part == "total":
                        try:
                            results["tests_total"] = int(parts[i - 1])
                        except (ValueError, IndexError):
                            pass

            # Coverage
            if coverage and "% Lines" in line:
                # Next line usually has coverage
                pass

        results["tests_failed"] = results["tests_total"] - results["tests_passed"]

        return results

    def format_results(self, results: dict[str, Any]) -> str:
        """Format test results for display."""
        output = []

        output.append(f"\n{'='*60}")
        output.append(f"📊 Test Results: {results.get('extension', 'Unknown')}")
        output.append(f"{'='*60}")

        if not results.get("success", False):
            output.append("\n❌ TESTS FAILED")
            if "error" in results:
                output.append(f"   Error: {results['error']}")
        else:
            output.append("\n✅ ALL TESTS PASSED")

        output.append("\n📈 Statistics:")
        output.append(
            f"   Test Suites: {results.get('suites_passed', 0)}/{results.get('suites_total', 0)} passed"
        )
        output.append(
            f"   Tests:       {results.get('tests_passed', 0)}/{results.get('tests_total', 0)} passed"
        )

        if results.get("tests_failed", 0) > 0:
            output.append(f"   Failed:      {results['tests_failed']}")

        return "\n".join(output)

    def list_extensions(self) -> list[str]:
        """List available extensions."""
        if not self.extensions_dir.exists():
            return []

        extensions = []
        for ext_dir in self.extensions_dir.iterdir():
            if ext_dir.is_dir() and (ext_dir / "package.json").exists():
                extensions.append(ext_dir.name)

        return sorted(extensions)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="🧪 Extension Test Runner - VSCode extension testing tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python tools/extension_test_runner.py --extension repository-navigator
  
  # Run unit tests with coverage
  python tools/extension_test_runner.py --extension repository-navigator --unit --coverage
  
  # Run integration tests
  python tools/extension_test_runner.py --extension repository-navigator --integration
  
  # List available extensions
  python tools/extension_test_runner.py --list

🐝 WE. ARE. SWARM. ⚡️🔥
        """,
    )

    parser.add_argument("--extension", type=str, help="Extension name (e.g., repository-navigator)")

    parser.add_argument("--unit", action="store_true", help="Run unit tests only")

    parser.add_argument("--integration", action="store_true", help="Run integration tests only")

    parser.add_argument("--e2e", action="store_true", help="Run E2E tests only")

    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")

    parser.add_argument("--list", action="store_true", help="List available extensions")

    args = parser.parse_args()

    # Initialize runner
    workspace_root = Path(__file__).parent.parent
    runner = ExtensionTestRunner(workspace_root)

    # List extensions
    if args.list:
        extensions = runner.list_extensions()
        print(f"\n{'='*60}")
        print("📦 Available Extensions")
        print(f"{'='*60}\n")

        if extensions:
            for ext in extensions:
                print(f"  • {ext}")
        else:
            print("  No extensions found!")

        print()
        return

    # Validate arguments
    if not args.extension:
        parser.print_help()
        print("\n❌ Error: Must specify --extension or --list")
        sys.exit(1)

    # Determine test type
    test_type = "all"
    if args.unit:
        test_type = "unit"
    elif args.integration:
        test_type = "integration"
    elif args.e2e:
        test_type = "e2e"

    # Run tests
    results = runner.run_tests(args.extension, test_type, args.coverage)

    # Display results
    print(runner.format_results(results))

    # Exit with appropriate code
    sys.exit(0 if results.get("success", False) else 1)


if __name__ == "__main__":
    main()

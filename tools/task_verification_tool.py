#!/usr/bin/env python3
"""
Task Verification Tool - Pre-Execution Validator
=================================================

Verifies task current state before starting work to prevent wasted effort.
Based on Agent-1's session learning: Always verify before executing!

Usage:
    python tools/task_verification_tool.py src/core/shared_utilities.py
    python tools/task_verification_tool.py --file src/gaming/gaming_integration_core.py
    python tools/task_verification_tool.py --check-history src/services/agent_vector_utils.py

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-10-13
License: MIT
"""

import argparse
import ast
import subprocess
import sys
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TaskVerifier:
    """Verifies task state before execution."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.exists = self.file_path.exists()
        self.metrics = {}
        self.git_history = []
        self.refactor_info = {}

    def verify_all(self) -> dict[str, Any]:
        """Run all verification checks."""
        if not self.exists:
            return {
                "status": "FILE_NOT_FOUND",
                "exists": False,
                "path": str(self.file_path),
                "message": f"❌ File does not exist: {self.file_path}",
            }

        self._get_metrics()
        self._check_git_history()
        self._check_refactor_headers()

        return {
            "status": "VERIFIED",
            "exists": True,
            "path": str(self.file_path),
            "metrics": self.metrics,
            "git_history": self.git_history[:5],  # Last 5 commits
            "refactor_info": self.refactor_info,
            "recommendation": self._get_recommendation(),
        }

    def _get_metrics(self):
        """Get current file metrics."""
        try:
            with open(self.file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()

            self.metrics = {
                "lines": len(lines),
                "non_empty_lines": len([l for l in lines if l.strip()]),
            }

            # Try to parse Python AST
            if self.file_path.suffix == ".py":
                try:
                    tree = ast.parse(content)
                    self.metrics.update(
                        {
                            "classes": len(
                                [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                            ),
                            "functions": len(
                                [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
                            ),
                        }
                    )
                except SyntaxError:
                    self.metrics["parse_error"] = True

        except Exception as e:
            self.metrics["error"] = str(e)

    def _check_git_history(self):
        """Check git history for recent changes."""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-n", "5", "--", str(self.file_path)],
                capture_output=True,
                text=True,
                cwd=self.file_path.parent,
            )
            if result.returncode == 0:
                self.git_history = (
                    result.stdout.strip().split("\n") if result.stdout.strip() else []
                )
        except Exception:
            pass

    def _check_refactor_headers(self):
        """Check for refactor/author headers in file."""
        try:
            with open(self.file_path, encoding="utf-8") as f:
                first_50_lines = "".join([f.readline() for _ in range(50)])

            # Look for refactor indicators
            indicators = {
                "refactored": "REFACTORED" in first_50_lines.upper(),
                "v2_compliant": "V2" in first_50_lines and "COMPLIANT" in first_50_lines.upper(),
                "solid": "SOLID" in first_50_lines.upper(),
                "author": None,
            }

            # Extract author if present
            for line in first_50_lines.split("\n"):
                if "Author:" in line or "REFACTORED BY:" in line:
                    indicators["author"] = line.strip()
                    break

            self.refactor_info = indicators

        except Exception as e:
            self.refactor_info["error"] = str(e)

    def _get_recommendation(self) -> str:
        """Get recommendation based on verification."""
        recommendations = []

        # Check if file appears already refactored
        if self.refactor_info.get("refactored"):
            recommendations.append("⚠️  File shows REFACTORED marker - may already be complete!")

        if self.refactor_info.get("v2_compliant"):
            recommendations.append("⚠️  File shows V2 COMPLIANT marker - verify task necessity!")

        if self.refactor_info.get("solid"):
            recommendations.append("⚠️  File shows SOLID marker - may have been refactored!")

        # Check file size compliance
        if self.metrics.get("lines", 0) < 400:
            recommendations.append("✅ File under 400 lines - already V2 size compliant!")

        # Check git history
        if len(self.git_history) > 0:
            recent_commit = self.git_history[0]
            if any(
                word in recent_commit.lower() for word in ["refactor", "consolidate", "v2", "solid"]
            ):
                recommendations.append(f"⚠️  Recent refactor commit: {recent_commit}")

        if not recommendations:
            recommendations.append("✅ No obvious signs of completion - task appears valid!")

        return " | ".join(recommendations)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="🔍 Verify task state before execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic verification
  python tools/task_verification_tool.py src/core/shared_utilities.py
  
  # Check file state
  python tools/task_verification_tool.py --file src/gaming/gaming_integration_core.py
  
  # Verify multiple files
  python tools/task_verification_tool.py src/services/agent_vector_*.py

🔍 ALWAYS VERIFY BEFORE YOU START! 🔍
        """,
    )

    parser.add_argument("files", nargs="*", help="File(s) to verify")
    parser.add_argument("--file", "-f", help="Single file to verify")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Get files to check
    files_to_check = []
    if args.file:
        files_to_check.append(args.file)
    if args.files:
        files_to_check.extend(args.files)

    if not files_to_check:
        parser.print_help()
        return 1

    # Verify each file
    results = []
    for file_path in files_to_check:
        verifier = TaskVerifier(file_path)
        result = verifier.verify_all()
        results.append(result)

        if not args.json:
            print(f"\n{'='*70}")
            print(f"📋 TASK VERIFICATION: {file_path}")
            print(f"{'='*70}")
            print(f"Status: {result['status']}")
            print(f"Exists: {'✅' if result['exists'] else '❌'}")

            if result["exists"]:
                print("\n📊 Metrics:")
                for key, value in result["metrics"].items():
                    print(f"  {key}: {value}")

                if result["git_history"]:
                    print("\n📜 Recent Git History:")
                    for commit in result["git_history"]:
                        print(f"  {commit}")

                if result["refactor_info"]:
                    print("\n🔍 Refactor Indicators:")
                    for key, value in result["refactor_info"].items():
                        if value:
                            print(f"  {key}: {value}")

                print("\n💡 Recommendation:")
                print(f"  {result['recommendation']}")

            print(f"{'='*70}\n")

    if args.json:
        import json

        print(json.dumps(results, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())

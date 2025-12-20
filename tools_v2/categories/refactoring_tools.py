#!/usr/bin/env python3
"""
Refactoring Tools for V2 Compliance
====================================

Tools for automated file refactoring and V2 compliance enforcement.
Based on Agent-1 Lean Excellence mission learnings.

Author: Agent-1 - Testing & Quality Assurance Specialist
Created: 2025-10-14
"""

import ast
import logging
import subprocess
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class FileSizeCheckTool(IToolAdapter):
    """Check file size for V2 compliance."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="refactor.check_file_size",
            version="1.0.0",
            category="refactoring",
            summary="Check if files meet V2 compliance (≤400 lines)",
            required_params=["path"],
            optional_params={"threshold": 400, "recursive": False},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute file size check."""
        try:
            path = Path(params["path"])
            threshold = params.get("threshold", 400)
            recursive = params.get("recursive", False)

            violations = []

            if path.is_file():
                line_count = len(path.read_text(encoding="utf-8").splitlines())
                if line_count > threshold:
                    violations.append(
                        {"file": str(path), "lines": line_count, "excess": line_count - threshold}
                    )
            elif path.is_dir() and recursive:
                for py_file in path.rglob("*.py"):
                    line_count = len(py_file.read_text(encoding="utf-8").splitlines())
                    if line_count > threshold:
                        violations.append(
                            {
                                "file": str(py_file),
                                "lines": line_count,
                                "excess": line_count - threshold,
                            }
                        )

            return ToolResult(
                success=True,
                output={
                    "threshold": threshold,
                    "violations": violations,
                    "compliant": len(violations) == 0,
                    "total_checked": 1 if path.is_file() else len(list(path.rglob("*.py"))),
                },
                exit_code=0,
            )

        except Exception as e:
            logger.error(f"Error checking file size: {e}")
            raise ToolExecutionError(str(e), tool_name="refactor.check_file_size")


class AutoExtractTool(IToolAdapter):
    """Automatically extract functions/classes to reduce file size."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="refactor.auto_extract",
            version="1.0.0",
            category="refactoring",
            summary="Auto-extract functions/classes to meet V2 compliance",
            required_params=["file"],
            optional_params={"target_lines": 400, "strategy": "functions"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute auto-extraction."""
        try:
            file_path = Path(params["file"])
            target_lines = params.get("target_lines", 400)
            strategy = params.get("strategy", "functions")

            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)

            extractable_items = []

            if strategy == "functions":
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        extractable_items.append(
                            {
                                "type": "function",
                                "name": node.name,
                                "start_line": node.lineno,
                                "end_line": node.end_lineno,
                                "size": node.end_lineno - node.lineno,
                            }
                        )
            elif strategy == "classes":
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        extractable_items.append(
                            {
                                "type": "class",
                                "name": node.name,
                                "start_line": node.lineno,
                                "end_line": node.end_lineno,
                                "size": node.end_lineno - node.lineno,
                            }
                        )

            current_lines = len(content.splitlines())
            lines_to_remove = current_lines - target_lines

            # Sort by size (largest first) for extraction candidates
            extractable_items.sort(key=lambda x: x["size"], reverse=True)

            extraction_plan = []
            total_removed = 0

            for item in extractable_items:
                if total_removed >= lines_to_remove:
                    break
                extraction_plan.append(item)
                total_removed += item["size"]

            return ToolResult(
                success=True,
                output={
                    "current_lines": current_lines,
                    "target_lines": target_lines,
                    "lines_to_remove": lines_to_remove,
                    "extraction_plan": extraction_plan,
                    "estimated_final_lines": current_lines - total_removed,
                },
                exit_code=0,
            )

        except Exception as e:
            logger.error(f"Error in auto-extract: {e}")
            raise ToolExecutionError(str(e), tool_name="refactor.auto_extract")


class TestPyramidAnalyzerTool(IToolAdapter):
    """Analyze test pyramid distribution (60/30/10)."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="test.pyramid_check",
            version="1.0.0",
            category="testing",
            summary="Check test pyramid distribution (60% unit, 30% integration, 10% E2E)",
            required_params=[],
            optional_params={"test_dir": "tests/"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute pyramid analysis."""
        try:
            test_dir = Path(params.get("test_dir", "tests/"))

            unit_tests = list(test_dir.glob("unit/test_*.py")) + list(
                test_dir.glob("test_*_unit.py")
            )
            integration_tests = list(test_dir.glob("integration/test_*.py")) + list(
                test_dir.glob("test_*_integration.py")
            )
            e2e_tests = (
                list(test_dir.glob("e2e/test_*.py"))
                + list(test_dir.glob("test_*_e2e.py"))
                + list(test_dir.glob("**/test_*_smoke.py"))
            )

            total = len(unit_tests) + len(integration_tests) + len(e2e_tests)

            if total == 0:
                unit_pct = integration_pct = e2e_pct = 0
            else:
                unit_pct = (len(unit_tests) / total) * 100
                integration_pct = (len(integration_tests) / total) * 100
                e2e_pct = (len(e2e_tests) / total) * 100

            ideal_pyramid = {"unit": 60, "integration": 30, "e2e": 10}
            actual_pyramid = {
                "unit": round(unit_pct, 1),
                "integration": round(integration_pct, 1),
                "e2e": round(e2e_pct, 1),
            }

            # Check if pyramid is inverted or balanced
            is_balanced = (
                50 <= unit_pct <= 70 and 20 <= integration_pct <= 40 and 5 <= e2e_pct <= 15
            )

            is_inverted = e2e_pct > unit_pct

            return ToolResult(
                success=True,
                output={
                    "total_tests": total,
                    "unit_tests": len(unit_tests),
                    "integration_tests": len(integration_tests),
                    "e2e_tests": len(e2e_tests),
                    "ideal_pyramid": ideal_pyramid,
                    "actual_pyramid": actual_pyramid,
                    "is_balanced": is_balanced,
                    "is_inverted": is_inverted,
                    "recommendations": self._generate_recommendations(
                        actual_pyramid, ideal_pyramid
                    ),
                },
                exit_code=0,
            )

        except Exception as e:
            logger.error(f"Error analyzing test pyramid: {e}")
            raise ToolExecutionError(str(e), tool_name="test.pyramid_check")

    def _generate_recommendations(
        self, actual: dict[str, float], ideal: dict[str, float]
    ) -> list[str]:
        """Generate pyramid recommendations."""
        recommendations = []

        if actual["unit"] < ideal["unit"]:
            recommendations.append(
                f"Add {int(ideal['unit'] - actual['unit'])}% more unit tests"
            )
        if actual["integration"] < ideal["integration"]:
            recommendations.append(
                f"Add {int(ideal['integration'] - actual['integration'])}% more integration tests"
            )
        if actual["e2e"] > ideal["e2e"]:
            recommendations.append(f"Reduce E2E tests by {int(actual['e2e'] - ideal['e2e'])}%")

        return recommendations


class LintFixTool(IToolAdapter):
    """Auto-fix linting issues."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="refactor.lint_fix",
            version="1.0.0",
            category="refactoring",
            summary="Auto-fix linting issues with ruff/black",
            required_params=["path"],
            optional_params={"formatter": "ruff"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute lint fixes."""
        try:
            path = params["path"]
            formatter = params.get("formatter", "ruff")

            if formatter == "ruff":
                result = subprocess.run(
                    ["ruff", "check", "--fix", path], capture_output=True, text=True
                )
            elif formatter == "black":
                result = subprocess.run(["black", path], capture_output=True, text=True)
            else:
                result = subprocess.run(
                    ["ruff", "format", path], capture_output=True, text=True
                )

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )

        except Exception as e:
            logger.error(f"Error in lint fix: {e}")
            raise ToolExecutionError(str(e), tool_name="refactor.lint_fix")


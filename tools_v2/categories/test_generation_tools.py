#!/usr/bin/env python3
"""
Test Generation Tools
====================

Auto-generate test files and test templates based on source code.
Based on Agent-1 Testing Pyramid mission learnings.

Author: Agent-1 - Testing & Quality Assurance Specialist
Created: 2025-10-14
"""

import ast
import logging
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class TestFileGeneratorTool(IToolAdapter):
    """Generate test file template from source file."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="test.generate_template",
            version="1.0.0",
            category="testing",
            summary="Generate test file template from source code",
            required_params=["source_file"],
            optional_params={"test_type": "unit", "coverage_target": 100},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute test template generation."""
        try:
            source_file = Path(params["source_file"])
            test_type = params.get("test_type", "unit")
            coverage_target = params.get("coverage_target", 100)

            if not source_file.exists():
                raise FileNotFoundError(f"Source file not found: {source_file}")

            content = source_file.read_text(encoding="utf-8")
            tree = ast.parse(content)

            # Extract classes and functions
            classes = []
            functions = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    classes.append({"name": node.name, "methods": methods})
                elif isinstance(node, ast.FunctionDef) and not any(
                    isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)
                ):
                    functions.append(node.name)

            # Generate test file template
            test_template = self._generate_test_template(
                source_file, classes, functions, test_type, coverage_target
            )

            # Determine test file path
            test_file_path = Path(f"tests/{test_type}/test_{source_file.stem}.py")

            return ToolResult(
                success=True,
                output={
                    "source_file": str(source_file),
                    "test_file": str(test_file_path),
                    "test_template": test_template,
                    "classes_found": len(classes),
                    "functions_found": len(functions),
                    "estimated_tests": len(classes) * 5 + len(functions) * 3,
                },
                exit_code=0,
            )

        except Exception as e:
            logger.error(f"Error generating test template: {e}")
            raise ToolExecutionError(str(e), tool_name="test.generate_template")

    def _generate_test_template(
        self,
        source_file: Path,
        classes: list[dict],
        functions: list[str],
        test_type: str,
        coverage_target: int,
    ) -> str:
        """Generate test template content."""
        module_path = str(source_file).replace("\\", ".").replace("/", ".").replace(".py", "")

        template = f'''#!/usr/bin/env python3
"""
{test_type.capitalize()} Tests for {source_file.name}
{"=" * (len(source_file.name) + len(test_type) + 11)}

Author: Agent-1 - Testing & Quality Assurance Specialist
Coverage Target: {coverage_target}%
"""

import pytest
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from {module_path} import (
'''

        # Add imports
        for cls in classes:
            template += f"    {cls['name']},\n"
        for func in functions:
            template += f"    {func},\n"

        template += ")\n\n"

        # Generate test classes
        for cls in classes:
            template += f"""
class Test{cls['name']}:
    \"\"\"Test suite for {cls['name']}.\"\"\"

    def setup_method(self):
        \"\"\"Set up test fixtures.\"\"\"
        # TODO: Initialize test fixtures

    def test_init(self):
        \"\"\"Test {cls['name']} initialization.\"\"\"
        # TODO: Implement initialization test
        pass

"""
            for method in cls["methods"]:
                if not method.startswith("_"):
                    template += f"""    def test_{method}(self):
        \"\"\"Test {method} method.\"\"\"
        # TODO: Implement {method} test
        pass

"""

        # Generate function tests
        if functions:
            template += """
class TestFunctions:
    \"\"\"Test suite for module functions.\"\"\"

"""
            for func in functions:
                template += f"""    def test_{func}(self):
        \"\"\"Test {func} function.\"\"\"
        # TODO: Implement {func} test
        pass

"""

        template += '''
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''

        return template


class CoveragePyramidReportTool(IToolAdapter):
    """Generate coverage + pyramid combined report."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="test.coverage_pyramid_report",
            version="1.0.0",
            category="testing",
            summary="Combined coverage and pyramid distribution report",
            required_params=[],
            optional_params={"test_dir": "tests/", "min_coverage": 85},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute combined report."""
        try:
            import subprocess

            # Run coverage
            cov_result = subprocess.run(
                ["coverage", "run", "-m", "pytest", "-q"], capture_output=True, text=True
            )

            # Get coverage report
            cov_report = subprocess.run(
                ["coverage", "report"], capture_output=True, text=True
            )

            # Parse coverage percentage
            coverage_pct = 0.0
            for line in cov_report.stdout.splitlines():
                if "TOTAL" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        coverage_pct = float(parts[3].replace("%", ""))

            # Get pyramid distribution (would call pyramid_check tool)
            test_dir = Path(params.get("test_dir", "tests/"))

            unit_tests = len(list(test_dir.glob("unit/test_*.py")))
            integration_tests = len(list(test_dir.glob("integration/test_*.py")))
            e2e_tests = len(list(test_dir.glob("e2e/test_*.py")))

            total = unit_tests + integration_tests + e2e_tests

            return ToolResult(
                success=True,
                output={
                    "coverage": {
                        "percentage": coverage_pct,
                        "target": params.get("min_coverage", 85),
                        "meets_target": coverage_pct >= params.get("min_coverage", 85),
                    },
                    "pyramid": {
                        "total_tests": total,
                        "unit": unit_tests,
                        "integration": integration_tests,
                        "e2e": e2e_tests,
                        "unit_pct": (unit_tests / total * 100) if total > 0 else 0,
                        "integration_pct": (integration_tests / total * 100) if total > 0 else 0,
                        "e2e_pct": (e2e_tests / total * 100) if total > 0 else 0,
                    },
                    "overall_quality": "excellent"
                    if coverage_pct >= 85 and 50 <= (unit_tests / total * 100) <= 70
                    else "good"
                    if coverage_pct >= 70
                    else "needs_improvement",
                },
                exit_code=0,
            )

        except Exception as e:
            logger.error(f"Error generating coverage pyramid report: {e}")
            raise ToolExecutionError(str(e), tool_name="test.coverage_pyramid_report")


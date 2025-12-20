"""
Testing Tools
=============

Tool adapters for testing and coverage operations.

V2 Compliance: <180 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import logging
import subprocess
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class CoverageReportTool(IToolAdapter):
    """Generate test coverage report."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="test.coverage",
            version="1.0.0",
            category="testing",
            summary="Run tests with coverage analysis",
            required_params=[],
            optional_params={"path": "tests/", "html": False, "min_coverage": 85},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])  # No required params

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute coverage analysis."""
        try:
            cmd = ["python", "tools/coverage/run_coverage_analysis.py"]

            if params.get("html"):
                cmd.append("--html")

            result = subprocess.run(cmd, capture_output=True, text=True)

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error running coverage: {e}")
            raise ToolExecutionError(str(e), tool_name="test.coverage")


class MutationGateTool(IToolAdapter):
    """Run mutation testing gate."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="test.mutation",
            version="1.0.0",
            category="testing",
            summary="Run mutation testing quality gate",
            required_params=[],
            optional_params={"threshold": 80},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute mutation testing."""
        try:
            cmd = ["python", "tools/coverage/mutation_gate.py"]

            result = subprocess.run(cmd, capture_output=True, text=True)

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error running mutation tests: {e}")
            raise ToolExecutionError(str(e), tool_name="test.mutation")

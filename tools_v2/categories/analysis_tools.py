"""
Analysis Tools
==============

Tool adapters for code analysis operations.

V2 Compliance: <220 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import logging
import subprocess
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class ProjectScanTool(IToolAdapter):
    """Run comprehensive project scan."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="analysis.scan",
            version="1.0.0",
            category="analysis",
            summary="Run comprehensive project analysis scan",
            required_params=[],
            optional_params={"enhanced": False},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])  # No required params

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute project scan."""
        try:
            if params.get("enhanced"):
                cmd = ["python", "comprehensive_project_analyzer.py"]
            else:
                cmd = ["python", "tools/run_project_scan.py"]

            result = subprocess.run(cmd, capture_output=True, text=True)

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error running project scan: {e}")
            raise ToolExecutionError(str(e), tool_name="analysis.scan")


class ComplexityTool(IToolAdapter):
    """Analyze code complexity."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="analysis.complexity",
            version="1.0.0",
            category="analysis",
            summary="Analyze code complexity and cyclomatic metrics",
            required_params=["path"],
            optional_params={"threshold": 10, "format": "text"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute complexity analysis."""
        try:
            cmd = ["python", "tools/complexity_analyzer_cli.py", params["path"]]

            if params.get("threshold"):
                cmd.extend(["--threshold", str(params["threshold"])])

            result = subprocess.run(cmd, capture_output=True, text=True)

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error analyzing complexity: {e}")
            raise ToolExecutionError(str(e), tool_name="analysis.complexity")


class DuplicationTool(IToolAdapter):
    """Find duplicate code."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="analysis.duplicates",
            version="1.0.0",
            category="analysis",
            summary="Detect duplicate code and consolidation opportunities",
            required_params=["path"],
            optional_params={"min_lines": 5, "report": False},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute duplication analysis."""
        try:
            cmd = ["python", "tools/duplication_analyzer.py", params["path"]]

            result = subprocess.run(cmd, capture_output=True, text=True)

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error analyzing duplicates: {e}")
            raise ToolExecutionError(str(e), tool_name="analysis.duplicates")

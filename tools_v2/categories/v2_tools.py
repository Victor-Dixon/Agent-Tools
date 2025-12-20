"""
V2 Compliance Tools
===================

Tool adapters for V2 compliance checking and reporting.

V2 Compliance: <180 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import logging
import subprocess
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class V2CheckTool(IToolAdapter):
    """Check V2 compliance violations."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="v2.check",
            version="1.0.0",
            category="v2",
            summary="Check files for V2 compliance violations (≤400 lines)",
            required_params=["path"],
            optional_params={"fix": False, "recursive": True},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute V2 compliance check."""
        try:
            cmd = ["python", "tools/v2_checker_cli.py", "--check", params["path"]]

            if params.get("fix"):
                cmd.append("--fix")

            result = subprocess.run(cmd, capture_output=True, text=True)

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error checking V2 compliance: {e}")
            raise ToolExecutionError(str(e), tool_name="v2.check")


class V2ReportTool(IToolAdapter):
    """Generate V2 compliance report."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="v2.report",
            version="1.0.0",
            category="v2",
            summary="Generate comprehensive V2 compliance report",
            required_params=[],
            optional_params={"format": "text", "path": "src/"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])  # No required params

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute V2 report generation."""
        try:
            cmd = ["python", "tools/v2_checker_cli.py", "--report"]

            if params.get("format") == "json":
                cmd.append("--json")

            result = subprocess.run(cmd, capture_output=True, text=True)

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error generating V2 report: {e}")
            raise ToolExecutionError(str(e), tool_name="v2.report")

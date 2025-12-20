"""
Compliance Tools
================

Tool adapters for compliance tracking and history.

V2 Compliance: <180 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import logging
import subprocess
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class ComplianceHistoryTool(IToolAdapter):
    """View compliance history and trends."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="comp.history",
            version="1.0.0",
            category="compliance",
            summary="View compliance history and trend analysis",
            required_params=[],
            optional_params={"agent_id": None, "days": 7, "format": "text"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])  # No required params

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute compliance history retrieval."""
        try:
            cmd = ["python", "tools/compliance_history_tracker.py", "--history"]

            if params.get("agent_id"):
                cmd.extend(["--agent", params["agent_id"]])

            if params.get("days"):
                cmd.extend(["--days", str(params["days"])])

            result = subprocess.run(cmd, capture_output=True, text=True)

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error getting compliance history: {e}")
            raise ToolExecutionError(str(e), tool_name="comp.history")


class PolicyCheckTool(IToolAdapter):
    """Check policy compliance."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="comp.check",
            version="1.0.0",
            category="compliance",
            summary="Check code against project policies and standards",
            required_params=["path"],
            optional_params={"policy": "all", "strict": False},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute policy check."""
        try:
            cmd = ["python", "tools/compliance_dashboard.py", "--check", params["path"]]

            result = subprocess.run(cmd, capture_output=True, text=True)

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error checking policy compliance: {e}")
            raise ToolExecutionError(str(e), tool_name="comp.check")

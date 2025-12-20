"""
Onboarding Tools
================

Tool adapters for agent onboarding operations.

V2 Compliance: <180 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import logging
import subprocess
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class SoftOnboardTool(IToolAdapter):
    """Soft onboarding (3-step cleanup + onboard)."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="onboard.soft",
            version="1.0.0",
            category="onboarding",
            summary="Soft onboarding with 3-step session cleanup protocol",
            required_params=["agent_id", "message"],
            optional_params={"priority": "regular"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute soft onboarding."""
        try:
            cmd = [
                "python",
                "-m",
                "src.services.messaging_cli",
                "--soft-onboarding",
                "--agent",
                params["agent_id"],
                "--message",
                params["message"],
                "--priority",
                params.get("priority", "regular"),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error during soft onboarding: {e}")
            raise ToolExecutionError(str(e), tool_name="onboard.soft")


class HardOnboardTool(IToolAdapter):
    """Hard onboarding (complete reset with confirmation)."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="onboard.hard",
            version="1.0.0",
            category="onboarding",
            summary="Hard onboarding with complete reset (DESTRUCTIVE - requires --yes)",
            required_params=["agent_id", "message"],
            optional_params={"confirm": False},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        is_valid, missing = spec.validate_params(params)

        # Require confirmation for destructive operation
        if is_valid and not params.get("confirm"):
            return (False, ["confirm (use --yes to confirm destructive operation)"])

        return (is_valid, missing)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute hard onboarding."""
        try:
            cmd = [
                "python",
                "-m",
                "src.services.messaging_cli",
                "--hard-onboarding",
                "--agent",
                params["agent_id"],
                "--message",
                params["message"],
                "--yes",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error during hard onboarding: {e}")
            raise ToolExecutionError(str(e), tool_name="onboard.hard")

"""
Health Monitoring Tools
=======================

Tool adapters for project health and monitoring operations.

V2 Compliance: <180 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import logging
import subprocess
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class HealthPingTool(IToolAdapter):
    """Check project health status."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="health.ping",
            version="1.0.0",
            category="health",
            summary="Quick health check of project status",
            required_params=[],
            optional_params={"check_snapshots": True, "check_agents": True},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])  # No required params

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute health ping."""
        try:
            health_status = {
                "project_root": str(Path.cwd()),
                "snapshots_current": False,
                "agents_active": 0,
            }

            # Check snapshots
            if params.get("check_snapshots", True):
                snapshot_check = subprocess.run(
                    ["python", "tools/check_snapshot_up_to_date.py"], capture_output=True
                )
                health_status["snapshots_current"] = snapshot_check.returncode == 0

            # Check active agents
            if params.get("check_agents", True):
                agent_workspaces = Path("agent_workspaces")
                if agent_workspaces.exists():
                    health_status["agents_active"] = len(list(agent_workspaces.glob("Agent-*")))

            return ToolResult(success=True, output=health_status, exit_code=0)
        except Exception as e:
            logger.error(f"Error checking health: {e}")
            raise ToolExecutionError(str(e), tool_name="health.ping")


class SnapshotTool(IToolAdapter):
    """Create or update captain snapshot."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="health.snapshot",
            version="1.0.0",
            category="health",
            summary="Create or update project snapshot for captain tracking",
            required_params=[],
            optional_params={"update": True, "validate": False},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute snapshot operation."""
        try:
            if params.get("validate"):
                cmd = ["python", "tools/check_snapshot_up_to_date.py"]
            else:
                cmd = ["python", "tools/captain_snapshot.py"]
                if params.get("update"):
                    cmd.append("--update")

            result = subprocess.run(cmd, capture_output=True, text=True)

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error with snapshot: {e}")
            raise ToolExecutionError(str(e), tool_name="health.snapshot")

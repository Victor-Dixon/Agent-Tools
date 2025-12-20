"""
Agent Operations Tools
======================

Tool adapters for agent status and operations.

V2 Compliance: <220 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import json
import logging
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class AgentStatusTool(IToolAdapter):
    """Get comprehensive agent status."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="agent.status",
            version="1.0.0",
            category="agent_ops",
            summary="Get comprehensive agent status and metrics",
            required_params=["agent_id"],
            optional_params={"include_vector": True},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute status retrieval."""
        try:
            from src.services.agent_management import AgentStatusManager

            agent_id = params["agent_id"]
            status_mgr = AgentStatusManager(agent_id=agent_id)
            status = status_mgr.get_agent_status()

            return ToolResult(success=True, output=status, exit_code=0)
        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            raise ToolExecutionError(str(e), tool_name="agent.status")


class ClaimTaskTool(IToolAdapter):
    """Claim next available task from queue."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="agent.claim",
            version="1.0.0",
            category="agent_ops",
            summary="Claim next available task from task queue",
            required_params=["agent_id"],
            optional_params={"task_type": None, "priority": None},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute task claiming."""
        try:
            agent_id = params["agent_id"]

            # Check for available tasks in message_queue
            queue_path = Path(f"message_queue/{agent_id}")
            if queue_path.exists():
                tasks = list(queue_path.glob("*.json"))
                if tasks:
                    # Read first task
                    task_file = tasks[0]
                    task_data = json.loads(task_file.read_text())

                    return ToolResult(
                        success=True,
                        output={"task": task_data, "source": str(task_file)},
                        exit_code=0,
                    )

            return ToolResult(
                success=True,
                output={"message": "No tasks available", "agent_id": agent_id},
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error claiming task: {e}")
            raise ToolExecutionError(str(e), tool_name="agent.claim")

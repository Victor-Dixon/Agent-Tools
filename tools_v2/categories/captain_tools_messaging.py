"""
Captain Operations Tools - Messaging
=====================================

Messaging tools for captain operations.

V2 Compliance: <400 lines
Author: Agent-2 (Architecture & Design) - 2025-01-27
Split from captain_tools_extension.py (986 lines → 3 files)
"""

import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)

# Swarm agents list
SWARM_AGENTS = [f"Agent-{i}" for i in range(1, 9)]


class SelfMessageTool(IToolAdapter):
    """Send self-message to Captain (Agent-4) as reminder."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.self_message",
            version="1.0.0",
            category="captain",
            summary="Send self-message to Captain (Agent-4) as reminder",
            required_params=["message"],
            optional_params={"priority": "regular"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        errors = []
        if "message" not in params:
            errors.append("message is required")
        return len(errors) == 0, errors

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Send self-message to Captain."""
        try:
            message = params["message"]
            priority = params.get("priority", "regular")

            # Send message to Agent-4 (Captain)
            cmd = [
                "python",
                "-m",
                "src.services.messaging_cli",
                "--agent",
                "Agent-4",
                "--message",
                f"[SELF-REMINDER] {message}",
                "--priority",
                priority,
                "--mode",
                "pyautogui",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            return ToolResult(
                success=result.returncode == 0,
                output={
                    "message_sent": result.returncode == 0,
                    "message": message,
                    "priority": priority,
                    "stdout": result.stdout,
                },
                exit_code=result.returncode,
                execution_time=0.0,
            )
        except Exception as e:
            logger.error(f"Error sending self-message: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.self_message")


class MessageAllAgentsTool(IToolAdapter):
    """Send message to all swarm agents including Captain."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.message_all",
            version="1.0.0",
            category="captain",
            summary="Send message to all swarm agents",
            required_params=["message"],
            optional_params={
                "priority": "regular",
                "include_captain": True,
                "tags": [],
            },
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        errors = []
        if "message" not in params:
            errors.append("message is required")
        return len(errors) == 0, errors

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Send message to all agents."""
        try:
            message = params["message"]
            priority = params.get("priority", "regular")
            include_captain = params.get("include_captain", True)
            tags = params.get("tags", [])

            agents_to_message = (
                SWARM_AGENTS if include_captain else [a for a in SWARM_AGENTS if a != "Agent-4"]
            )

            results = {}
            successful = 0
            failed = 0

            for agent_id in agents_to_message:
                cmd = [
                    "python",
                    "-m",
                    "src.services.messaging_cli",
                    "--agent",
                    agent_id,
                    "--message",
                    message,
                    "--priority",
                    priority,
                    "--mode",
                    "pyautogui",
                ]

                if tags:
                    cmd.extend(["--tags"] + tags)

                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    success = result.returncode == 0
                    results[agent_id] = {
                        "success": success,
                        "stdout": result.stdout,
                        "stderr": result.stderr if not success else None,
                    }

                    if success:
                        successful += 1
                    else:
                        failed += 1

                except Exception as e:
                    results[agent_id] = {"success": False, "error": str(e)}
                    failed += 1

            return ToolResult(
                success=successful > 0,
                output={
                    "total_agents": len(agents_to_message),
                    "successful": successful,
                    "failed": failed,
                    "results": results,
                    "message": message,
                    "priority": priority,
                },
                exit_code=0 if failed == 0 else 1,
                execution_time=0.0,
            )
        except Exception as e:
            logger.error(f"Error messaging all agents: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.message_all")


# Export all tools
__all__ = [
    "SelfMessageTool",
    "MessageAllAgentsTool",
]





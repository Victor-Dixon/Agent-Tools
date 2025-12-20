"""
Messaging Tools
===============

Tool adapters for agent messaging operations.

V2 Compliance: <220 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import logging
import subprocess
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class SendMessageTool(IToolAdapter):
    """Send message to specific agent."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="msg.send",
            version="1.0.0",
            category="messaging",
            summary="Send message to a specific agent via PyAutoGUI",
            required_params=["agent_id", "message"],
            optional_params={"priority": "regular", "tags": []},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute message sending."""
        try:
            cmd = [
                "python",
                "-m",
                "src.services.messaging_cli",
                "--agent",
                params["agent_id"],
                "--message",
                params["message"],
                "--priority",
                params.get("priority", "regular"),
            ]

            if params.get("tags"):
                cmd.extend(["--tags"] + params["tags"])

            result = subprocess.run(cmd, capture_output=True, text=True)

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise ToolExecutionError(str(e), tool_name="msg.send")


class BroadcastTool(IToolAdapter):
    """Broadcast message to all agents."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="msg.broadcast",
            version="1.0.0",
            category="messaging",
            summary="Broadcast message to all agents",
            required_params=["message"],
            optional_params={"priority": "regular"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute broadcast."""
        try:
            cmd = [
                "python",
                "-m",
                "src.services.messaging_cli",
                "--broadcast",
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
            logger.error(f"Error broadcasting message: {e}")
            raise ToolExecutionError(str(e), tool_name="msg.broadcast")


class InboxCheckTool(IToolAdapter):
    """Check agent inbox with optional semantic search."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="msg.inbox",
            version="1.0.0",
            category="messaging",
            summary="Check agent inbox, optionally with semantic search",
            required_params=["agent_id"],
            optional_params={"search_query": None},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute inbox check."""
        try:
            from pathlib import Path

            agent_id = params["agent_id"]
            inbox_path = Path(f"agent_workspaces/{agent_id}/inbox")

            if not inbox_path.exists():
                return ToolResult(
                    success=False,
                    output={"error": f"No inbox found for {agent_id}"},
                    exit_code=1,
                    error_message=f"Inbox not found: {inbox_path}",
                )

            messages = list(inbox_path.glob("*.md"))

            if params.get("search_query"):
                # TODO: Implement semantic search
                filtered = [m for m in messages if params["search_query"].lower() in m.name.lower()]
                messages = filtered

            return ToolResult(
                success=True,
                output={
                    "agent_id": agent_id,
                    "message_count": len(messages),
                    "messages": [m.name for m in messages[:20]],
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error checking inbox: {e}")
            raise ToolExecutionError(str(e), tool_name="msg.inbox")

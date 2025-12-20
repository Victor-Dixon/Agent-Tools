"""
Queue Monitor Tools - Agent Toolbelt V2
========================================

Tools for monitoring message queue status.

Author: Agent-4 (Captain)
Date: 2025-01-27
V2 Compliance: <300 lines per tool
"""

import logging
from typing import Any, Dict

from ..adapters.base_adapter import IToolAdapter, ToolResult
from ..core.tool_spec import ToolSpec

logger = logging.getLogger(__name__)


class QueueStatusMonitorTool(IToolAdapter):
    """Monitor message queue status."""

    def get_name(self) -> str:
        return "queue.status"

    def get_description(self) -> str:
        return "Monitor message queue status (pending, processing, delivered)"

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="queue.status",
            version="1.0.0",
            category="messaging",
            summary="Monitor queue status",
            required_params=[],
            optional_params={},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Monitor queue status."""
        try:
            from src.core.message_queue import MessageQueue

            queue = MessageQueue()
            entries = queue.persistence.load_entries()

            # Count by status
            status_counts = {"PENDING": 0, "PROCESSING": 0, "DELIVERED": 0, "FAILED": 0}

            for entry in entries:
                status = getattr(entry, "status", "UNKNOWN")
                status_counts[status] = status_counts.get(status, 0) + 1

            output = {
                "total_entries": len(entries),
                "by_status": status_counts,
                "pending": status_counts["PENDING"],
                "processing": status_counts["PROCESSING"],
                "delivered": status_counts["DELIVERED"],
                "failed": status_counts["FAILED"],
            }

            return ToolResult(success=True, output=output)

        except Exception as e:
            logger.error(f"Queue status monitoring failed: {e}")
            return ToolResult(
                success=False, output=None, error_message=str(e), exit_code=1
            )


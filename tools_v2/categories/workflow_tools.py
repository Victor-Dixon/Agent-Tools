"""
Workflow Tools
==============

Tools for inbox management, mission claiming, and workflow automation.

V2 Compliance: <250 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class InboxCleanupTool(IToolAdapter):
    """Clean old messages from agent inbox."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="msg.cleanup",
            version="1.0.0",
            category="workflow",
            summary="Clean old messages from inbox (archive or delete)",
            required_params=["agent_id"],
            optional_params={"days_old": 7, "action": "archive", "dry_run": False},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute inbox cleanup."""
        try:
            agent_id = params["agent_id"]
            days_old = params.get("days_old", 7)
            action = params.get("action", "archive")
            dry_run = params.get("dry_run", False)

            inbox_path = Path(f"agent_workspaces/{agent_id}/inbox")
            if not inbox_path.exists():
                return ToolResult(
                    success=False, output={"error": f"No inbox found for {agent_id}"}, exit_code=1
                )

            cutoff_date = datetime.now() - timedelta(days=days_old)
            old_messages = []

            for msg_file in inbox_path.glob("*.md"):
                if msg_file.stat().st_mtime < cutoff_date.timestamp():
                    old_messages.append(msg_file)

            if dry_run:
                return ToolResult(
                    success=True,
                    output={
                        "dry_run": True,
                        "messages_found": len(old_messages),
                        "files": [f.name for f in old_messages],
                    },
                    exit_code=0,
                )

            # Execute cleanup
            archive_path = Path(f"agent_workspaces/{agent_id}/inbox_archive")
            processed = []

            for msg_file in old_messages:
                if action == "archive":
                    archive_path.mkdir(exist_ok=True)
                    msg_file.rename(archive_path / msg_file.name)
                    processed.append(f"archived: {msg_file.name}")
                elif action == "delete":
                    msg_file.unlink()
                    processed.append(f"deleted: {msg_file.name}")

            return ToolResult(
                success=True,
                output={
                    "agent_id": agent_id,
                    "action": action,
                    "processed": len(processed),
                    "files": processed,
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error cleaning inbox: {e}")
            raise ToolExecutionError(str(e), tool_name="msg.cleanup")


class MissionClaimTool(IToolAdapter):
    """Claim high-value mission from queue."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="mission.claim",
            version="1.0.0",
            category="workflow",
            summary="Claim next high-value mission from task queue",
            required_params=["agent_id"],
            optional_params={"sort_by": "roi", "min_points": 0},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute mission claiming."""
        try:
            agent_id = params["agent_id"]
            sort_by = params.get("sort_by", "roi")
            min_points = params.get("min_points", 0)

            # Check inbox for mission assignments
            inbox_path = Path(f"agent_workspaces/{agent_id}/inbox")
            if not inbox_path.exists():
                return ToolResult(
                    success=False, output={"error": f"No inbox found for {agent_id}"}, exit_code=1
                )

            # Find mission files
            missions = []
            for msg_file in inbox_path.glob("*.md"):
                content = msg_file.read_text()

                # Extract mission metadata (simple parsing)
                if "MISSION" in content or "ORDER" in content:
                    missions.append(
                        {
                            "file": msg_file.name,
                            "path": str(msg_file),
                            "modified": msg_file.stat().st_mtime,
                            "content_preview": content[:200],
                        }
                    )

            if not missions:
                return ToolResult(
                    success=True,
                    output={
                        "agent_id": agent_id,
                        "missions_available": 0,
                        "message": "No missions in inbox",
                    },
                    exit_code=0,
                )

            # Sort missions
            if sort_by == "roi":
                missions.sort(key=lambda m: m["modified"], reverse=True)

            claimed_mission = missions[0]

            return ToolResult(
                success=True,
                output={
                    "agent_id": agent_id,
                    "mission_claimed": claimed_mission["file"],
                    "total_available": len(missions),
                    "preview": claimed_mission["content_preview"],
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error claiming mission: {e}")
            raise ToolExecutionError(str(e), tool_name="mission.claim")


class ROICalculatorTool(IToolAdapter):
    """Calculate ROI for potential tasks."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="workflow.roi",
            version="1.0.0",
            category="workflow",
            summary="Calculate ROI (return on investment) for task prioritization",
            required_params=["task_description"],
            optional_params={"estimated_hours": 1, "points_estimate": 0},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute ROI calculation."""
        try:
            task = params["task_description"]
            hours = params.get("estimated_hours", 1)
            points = params.get("points_estimate", 0)

            # Simple ROI calculation
            if hours == 0:
                hours = 0.5  # Minimum

            roi = points / hours if hours > 0 else 0

            # Priority classification
            if roi >= 500:
                priority = "CRITICAL"
            elif roi >= 300:
                priority = "HIGH"
            elif roi >= 150:
                priority = "MEDIUM"
            else:
                priority = "LOW"

            return ToolResult(
                success=True,
                output={
                    "task": task[:100],
                    "estimated_hours": hours,
                    "estimated_points": points,
                    "roi": round(roi, 2),
                    "priority": priority,
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error calculating ROI: {e}")
            raise ToolExecutionError(str(e), tool_name="workflow.roi")

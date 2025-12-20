"""
Agent Activity Tracking Tools - Agent Toolbelt V2
=================================================

Tools for tracking and viewing agent runtime activity.

Author: Agent-4 (Captain)
Date: 2025-01-27
V2 Compliance: <300 lines per tool
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..adapters.base_adapter import IToolAdapter, ToolResult
from ..core.tool_spec import ToolSpec

logger = logging.getLogger(__name__)


class AgentActivityTrackerTool(IToolAdapter):
    """Track agent runtime activity."""

    def get_name(self) -> str:
        return "agent_activity.track"

    def get_description(self) -> str:
        return "Track and view agent runtime activity (who's actively working)"

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="agent_activity.track",
            version="1.0.0",
            category="monitoring",
            summary="Track agent activity",
            required_params=[],
            optional_params={"agent_id": None, "check_all": False},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Track agent activity."""
        try:
            agent_id = params.get("agent_id")
            check_all = params.get("check_all", False)

            activity_data = {}

            if check_all or not agent_id:
                # Check all agents
                for i in range(1, 9):
                    aid = f"Agent-{i}"
                    activity = self._check_agent_activity(aid)
                    activity_data[aid] = activity
            else:
                # Check specific agent
                activity = self._check_agent_activity(agent_id)
                activity_data[agent_id] = activity

            return ToolResult(success=True, output=activity_data)

        except Exception as e:
            logger.error(f"Agent activity tracking failed: {e}")
            return ToolResult(
                success=False, output=None, error_message=str(e), exit_code=1
            )

    def _check_agent_activity(self, agent_id: str) -> dict[str, Any]:
        """Check activity for a single agent."""
        workspace = Path("agent_workspaces") / agent_id
        current_time = time.time()

        activity = {
            "agent_id": agent_id,
            "status": "unknown",
            "last_status_update": None,
            "last_devlog": None,
            "inbox_processed": False,
            "queue_activity": None,
        }

        # Check status.json
        status_file = workspace / "status.json"
        if status_file.exists():
            try:
                status_data = json.loads(status_file.read_text())
                activity["last_status_update"] = status_file.stat().st_mtime
                activity["current_mission"] = status_data.get("current_mission")
                activity["current_phase"] = status_data.get("current_phase")
            except Exception:
                pass

        # Check devlogs
        devlogs_dir = Path("devlogs")
        if devlogs_dir.exists():
            agent_devlogs = list(devlogs_dir.glob(f"*{agent_id.lower()}*.md"))
            if agent_devlogs:
                latest = max(agent_devlogs, key=lambda p: p.stat().st_mtime)
                activity["last_devlog"] = latest.stat().st_mtime
                activity["devlog_age_seconds"] = current_time - activity["last_devlog"]

        # Check inbox
        inbox_dir = workspace / "inbox"
        if inbox_dir.exists():
            inbox_files = list(inbox_dir.glob("*.md"))
            activity["inbox_count"] = len(inbox_files)
            activity["inbox_processed"] = len(inbox_files) == 0

        # Check queue activity
        try:
            from src.core.message_queue import MessageQueue

            queue = MessageQueue()
            # Check if agent has messages in queue
            # This would need queue inspection capability
            activity["queue_activity"] = "unknown"
        except Exception:
            pass

        # Determine activity status
        if activity["last_status_update"]:
            age = current_time - activity["last_status_update"]
            if age < 300:  # 5 minutes
                activity["status"] = "active"
            elif age < 3600:  # 1 hour
                activity["status"] = "recent"
            else:
                activity["status"] = "inactive"
        else:
            activity["status"] = "unknown"

        return activity


class AgentActivityMonitorTool(IToolAdapter):
    """Monitor all agent activity in real-time."""

    def get_name(self) -> str:
        return "agent_activity.monitor"

    def get_description(self) -> str:
        return "Monitor all agent activity and show who's actively working"

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="agent_activity.monitor",
            version="1.0.0",
            category="monitoring",
            summary="Monitor all agents",
            required_params=[],
            optional_params={},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Monitor all agent activity."""
        try:
            from tools_v2.categories.agent_activity_tools import (
                AgentActivityTrackerTool,
            )

            tracker = AgentActivityTrackerTool()
            result = tracker.execute({"check_all": True})

            if result.success:
                # Format for monitoring display
                output = {
                    "timestamp": datetime.now().isoformat(),
                    "agents": result.output,
                    "summary": {
                        "active": sum(
                            1
                            for a in result.output.values()
                            if a.get("status") == "active"
                        ),
                        "recent": sum(
                            1
                            for a in result.output.values()
                            if a.get("status") == "recent"
                        ),
                        "inactive": sum(
                            1
                            for a in result.output.values()
                            if a.get("status") == "inactive"
                        ),
                    },
                }
                return ToolResult(success=True, output=output)

            return result

        except Exception as e:
            logger.error(f"Agent activity monitoring failed: {e}")
            return ToolResult(
                success=False, output=None, error_message=str(e), exit_code=1
            )


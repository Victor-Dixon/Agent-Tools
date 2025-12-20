"""
System Tools - Agent Toolbelt V2
=================================

System utilities including date/time sync and check-in system.

Author: Agent-4 (Captain)
Date: 2025-01-27
V2 Compliance: <300 lines per tool
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from ..adapters.base_adapter import IToolAdapter, ToolResult
from ..core.tool_spec import ToolSpec

logger = logging.getLogger(__name__)


class SystemDateTimeTool(IToolAdapter):
    """Get correct date and time from computer."""

    def get_name(self) -> str:
        return "system.datetime"

    def get_description(self) -> str:
        return "Get current date and time from system (for synchronization)"

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="system.datetime",
            version="1.0.0",
            category="system",
            summary="Get system date/time",
            required_params=[],
            optional_params={"format": "iso"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Get system date/time."""
        try:
            format_type = params.get("format", "iso")
            current_time = datetime.now()

            if format_type == "iso":
                time_str = current_time.isoformat()
            elif format_type == "timestamp":
                time_str = str(time.time())
            elif format_type == "readable":
                time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            else:
                time_str = current_time.isoformat()

            output = {
                "datetime": time_str,
                "timestamp": time.time(),
                "iso": current_time.isoformat(),
                "readable": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "timezone": str(current_time.astimezone().tzinfo),
            }

            return ToolResult(success=True, output=output)

        except Exception as e:
            logger.error(f"System datetime failed: {e}")
            return ToolResult(
                success=False, output=None, error_message=str(e), exit_code=1
            )


class CheckInSystemTool(IToolAdapter):
    """Agent check-in system."""

    def get_name(self) -> str:
        return "system.checkin"

    def get_description(self) -> str:
        return "Check-in system for agents (track presence and activity)"

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="system.checkin",
            version="1.0.0",
            category="system",
            summary="Agent check-in",
            required_params=["agent_id"],
            optional_params={"status": "active", "note": None},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        if not params.get("agent_id"):
            return (False, ["agent_id is required"])
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Agent check-in."""
        try:
            agent_id = params["agent_id"]
            status = params.get("status", "active")
            note = params.get("note")

            # Get system time
            dt_tool = SystemDateTimeTool()
            dt_result = dt_tool.execute({})

            if not dt_result.success:
                return ToolResult(
                    success=False,
                    output=None,
                    error_message="Failed to get system time",
                    exit_code=1,
                )

            checkin_data = {
                "agent_id": agent_id,
                "status": status,
                "timestamp": dt_result.output["iso"],
                "note": note,
            }

            # Save check-in
            checkin_file = Path("data") / "checkins" / f"{agent_id}_checkins.json"
            checkin_file.parent.mkdir(parents=True, exist_ok=True)

            checkins = []
            if checkin_file.exists():
                try:
                    checkins = json.loads(checkin_file.read_text())
                except Exception:
                    pass

            checkins.append(checkin_data)

            # Keep last 100 check-ins
            checkins = checkins[-100:]

            checkin_file.write_text(json.dumps(checkins, indent=2))

            output = {
                "checkin": checkin_data,
                "total_checkins": len(checkins),
                "message": f"✅ {agent_id} checked in as {status}",
            }

            return ToolResult(success=True, output=output)

        except Exception as e:
            logger.error(f"Check-in failed: {e}")
            return ToolResult(
                success=False, output=None, error_message=str(e), exit_code=1
            )


class CheckInViewerTool(IToolAdapter):
    """View check-in history."""

    def get_name(self) -> str:
        return "system.checkin.view"

    def get_description(self) -> str:
        return "View check-in history for agents"

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="system.checkin.view",
            version="1.0.0",
            category="system",
            summary="View check-ins",
            required_params=[],
            optional_params={"agent_id": None, "limit": 50},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """View check-ins."""
        try:
            agent_id = params.get("agent_id")
            limit = params.get("limit", 50)

            checkin_dir = Path("data") / "checkins"
            if not checkin_dir.exists():
                return ToolResult(success=True, output={"checkins": [], "total": 0})

            all_checkins = []

            if agent_id:
                # Single agent
                checkin_file = checkin_dir / f"{agent_id}_checkins.json"
                if checkin_file.exists():
                    try:
                        checkins = json.loads(checkin_file.read_text())
                        all_checkins.extend(checkins)
                    except Exception:
                        pass
            else:
                # All agents
                for checkin_file in checkin_dir.glob("*_checkins.json"):
                    try:
                        checkins = json.loads(checkin_file.read_text())
                        all_checkins.extend(checkins)
                    except Exception:
                        pass

            # Sort by timestamp
            all_checkins.sort(
                key=lambda x: x.get("timestamp", ""), reverse=True
            )

            output = {
                "checkins": all_checkins[:limit],
                "total": len(all_checkins),
                "filter": {"agent_id": agent_id, "limit": limit},
            }

            return ToolResult(success=True, output=output)

        except Exception as e:
            logger.error(f"Check-in viewing failed: {e}")
            return ToolResult(
                success=False, output=None, error_message=str(e), exit_code=1
            )


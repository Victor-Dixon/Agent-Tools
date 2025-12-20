"""
Captain Operations Tools - Utilities
=====================================

Utility tools for captain operations (idle detection, gas checking, logging).

V2 Compliance: <400 lines
Author: Agent-2 (Architecture & Design) - 2025-01-27
Split from captain_tools_extension.py (986 lines → 4 files)
ArchitecturalCheckerTool moved to captain_tools_architecture.py
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)

# Swarm agents list
SWARM_AGENTS = [f"Agent-{i}" for i in range(1, 9)]


class FindIdleAgentsTool(IToolAdapter):
    """Find agents that are idle or need new tasks."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.find_idle",
            version="1.0.0",
            category="captain",
            summary="Find agents that are idle or need new tasks",
            required_params=[],
            optional_params={"hours_threshold": 1},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Find idle agents."""
        try:
            hours_threshold = params.get("hours_threshold", 1)

            idle_agents = []
            active_agents = []

            for agent_id in SWARM_AGENTS:
                status_file = Path(f"agent_workspaces/{agent_id}/status.json")

                if not status_file.exists():
                    idle_agents.append(
                        {"agent": agent_id, "reason": "No status.json", "urgency": "HIGH"}
                    )
                    continue

                try:
                    with open(status_file) as f:
                        status = json.load(f)

                    current_task = status.get("current_task", "")
                    agent_status = status.get("status", "").lower()

                    # Check if idle
                    if not current_task or current_task == "None" or "idle" in agent_status:
                        idle_agents.append(
                            {
                                "agent": agent_id,
                                "reason": f"Status: {agent_status}, Task: {current_task}",
                                "urgency": "HIGH",
                            }
                        )
                    else:
                        active_agents.append(agent_id)

                except Exception as e:
                    idle_agents.append(
                        {"agent": agent_id, "reason": f"Error: {e}", "urgency": "MEDIUM"}
                    )

            return ToolResult(
                success=True,
                output={
                    "idle_agents": idle_agents,
                    "active_agents": active_agents,
                    "idle_count": len(idle_agents),
                    "active_count": len(active_agents),
                    "total_agents": len(SWARM_AGENTS),
                },
                exit_code=0,
                execution_time=0.0,
            )
        except Exception as e:
            logger.error(f"Error finding idle agents: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.find_idle")


class GasCheckTool(IToolAdapter):
    """Check when agents last received messages (GAS levels)."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.gas_check",
            version="1.0.0",
            category="captain",
            summary="Check when agents last received messages (GAS levels)",
            required_params=[],
            optional_params={"hours_threshold": 2},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Check agent gas levels."""
        try:
            hours_threshold = params.get("hours_threshold", 2)

            low_gas = []
            good_gas = []
            gas_levels = {}

            for agent_id in SWARM_AGENTS:
                inbox_path = Path(f"agent_workspaces/{agent_id}/inbox")

                if not inbox_path.exists():
                    low_gas.append(agent_id)
                    gas_levels[agent_id] = {"status": "NO_INBOX", "age_hours": None}
                    continue

                # Find most recent message
                message_files = list(inbox_path.glob("*.md")) + list(inbox_path.glob("*.txt"))

                if not message_files:
                    low_gas.append(agent_id)
                    gas_levels[agent_id] = {"status": "EMPTY_INBOX", "age_hours": None}
                    continue

                # Get most recent
                most_recent = max(message_files, key=lambda p: p.stat().st_mtime)
                modified_time = datetime.fromtimestamp(most_recent.st_mtime)
                age_hours = (datetime.now() - modified_time).total_seconds() / 3600

                gas_levels[agent_id] = {
                    "status": "GOOD" if age_hours <= hours_threshold else "LOW",
                    "age_hours": round(age_hours, 1),
                    "last_message": most_recent.name,
                }

                if age_hours > hours_threshold:
                    low_gas.append(agent_id)
                else:
                    good_gas.append(agent_id)

            return ToolResult(
                success=True,
                output={
                    "low_gas_agents": low_gas,
                    "good_gas_agents": good_gas,
                    "low_gas_count": len(low_gas),
                    "good_gas_count": len(good_gas),
                    "gas_levels": gas_levels,
                    "threshold_hours": hours_threshold,
                },
                exit_code=0,
                execution_time=0.0,
            )
        except Exception as e:
            logger.error(f"Error checking gas levels: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.gas_check")


class UpdateLogTool(IToolAdapter):
    """Update Captain's log with key events."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.update_log",
            version="1.0.0",
            category="captain",
            summary="Update Captain's log with key events",
            required_params=["cycle", "event"],
            optional_params={"points": 0, "agent": None},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        errors = []
        if "cycle" not in params:
            errors.append("cycle is required")
        if "event" not in params:
            errors.append("event is required")
        return len(errors) == 0, errors

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Update Captain's log."""
        try:
            cycle = params["cycle"]
            event = params["event"]
            points = params.get("points", 0)
            agent = params.get("agent")

            log_file = Path(f"agent_workspaces/Agent-4/CAPTAINS_LOG_CYCLE_{cycle:03d}.md")
            timestamp = datetime.now().strftime("%H:%M:%S")

            entry = f"\n## [{timestamp}] {event}\n"
            if agent:
                entry += f"**Agent**: {agent}\n"
            if points > 0:
                entry += f"**Points**: {points}\n"
            entry += f"**Logged**: {datetime.now().isoformat()}\n"

            if log_file.exists():
                with open(log_file, "a") as f:
                    f.write(entry)
            else:
                log_file.parent.mkdir(parents=True, exist_ok=True)
                with open(log_file, "w") as f:
                    f.write(f"# 📓 CAPTAIN'S LOG - CYCLE {cycle:03d}\n")
                    f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d')}\n")
                    f.write("**Captain**: Agent-4\n\n")
                    f.write(entry)

            return ToolResult(
                success=True,
                output={
                    "log_file": str(log_file),
                    "cycle": cycle,
                    "event": event,
                    "entry": entry,
                    "created": not log_file.exists() or log_file.stat().st_size == len(entry),
                },
                exit_code=0,
                execution_time=0.0,
            )
        except Exception as e:
            logger.error(f"Error updating log: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.update_log")


# Import ArchitecturalCheckerTool from separate file (moved for V2 compliance)
from .captain_tools_architecture import ArchitecturalCheckerTool


class ToolbeltHelpTool(IToolAdapter):
    """Display Captain's toolbelt quick reference."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.toolbelt_help",
            version="1.0.0",
            category="captain",
            summary="Display Captain's toolbelt quick reference",
            required_params=[],
            optional_params={"category": None},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return True, []

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Display toolbelt help."""
        try:
            tools_info = {
                "Message All Agents": {
                    "tool": "msg.broadcast",
                    "when": "Need to activate all 8 agents at once",
                    "key": "Don't forget to include Agent-4 (Captain)!",
                },
                "Check Agent Status": {
                    "tool": "captain.status_check",
                    "when": "Want to see who's active vs idle",
                    "key": "Idle = needs tasks!",
                },
                "ROI Calculator": {
                    "tool": "captain.calculate_roi",
                    "when": "Need to calculate task ROI quickly",
                    "key": "ROI = (points + v2*100 + autonomy*200) / complexity",
                },
                "Update Log": {
                    "tool": "captain.update_log",
                    "when": "Quick log entry needed",
                    "key": "Keeps audit trail current",
                },
            }

            help_text = "\n🛠️  CAPTAIN'S TOOLBELT - QUICK REFERENCE\n"
            help_text += "=" * 80 + "\n\n"

            for name, info in tools_info.items():
                help_text += f"- {name} ({info['tool']})\n"
                help_text += f"  When: {info['when']}\n"
                help_text += f"  Key: {info['key']}\n\n"

            help_text += "=" * 80 + "\n"
            help_text += "⛽ REMEMBER: 'Prompts are gas for ALL agents - including Captain!'\n"
            help_text += "🐝 WE. ARE. SWARM. ⚡\n"
            help_text += "=" * 80 + "\n"

            return ToolResult(
                success=True,
                output={
                    "help_text": help_text,
                    "tools_count": len(tools_info),
                    "tools": list(tools_info.keys()),
                },
                exit_code=0,
                execution_time=0.0,
            )
        except Exception as e:
            logger.error(f"Error displaying help: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.toolbelt_help")


# Import ArchitecturalCheckerTool from separate file
from .captain_tools_architecture import ArchitecturalCheckerTool

# Export all tools
__all__ = [
    "FindIdleAgentsTool",
    "GasCheckTool",
    "UpdateLogTool",
    "ArchitecturalCheckerTool",
    "ToolbeltHelpTool",
]


"""
Captain Monitoring Operations Tools
====================================

Monitoring tool adapters for Captain operations: gas delivery,
leaderboard updates, and cycle reporting.

V2 Compliance: <300 lines
Author: Agent-4 (Captain) - Refactored 2025-01-27
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class GasDeliveryTool(IToolAdapter):
    """Send PyAutoGUI activation messages to agents ("Prompts Are Gas")."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.deliver_gas",
            version="1.0.0",
            category="captain",
            summary="Send PyAutoGUI activation message to agent",
            required_params=["agent_id", "message"],
            optional_params={"priority": "regular"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute gas delivery (PyAutoGUI message)."""
        try:
            agent_id = params["agent_id"]
            message = params["message"]
            priority = params.get("priority", "regular")

            # Use messaging_cli to send PyAutoGUI message
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
                "--pyautogui",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())

            if result.returncode != 0:
                return ToolResult(
                    success=False,
                    output={"error": result.stderr},
                    exit_code=result.returncode,
                    error_message=f"Gas delivery failed: {result.stderr}",
                )

            return ToolResult(
                success=True,
                output={
                    "agent_id": agent_id,
                    "message_sent": True,
                    "delivery_method": "PyAutoGUI",
                    "gas_type": "activation",
                    "stdout": result.stdout,
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error delivering gas: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.deliver_gas")


class LeaderboardUpdateTool(IToolAdapter):
    """
    Update agent leaderboard with new points, achievements, and session tracking.
    
    Consolidated from captain_tools.py and captain_coordination_tools.py (Agent-8 - 2025-01-27)
    Single source of truth for all leaderboard operations.
    """

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.update_leaderboard",
            version="2.0.0",
            category="captain",
            summary="Update agent leaderboard with points, achievements, and session tracking",
            required_params=[],
            optional_params={
                "updates": {},  # Dict: {agent_id: points} - batch update mode
                "agent_id": None,  # Single agent update mode
                "points": 0,  # Points to add (single agent mode)
                "achievement": None,  # Achievement name (optional)
                "session_date": None,  # Session date (defaults to today)
            },
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        # Either batch mode (updates dict) or single agent mode (agent_id + points)
        has_batch = "updates" in params and params["updates"]
        has_single = "agent_id" in params and params["agent_id"] and "points" in params

        if not has_batch and not has_single:
            return (False, ["Either 'updates' dict or 'agent_id' + 'points' required"])

        return (True, [])

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute leaderboard update."""
        try:
            session_date = params.get("session_date", datetime.now().strftime("%Y-%m-%d"))
            leaderboard_file = Path("runtime/leaderboard.json")
            leaderboard_file.parent.mkdir(parents=True, exist_ok=True)

            # Load existing leaderboard
            if leaderboard_file.exists():
                leaderboard = json.loads(leaderboard_file.read_text())
            else:
                leaderboard = {"version": "2.0.0", "last_updated": session_date, "agents": {}}

            updates_applied = 0

            # Batch update mode
            if "updates" in params and params["updates"]:
                updates = params["updates"]
                for agent_id, points in updates.items():
                    self._update_agent_entry(leaderboard, agent_id, points, session_date, None)
                    updates_applied += 1

            # Single agent update mode
            elif "agent_id" in params and params["agent_id"]:
                agent_id = params["agent_id"]
                points = params.get("points", 0)
                achievement = params.get("achievement")
                self._update_agent_entry(leaderboard, agent_id, points, session_date, achievement)
                updates_applied += 1

            # Sort by total points
            sorted_agents = sorted(
                leaderboard["agents"].items(), key=lambda x: x[1]["total_points"], reverse=True
            )

            leaderboard["last_updated"] = session_date
            leaderboard["ranking"] = [agent_id for agent_id, _ in sorted_agents]

            # Save leaderboard
            leaderboard_file.write_text(json.dumps(leaderboard, indent=2))

            return ToolResult(
                success=True,
                output={
                    "leaderboard_file": str(leaderboard_file),
                    "updates_applied": updates_applied,
                    "ranking": leaderboard["ranking"][:5],  # Top 5
                    "last_updated": session_date,
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error updating leaderboard: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.update_leaderboard")

    def _update_agent_entry(
        self, leaderboard: dict, agent_id: str, points: int, session_date: str, achievement: str | None
    ):
        """Update individual agent entry in leaderboard."""
        if agent_id not in leaderboard["agents"]:
            leaderboard["agents"][agent_id] = {
                "total_points": 0,
                "sessions": [],
                "achievements": [],
            }

        # Update points
        leaderboard["agents"][agent_id]["total_points"] += points

        # Add session tracking
        if "sessions" not in leaderboard["agents"][agent_id]:
            leaderboard["agents"][agent_id]["sessions"] = []

        leaderboard["agents"][agent_id]["sessions"].append(
            {"date": session_date, "points": points}
        )

        # Add achievement if provided
        if achievement:
            if "achievements" not in leaderboard["agents"][agent_id]:
                leaderboard["agents"][agent_id]["achievements"] = []

            leaderboard["agents"][agent_id]["achievements"].append(
                {
                    "achievement": achievement,
                    "points": points,
                    "timestamp": datetime.now().isoformat(),
                }
            )


class CycleReportTool(IToolAdapter):
    """Generate Captain's cycle report."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.cycle_report",
            version="1.0.0",
            category="captain",
            summary="Generate Captain's cycle activity report",
            required_params=["cycle_number"],
            optional_params={
                "missions_assigned": 0,
                "messages_sent": 0,
                "agents_activated": [],
                "points_awarded": 0,
                "notes": "",
            },
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute cycle report generation."""
        try:
            cycle_num = params["cycle_number"]
            missions = params.get("missions_assigned", 0)
            messages = params.get("messages_sent", 0)
            agents = params.get("agents_activated", [])
            points = params.get("points_awarded", 0)
            notes = params.get("notes", "")

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            report_file = Path(f"agent_workspaces/Agent-4/CAPTAIN_CYCLE_{cycle_num}_{timestamp}.md")
            report_file.parent.mkdir(parents=True, exist_ok=True)

            content = f"""# 🎯 CAPTAIN'S CYCLE REPORT #{cycle_num}

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Cycle:** {cycle_num}

---

## 📊 CYCLE METRICS

- **Missions Assigned:** {missions}
- **Messages Sent:** {messages}
- **Agents Activated:** {len(agents)}
- **Points Awarded:** {points}

---

## 🤖 AGENTS ACTIVATED

{chr(10).join(f'- {agent}' for agent in agents) if agents else 'None this cycle'}

---

## 📝 CYCLE NOTES

{notes if notes else 'No additional notes this cycle.'}

---

## 🎯 NEXT CYCLE PRIORITIES

- Monitor agent progress
- Check for idle agents
- Review completed work
- Update leaderboard

---

**🐝 WE. ARE. SWARM.** ⚡🔥
"""

            report_file.write_text(content, encoding="utf-8")

            return ToolResult(
                success=True,
                output={
                    "cycle_number": cycle_num,
                    "report_file": str(report_file),
                    "missions_assigned": missions,
                    "messages_sent": messages,
                    "agents_activated": agents,
                    "points_awarded": points,
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error generating cycle report: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.cycle_report")


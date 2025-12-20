#!/usr/bin/env python3
"""
Captain Coordination Tools - Agent Toolbelt V2
================================================

Coordination and reporting tools for captain operations.

V2 Compliance: <400 lines
Author: Agent-2 (Architecture & Design) - Split from captain_tools_advanced.py
Date: 2025-01-27
"""

import json
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)

# Swarm agents list
SWARM_AGENTS = [f"Agent-{i}" for i in range(1, 9)]


class MultiFuelDelivery(IToolAdapter):
    """Send fuel (gas) to multiple agents at once."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.multi_fuel",
            version="1.0.0",
            category="captain",
            summary="Send activation messages to multiple agents at once",
            required_params=["agent_ids", "message"],
            optional_params={"priority": "regular", "use_pyautogui": True},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute multi-agent fuel delivery."""
        try:
            agent_ids = params["agent_ids"]
            message = params["message"]
            priority = params.get("priority", "regular")
            use_pyautogui = params.get("use_pyautogui", True)

            delivery_results = {}
            success_count = 0

            for agent_id in agent_ids:
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
                ]

                if use_pyautogui:
                    cmd.append("--pyautogui")

                result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())

                delivery_results[agent_id] = {"success": result.returncode == 0}
                if result.returncode == 0:
                    success_count += 1

            return ToolResult(
                success=success_count > 0,
                output={
                    "agents_targeted": len(agent_ids),
                    "deliveries_successful": success_count,
                    "success_rate": (
                        round((success_count / len(agent_ids)) * 100, 2) if agent_ids else 0
                    ),
                    "delivery_results": delivery_results,
                },
                exit_code=0 if success_count == len(agent_ids) else 1,
            )
        except Exception as e:
            logger.error(f"Error delivering multi-agent fuel: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.multi_fuel")


class MarkovROIRunner(IToolAdapter):
    """Run Markov ROI optimizer and return optimal assignments."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.markov_roi",
            version="1.0.0",
            category="captain",
            summary="Execute Markov ROI optimizer for optimal task assignments",
            required_params=[],
            optional_params={"agent_count": 8},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute Markov ROI optimization."""
        try:
            result = subprocess.run(
                ["python", "tools/markov_8agent_roi_optimizer.py"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

            markov_output = {"optimization_completed": result.returncode == 0}

            # Load results
            results_file = Path("agent_workspaces/Agent-4/8agent_roi_assignments.json")
            if results_file.exists():
                with open(results_file) as f:
                    assignments = json.load(f)
                    markov_output.update(
                        {
                            "total_agents": assignments.get("total_agents", 0),
                            "total_points": assignments.get("total_points", 0),
                            "avg_roi": assignments.get("avg_roi", 0),
                            "top_3_tasks": assignments.get("assignments", [])[:3],
                        }
                    )

            return ToolResult(
                success=result.returncode == 0, output=markov_output, exit_code=result.returncode
            )
        except Exception as e:
            logger.error(f"Error running Markov ROI: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.markov_roi")


class SwarmStatusDashboard(IToolAdapter):
    """Generate comprehensive swarm status dashboard."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="captain.swarm_status",
            version="1.0.0",
            category="captain",
            summary="Generate swarm status overview",
            required_params=[],
            optional_params={},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute swarm dashboard generation."""
        try:
            dashboard = {"timestamp": datetime.now().isoformat(), "agents": {}, "active_count": 0}

            for agent_id in SWARM_AGENTS:
                workspace = Path(f"agent_workspaces/{agent_id}")
                if workspace.exists():
                    status_file = workspace / "status.json"
                    if status_file.exists():
                        status = json.loads(status_file.read_text())
                        dashboard["agents"][agent_id] = {
                            "status": status.get("status", "UNKNOWN"),
                            "mission": status.get("current_mission"),
                        }
                        if status.get("status") in ["ACTIVE", "EXECUTING"]:
                            dashboard["active_count"] += 1

            dashboard["swarm_health"] = "EXCELLENT" if dashboard["active_count"] >= 5 else "GOOD"
            return ToolResult(success=True, output=dashboard, exit_code=0)
        except Exception as e:
            raise ToolExecutionError(str(e), tool_name="captain.swarm_status")


class MorningBriefingTool(IToolAdapter):
    """Generate Captain's morning briefing with swarm status and priorities."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.morning_briefing",
            version="1.0.0",
            category="captain",
            summary="Generate Captain's morning briefing with swarm status",
            required_params=[],
            optional_params={"output_file": None, "detailed": True},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute morning briefing generation."""
        try:
            output_file = params.get("output_file")
            detailed = params.get("detailed", True)

            briefing = {
                "timestamp": datetime.now().isoformat(),
                "agents": {},
                "active_count": 0,
                "idle_count": 0,
                "recent_completions": [],
                "pending_tasks": [],
            }

            # Get agent status
            for agent_id in SWARM_AGENTS:
                workspace = Path(f"agent_workspaces/{agent_id}")
                if workspace.exists():
                    inbox = workspace / "inbox"
                    if inbox.exists():
                        messages = list(inbox.glob("*.md"))
                        if messages:
                            latest = max(messages, key=lambda p: p.stat().st_mtime)
                            last_activity = datetime.fromtimestamp(latest.stat().st_mtime)
                            minutes_ago = (datetime.now() - last_activity).total_seconds() / 60

                            status = "active" if minutes_ago < 60 else "idle"
                            briefing["agents"][agent_id] = {
                                "status": status,
                                "last_activity": last_activity.isoformat(),
                                "minutes_ago": round(minutes_ago, 1),
                            }

                            if status == "active":
                                briefing["active_count"] += 1
                            else:
                                briefing["idle_count"] += 1

            # Get recent completions (last 24 hours)
            for agent_dir in Path("agent_workspaces").iterdir():
                if not agent_dir.is_dir():
                    continue

                inbox = agent_dir / "inbox"
                if inbox.exists():
                    for msg_file in inbox.glob("*.md"):
                        mtime = datetime.fromtimestamp(msg_file.stat().st_mtime)
                        if (datetime.now() - mtime) < timedelta(hours=24):
                            content = msg_file.read_text(encoding="utf-8", errors="ignore")
                            if "COMPLETE" in content.upper() or "DONE" in content.upper():
                                briefing["recent_completions"].append(
                                    {
                                        "agent": agent_dir.name,
                                        "file": msg_file.name,
                                        "time": mtime.isoformat(),
                                    }
                                )

            # Get pending tasks
            for agent_dir in Path("agent_workspaces").iterdir():
                if not agent_dir.is_dir():
                    continue

                for order_file in agent_dir.glob("*EXECUTION_ORDER*.md"):
                    mtime = datetime.fromtimestamp(order_file.stat().st_mtime)
                    briefing["pending_tasks"].append(
                        {
                            "agent": agent_dir.name,
                            "file": order_file.name,
                            "assigned": mtime.isoformat(),
                            "age_hours": round((datetime.now() - mtime).total_seconds() / 3600, 1),
                        }
                    )

            # Sort completions and tasks
            briefing["recent_completions"].sort(key=lambda x: x["time"], reverse=True)
            briefing["pending_tasks"].sort(key=lambda x: x["assigned"], reverse=True)

            # Generate markdown if output file specified
            if output_file:
                self._generate_markdown_briefing(briefing, Path(output_file))

            return ToolResult(
                success=True,
                output={
                    "briefing": briefing,
                    "summary": {
                        "active_agents": briefing["active_count"],
                        "idle_agents": briefing["idle_count"],
                        "recent_completions": len(briefing["recent_completions"]),
                        "pending_tasks": len(briefing["pending_tasks"]),
                    },
                    "output_file": output_file,
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error generating morning briefing: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.morning_briefing")

    def _generate_markdown_briefing(self, briefing: dict, output_file: Path):
        """Generate markdown briefing file."""
        output_file.parent.mkdir(parents=True, exist_ok=True)

        content = f"# ☀️ CAPTAIN'S MORNING BRIEFING\n\n"
        content += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += f"## 🤖 AGENT STATUS\n\n"
        content += f"**Active:** {briefing['active_count']}/8  |  **Idle:** {briefing['idle_count']}/8\n\n"

        for agent_id, info in briefing["agents"].items():
            emoji = "🟢" if info["status"] == "active" else "🟡"
            content += f"{emoji} **{agent_id}**: {info['status'].upper()} "
            content += f"(last activity: {info['minutes_ago']:.0f}m ago)\n"

        content += f"\n## ✅ RECENT COMPLETIONS (Last 24h)\n\n"
        for comp in briefing["recent_completions"][:5]:
            content += f"- **{comp['agent']}**: {comp['file']}\n"

        content += f"\n## 📋 PENDING TASKS\n\n"
        for task in briefing["pending_tasks"][:5]:
            content += f"- **{task['agent']}**: {task['file']} ({task['age_hours']:.1f}h ago)\n"

        content += f"\n**🐝 WE. ARE. SWARM.** ⚡\n"

        output_file.write_text(content, encoding="utf-8")


__all__ = [
    "MultiFuelDelivery",
    "MarkovROIRunner",
    "SwarmStatusDashboard",
    "MorningBriefingTool",
]





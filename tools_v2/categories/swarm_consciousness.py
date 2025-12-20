"""
Swarm Pulse - Real-Time Swarm Consciousness
============================================

THE MASTERPIECE TOOL: Real-time awareness of entire swarm activity.

This tool provides what messaging/vector DB cannot:
- LIVE view of what every agent is doing RIGHT NOW
- Automatic conflict detection (duplicate work prevention)
- Spontaneous collaboration opportunities
- Instant swarm-wide context awareness
- Captain's real-time command center

Like a nervous system for the swarm - every agent can sense the whole organism.

V2 Compliance: <400 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class SwarmPulseTool(IToolAdapter):
    """Real-time swarm consciousness dashboard."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="swarm.pulse",
            version="1.0.0",
            category="consciousness",
            summary="Real-time view of entire swarm activity (MASTERPIECE TOOL)",
            required_params=[],
            optional_params={
                "mode": "dashboard",  # dashboard, conflicts, related, captain
                "agent_id": None,
                "refresh": False,
            },
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])  # No required params

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute swarm pulse."""
        try:
            mode = params.get("mode", "dashboard")
            agent_id = params.get("agent_id")

            # Collect real-time swarm data
            pulse_data = self._collect_swarm_pulse()

            if mode == "dashboard":
                return self._dashboard_view(pulse_data, agent_id)
            elif mode == "conflicts":
                return self._detect_conflicts(pulse_data)
            elif mode == "related":
                return self._find_related_work(pulse_data, agent_id)
            elif mode == "captain":
                return self._captain_command_center(pulse_data)
            else:
                raise ToolExecutionError(f"Invalid mode: {mode}", tool_name="swarm.pulse")

        except Exception as e:
            logger.error(f"Error in swarm pulse: {e}")
            raise ToolExecutionError(str(e), tool_name="swarm.pulse")

    def _collect_swarm_pulse(self) -> dict:
        """Collect real-time data from all agents."""
        pulse = {
            "timestamp": datetime.now().isoformat(),
            "agents": {},
            "active_count": 0,
            "tasks_in_progress": [],
            "recent_activity": [],
        }

        # Scan all agent workspaces
        workspaces = Path("agent_workspaces")
        if not workspaces.exists():
            return pulse

        for agent_dir in workspaces.glob("Agent-*"):
            agent_id = agent_dir.name
            agent_data = self._get_agent_pulse(agent_dir)

            if agent_data:
                pulse["agents"][agent_id] = agent_data

                if agent_data["status"] == "active":
                    pulse["active_count"] += 1

                if agent_data["current_task"]:
                    pulse["tasks_in_progress"].append(
                        {
                            "agent": agent_id,
                            "task": agent_data["current_task"],
                            "started": agent_data["task_started"],
                            "elapsed": agent_data["task_elapsed"],
                        }
                    )

        return pulse

    def _get_agent_pulse(self, agent_dir: Path) -> dict | None:
        """Get pulse data for single agent."""
        status_file = agent_dir / "status.json"
        inbox_dir = agent_dir / "inbox"

        if not status_file.exists():
            return None

        try:
            status = json.loads(status_file.read_text())

            # Determine if agent is active (recent file changes)
            last_modified = status_file.stat().st_mtime
            idle_minutes = (time.time() - last_modified) / 60

            is_active = idle_minutes < 15  # Active if modified in last 15 min

            # Extract current task
            current_task = None
            task_started = None

            # Check inbox for recent assignments
            if inbox_dir.exists():
                recent_messages = sorted(
                    inbox_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True
                )

                if recent_messages:
                    latest = recent_messages[0]
                    msg_age = (time.time() - latest.stat().st_mtime) / 60

                    if msg_age < 60:  # Message from last hour
                        content = latest.read_text()
                        # Extract task from message (simple parsing)
                        if "MISSION" in content or "TASK" in content:
                            lines = content.split("\n")
                            for line in lines:
                                if "MISSION" in line or "TASK" in line:
                                    current_task = line.strip()[:100]
                                    task_started = datetime.fromtimestamp(
                                        latest.stat().st_mtime
                                    ).isoformat()
                                    break

            # Calculate task elapsed time
            task_elapsed = None
            if task_started:
                started_dt = datetime.fromisoformat(task_started)
                elapsed = datetime.now() - started_dt
                task_elapsed = str(elapsed).split(".")[0]  # Format: H:MM:SS

            return {
                "status": "active" if is_active else "idle",
                "idle_minutes": round(idle_minutes, 1),
                "current_task": current_task,
                "task_started": task_started,
                "task_elapsed": task_elapsed,
                "role": status.get("current_role", "Unknown"),
                "points": status.get("total_points", 0),
                "inbox_count": len(list(inbox_dir.glob("*.md"))) if inbox_dir.exists() else 0,
                "last_activity": datetime.fromtimestamp(last_modified).isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting pulse for {agent_dir.name}: {e}")
            return None

    def _dashboard_view(self, pulse: dict, requesting_agent: str | None) -> ToolResult:
        """Generate dashboard view of swarm activity."""
        output = {
            "swarm_pulse": {
                "timestamp": pulse["timestamp"],
                "total_agents": len(pulse["agents"]),
                "active_agents": pulse["active_count"],
                "idle_agents": len(pulse["agents"]) - pulse["active_count"],
                "tasks_in_progress": len(pulse["tasks_in_progress"]),
            },
            "live_activity": [],
            "agent_details": {},
        }

        # Sort agents by activity (active first, then by recent activity)
        sorted_agents = sorted(
            pulse["agents"].items(),
            key=lambda x: (x[1]["status"] != "active", -x[1]["idle_minutes"]),
        )

        for agent_id, data in sorted_agents:
            activity_emoji = "🟢" if data["status"] == "active" else "⚫"

            activity_summary = {
                "agent": agent_id,
                "status": f"{activity_emoji} {data['status'].upper()}",
                "role": data["role"],
                "current_task": data["current_task"] or "No active task",
                "task_duration": data["task_elapsed"] or "N/A",
                "points": data["points"],
                "inbox": data["inbox_count"],
                "idle_time": f"{data['idle_minutes']}m",
            }

            output["live_activity"].append(activity_summary)
            output["agent_details"][agent_id] = data

        # Add conflict warnings
        conflicts = self._detect_conflicts(pulse)
        if conflicts.output.get("conflicts"):
            output["warnings"] = conflicts.output["conflicts"]

        return ToolResult(success=True, output=output, exit_code=0)

    def _detect_conflicts(self, pulse: dict) -> ToolResult:
        """Detect potential work conflicts (duplicate efforts)."""
        conflicts = []

        # Group tasks by similarity
        tasks = pulse["tasks_in_progress"]

        for i, task1 in enumerate(tasks):
            for task2 in tasks[i + 1 :]:
                # Simple similarity check (keyword overlap)
                task1_words = set(task1["task"].lower().split())
                task2_words = set(task2["task"].lower().split())

                overlap = task1_words & task2_words
                if len(overlap) >= 2:  # 2+ shared keywords
                    conflicts.append(
                        {
                            "type": "potential_duplicate",
                            "severity": "warning",
                            "agent1": task1["agent"],
                            "agent2": task2["agent"],
                            "task1": task1["task"],
                            "task2": task2["task"],
                            "shared_keywords": list(overlap),
                        }
                    )

        return ToolResult(
            success=True,
            output={"conflicts_detected": len(conflicts), "conflicts": conflicts},
            exit_code=0,
        )

    def _find_related_work(self, pulse: dict, agent_id: str | None) -> ToolResult:
        """Find agents working on related tasks."""
        if not agent_id or agent_id not in pulse["agents"]:
            return ToolResult(
                success=False,
                output={"error": "Agent ID required for related work search"},
                exit_code=1,
            )

        my_task = pulse["agents"][agent_id].get("current_task")
        if not my_task:
            return ToolResult(
                success=True,
                output={"message": "No current task to compare", "related_agents": []},
                exit_code=0,
            )

        # Find related work
        my_keywords = set(my_task.lower().split())
        related = []

        for task in pulse["tasks_in_progress"]:
            if task["agent"] == agent_id:
                continue  # Skip self

            task_keywords = set(task["task"].lower().split())
            overlap = my_keywords & task_keywords

            if len(overlap) >= 1:  # Any shared keyword
                related.append(
                    {
                        "agent": task["agent"],
                        "task": task["task"],
                        "relevance": len(overlap),
                        "shared_keywords": list(overlap),
                        "collaboration_opportunity": len(overlap) >= 2,
                    }
                )

        # Sort by relevance
        related.sort(key=lambda x: x["relevance"], reverse=True)

        return ToolResult(
            success=True,
            output={
                "my_task": my_task,
                "related_agents": related,
                "collaboration_opportunities": sum(
                    1 for r in related if r["collaboration_opportunity"]
                ),
            },
            exit_code=0,
        )

    def _captain_command_center(self, pulse: dict) -> ToolResult:
        """Captain's real-time command center view."""
        # Strategic overview
        overview = {
            "swarm_health": {
                "total_agents": len(pulse["agents"]),
                "active": pulse["active_count"],
                "idle": len(pulse["agents"]) - pulse["active_count"],
                "utilization": f"{(pulse['active_count'] / max(len(pulse['agents']), 1)) * 100:.1f}%",
            },
            "workload_distribution": {},
            "bottlenecks": [],
            "opportunities": [],
        }

        # Analyze workload
        for agent_id, data in pulse["agents"].items():
            overview["workload_distribution"][agent_id] = {
                "status": data["status"],
                "task": data["current_task"],
                "inbox": data["inbox_count"],
                "capacity": "busy" if data["status"] == "active" else "available",
            }

        # Detect bottlenecks
        for agent_id, data in pulse["agents"].items():
            if data["inbox_count"] > 5:
                overview["bottlenecks"].append(
                    {
                        "agent": agent_id,
                        "issue": "High inbox count",
                        "inbox_count": data["inbox_count"],
                        "recommendation": "Consider redistributing tasks",
                    }
                )

            if data["status"] == "active" and data["task_elapsed"]:
                # Parse elapsed time
                elapsed = data["task_elapsed"]
                if ":" in elapsed:
                    hours = int(elapsed.split(":")[0])
                    if hours >= 2:
                        overview["bottlenecks"].append(
                            {
                                "agent": agent_id,
                                "issue": "Long-running task",
                                "duration": elapsed,
                                "task": data["current_task"],
                                "recommendation": "Check for blockers",
                            }
                        )

        # Find collaboration opportunities
        conflicts = self._detect_conflicts(pulse)
        if conflicts.output.get("conflicts"):
            for conflict in conflicts.output["conflicts"]:
                overview["opportunities"].append(
                    {
                        "type": "collaboration",
                        "agents": [conflict["agent1"], conflict["agent2"]],
                        "reason": "Working on similar tasks",
                        "keywords": conflict["shared_keywords"],
                    }
                )

        return ToolResult(success=True, output=overview, exit_code=0)

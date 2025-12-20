#!/usr/bin/env python3
"""
Swarm State Reader - Extracted from Swarm Mission Control
=========================================================

Handles reading and parsing swarm state from all agent workspaces.

Author: Agent-8 (SSOT & System Integration) - Lean Excellence Refactor
License: MIT
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def read_swarm_state() -> dict[str, Any]:
    """Read complete swarm state from all agents."""
    swarm_state = {
        "agents": {},
        "active_missions": [],
        "completed_today": [],
        "total_points": 0,
        "summary": {},
    }

    try:
        # Read all agent status files
        workspace = Path("agent_workspaces")
        for i in range(1, 9):
            agent_id = f"Agent-{i}"
            status_file = workspace / agent_id / "status.json"

            if status_file.exists():
                try:
                    with open(status_file) as f:
                        status = json.load(f)
                        swarm_state["agents"][agent_id] = status

                        # Track active missions
                        mission = status.get("current_mission", "")
                        if mission and "COMPLETE" not in mission.upper():
                            swarm_state["active_missions"].append(
                                {"agent": agent_id, "mission": mission}
                            )

                        # Sum points
                        points = status.get("points_earned", 0)
                        if isinstance(points, (int, float)):
                            swarm_state["total_points"] += points

                except:
                    pass

        swarm_state["summary"] = {
            "total_agents": len(swarm_state["agents"]),
            "active_count": len(swarm_state["active_missions"]),
            "total_points": swarm_state["total_points"],
        }

    except Exception as e:
        logger.error(f"Error reading swarm state: {e}")

    return swarm_state


def read_agent_context(agent_id: str, swarm_state: dict) -> dict[str, Any]:
    """Read agent's specific context."""
    context = {
        "agent_id": agent_id,
        "status": {},
        "inbox_count": 0,
        "inbox_messages": [],
        "recent_completions": [],
        "specialty": get_agent_specialty(agent_id),
    }

    try:
        # Read agent status
        if agent_id in swarm_state["agents"]:
            context["status"] = swarm_state["agents"][agent_id]

        # Read inbox
        inbox_path = Path(f"agent_workspaces/{agent_id}/inbox")
        if inbox_path.exists():
            inbox_files = list(inbox_path.glob("*.md"))
            context["inbox_count"] = len(inbox_files)

            # Read priority messages
            priority_messages = []
            for msg_file in sorted(inbox_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
                try:
                    content = open(msg_file).read()
                    priority_messages.append(
                        {
                            "file": msg_file.name,
                            "preview": content[:200],
                            "modified": datetime.fromtimestamp(
                                msg_file.stat().st_mtime
                            ).isoformat(),
                        }
                    )
                except:
                    pass

            context["inbox_messages"] = priority_messages

    except Exception as e:
        logger.error(f"Error reading agent context: {e}")

    return context


def get_agent_specialty(agent_id: str) -> str:
    """Get agent specialty."""
    specialties = {
        "Agent-1": "Integration & Core Systems",
        "Agent-2": "Architecture & Design",
        "Agent-3": "Infrastructure & DevOps",
        "Agent-4": "Quality Assurance (Captain)",
        "Agent-5": "Business Intelligence",
        "Agent-6": "Coordination & Communication",
        "Agent-7": "Web Development",
        "Agent-8": "Operations & Support",
    }
    return specialties.get(agent_id, "General")


def analyze_available_work(swarm_state: dict) -> list[dict]:
    """Analyze what work is available."""
    available = []

    try:
        # Check project analysis for violations
        if Path("project_analysis.json").exists():
            with open("project_analysis.json") as f:
                analysis = json.load(f)
                # Look for files that need work (this is simplified)
                # Real implementation would parse violations
                available.append(
                    {"type": "v2_compliance", "source": "project_analysis", "count": "multiple"}
                )

        # Check captain's tracking for unassigned work
        captain_docs = Path("agent_workspaces/Agent-4")
        if captain_docs.exists():
            # Look for execution orders or task lists
            for doc in captain_docs.glob("*EXECUTION*.md"):
                available.append({"type": "captain_order", "source": str(doc), "priority": "HIGH"})

    except Exception as e:
        logger.error(f"Error analyzing available work: {e}")

    return available


__all__ = [
    "read_swarm_state",
    "read_agent_context",
    "get_agent_specialty",
    "analyze_available_work",
]

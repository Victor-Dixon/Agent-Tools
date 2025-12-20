#!/usr/bin/env python3
"""
Mission Calculator - Extracted from Swarm Mission Control
=========================================================

Calculates optimal tasks and builds context packages for agents.

Author: Agent-8 (SSOT & System Integration) - Lean Excellence Refactor
License: MIT
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def calculate_optimal_task(
    agent_id: str, agent_context: dict, available_work: list, swarm_state: dict
) -> dict | None:
    """Calculate optimal next task for agent."""

    # Check inbox first (highest priority)
    if agent_context["inbox_count"] > 0:
        inbox_messages = agent_context["inbox_messages"]
        if inbox_messages:
            latest = inbox_messages[0]
            return {
                "type": "inbox_order",
                "priority": "URGENT",
                "source": latest["file"],
                "description": "Check inbox - Captain's orders waiting",
                "roi": 999,  # Highest priority
                "reasoning": f"{agent_context['inbox_count']} messages in inbox",
            }

    # Check for specialty-aligned work
    specialty = agent_context.get("specialty", "")
    if "Infrastructure" in specialty and available_work:
        for work in available_work:
            if "orchestrat" in str(work.get("source", "")).lower():
                return {
                    "type": "specialty_match",
                    "priority": "HIGH",
                    "description": "Infrastructure work matches your specialty",
                    "source": work.get("source"),
                    "roi": 800,
                    "reasoning": "Aligns with Infrastructure & DevOps expertise",
                }

    # No specific task found
    return {
        "type": "scan_for_opportunities",
        "priority": "MEDIUM",
        "description": "Scan project for proactive opportunities",
        "roi": 500,
        "reasoning": "No urgent tasks - proactive mode",
    }


def build_context_package(
    task: dict | None, agent_context: dict, swarm_state: dict
) -> dict[str, Any]:
    """Build complete context package for task execution."""
    if not task:
        return {}

    package = {
        "task_summary": task.get("description", "No task"),
        "priority": task.get("priority", "MEDIUM"),
        "estimated_roi": task.get("roi", 0),
        # Swarm coordination context
        "other_agents_working": [
            {"agent": m["agent"], "mission": m["mission"]} for m in swarm_state["active_missions"]
        ],
        # Agent status
        "your_status": agent_context.get("status", {}),
        # Related files
        "check_these_files": [],
        # Coordination needs
        "coordinate_with": [],
        # Success patterns
        "similar_past_work": [],
    }

    # Add task-specific context
    if task.get("source"):
        package["reference_file"] = task["source"]
        package["check_these_files"].append(task["source"])

    return package


def format_mission_brief(task: dict | None, context: dict) -> str:
    """Format human-readable mission brief."""
    if not task:
        return "No mission identified - Agent appears to be resting"

    brief = f"""
🎯 MISSION BRIEF FOR EXECUTION
================================

RECOMMENDED TASK: {task.get('description', 'Unknown')}
PRIORITY: {task.get('priority', 'MEDIUM')}
ROI: {task.get('roi', 0)}
TYPE: {task.get('type', 'Unknown')}

REASONING: {task.get('reasoning', 'Optimal task for your specialty')}

CONTEXT PROVIDED:
- Swarm state: {len(context.get('other_agents_working', []))} agents active
- Files to check: {len(context.get('check_these_files', []))}
- Coordination needed: {len(context.get('coordinate_with', []))}

READY TO EXECUTE: Yes
================================
"""
    return brief.strip()


__all__ = ["calculate_optimal_task", "build_context_package", "format_mission_brief"]

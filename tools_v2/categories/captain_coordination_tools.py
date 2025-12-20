"""
Captain Coordination Tools - V2 Compliant Category
=================================================

Consolidates scattered captain_* coordination tools into single category.
All tools follow IToolAdapter pattern for consistency.

Migrated from tools/ directory as part of Infrastructure Consolidation Mission.
Lead: Agent-2 (Architecture), Execution: Agent-6 (Co-Captain)
Fixed by: Agent-8 (SSOT & System Integration) - 2025-01-27

Date: 2025-10-15 (original), 2025-01-27 (IToolAdapter conversion)
Status: V2 COMPLIANT - All tools use IToolAdapter pattern
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


class CompletionProcessorTool(IToolAdapter):
    """
    Process agent task completions and update tracking systems.
    
    Migrated from: tools/captain_completion_processor.py
    """

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.process_completion",
            version="1.0.0",
            category="captain.coordination",
            summary="Process agent task completion and award points",
            required_params=["agent_id", "task_id", "result"],
            optional_params={"points": 0},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute completion processing."""
        try:
            agent_id = params["agent_id"]
            task_id = params["task_id"]
            result = params["result"]
            points = params.get("points", 0)

            completion_data = {
                "agent_id": agent_id,
                "task_id": task_id,
                "result": result,
                "points": points,
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
            }

            # Update agent status
            self._update_agent_status(agent_id, task_id, points)

            # Log to swarm brain
            self._log_to_swarm_brain(completion_data)

            return ToolResult(
                success=True,
                output={
                    "completion_id": f"{agent_id}_{task_id}_{datetime.now().strftime('%Y%m%d')}",
                    "points_awarded": points,
                    "agent_id": agent_id,
                    "task_id": task_id,
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error processing completion: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.process_completion")

    def _update_agent_status(self, agent_id: str, task_id: str, points: int):
        """Update agent's status.json with completion."""
        status_file = Path(f"agent_workspaces/{agent_id}/status.json")

        if status_file.exists():
            with open(status_file, "r") as f:
                status = json.load(f)

            # Move task to completed
            if "completed_tasks" not in status:
                status["completed_tasks"] = []

            status["completed_tasks"].insert(0, f"{task_id}: COMPLETE (+{points} pts)")
            status["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(status_file, "w") as f:
                json.dump(status, f, indent=2)

    def _log_to_swarm_brain(self, completion_data: dict):
        """Log completion to swarm brain."""
        try:
            from src.swarm_brain.swarm_memory import SwarmMemory

            memory = SwarmMemory(agent_id="Captain")
            memory.share_learning(
                title=f"Task Completion: {completion_data['task_id']}",
                content=f"Agent {completion_data['agent_id']} completed with {completion_data['points']} points",
                tags=["completion", "captain", "tracking"],
            )
        except Exception as e:
            logger.warning(f"Could not log to swarm brain: {e}")


# DEPRECATED: LeaderboardUpdaterTool consolidated into captain_tools.py
# Use captain.update_leaderboard instead (supports both batch and single-agent modes)
# This class kept for backward compatibility but delegates to consolidated tool
#
# Agent-8 SSOT Consolidation - 2025-01-27

class LeaderboardUpdaterTool(IToolAdapter):
    """
    DEPRECATED: Use captain.update_leaderboard instead.
    
    This tool has been consolidated into captain_tools.py → LeaderboardUpdateTool.
    Delegates to consolidated implementation for backward compatibility.
    """

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.update_leaderboard_coord",
            version="1.0.0",
            category="captain.coordination",
            summary="DEPRECATED: Use captain.update_leaderboard instead",
            required_params=["agent_id", "points"],
            optional_params={"achievement": None},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute leaderboard update - delegates to consolidated tool."""
        logger.warning(
            "captain.update_leaderboard_coord is deprecated. "
            "Use captain.update_leaderboard instead."
        )

        # Delegate to consolidated tool via toolbelt
        from ..toolbelt_core import get_toolbelt_core

        toolbelt = get_toolbelt_core()
        # Convert params to consolidated format
        consolidated_params = {
            "agent_id": params["agent_id"],
            "points": params["points"],
            "achievement": params.get("achievement"),
        }

        return toolbelt.run("captain.update_leaderboard", consolidated_params, context)


class NextTaskPickerTool(IToolAdapter):
    """
    Pick next optimal task for an agent based on specialty and ROI.
    
    Migrated from: tools/captain_next_task_picker.py
    """

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.pick_next_task",
            version="1.0.0",
            category="captain.coordination",
            summary="Pick optimal next task for agent based on specialty/ROI",
            required_params=["agent_id", "agent_specialty", "available_tasks"],
            optional_params={},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute task picking."""
        try:
            agent_id = params["agent_id"]
            agent_specialty = params["agent_specialty"]
            available_tasks = params["available_tasks"]

            if not available_tasks:
                return ToolResult(
                    success=True,
                    output={"agent_id": agent_id, "selected_task": None, "reason": "No tasks available"},
                    exit_code=0,
                )

            # Score tasks by fit to agent specialty
            scored_tasks = []
            for task in available_tasks:
                score = self._calculate_task_fit(
                    agent_specialty=agent_specialty,
                    task_category=task.get("category", ""),
                    task_priority=task.get("priority", "normal"),
                    task_points=task.get("points", 0),
                )
                scored_tasks.append((score, task))

            # Sort by score (highest first)
            scored_tasks.sort(key=lambda x: x[0], reverse=True)

            # Return best fit
            best_task = scored_tasks[0][1] if scored_tasks else None
            best_score = scored_tasks[0][0] if scored_tasks else 0.0

            return ToolResult(
                success=True,
                output={
                    "agent_id": agent_id,
                    "selected_task": best_task,
                    "score": round(best_score, 2),
                    "alternatives": [task for _, task in scored_tasks[1:4]],  # Top 3 alternatives
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error picking next task: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.pick_next_task")

    def _calculate_task_fit(
        self, agent_specialty: str, task_category: str, task_priority: str, task_points: int
    ) -> float:
        """Calculate how well task fits agent."""
        score = 0.0

        # Specialty match (+50 points)
        if agent_specialty.lower() in task_category.lower():
            score += 50.0

        # Priority bonus (+30 urgent, +15 high)
        if task_priority == "urgent":
            score += 30.0
        elif task_priority == "high":
            score += 15.0

        # Points ROI (+points/100)
        score += task_points / 100.0

        return score


class ROIQuickCalculatorTool(IToolAdapter):
    """
    Quick ROI calculation for captain decision-making.
    
    Migrated from: tools/captain_roi_quick_calc.py
    """

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.calculate_roi",
            version="1.0.0",
            category="captain.coordination",
            summary="Quick ROI calculation for decision-making",
            required_params=["points", "effort_hours"],
            optional_params={"complexity": 5},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute ROI calculation."""
        try:
            points = params["points"]
            effort_hours = params["effort_hours"]
            complexity = params.get("complexity", 5)

            # Base ROI: points per hour
            base_roi = points / effort_hours if effort_hours > 0 else 0

            # Complexity adjustment (lower complexity = higher ROI)
            complexity_factor = (10 - complexity) / 10.0
            adjusted_roi = base_roi * (1 + complexity_factor)

            # ROI tier
            if adjusted_roi >= 100:
                tier = "EXCELLENT"
            elif adjusted_roi >= 50:
                tier = "HIGH"
            elif adjusted_roi >= 20:
                tier = "MEDIUM"
            else:
                tier = "LOW"

            return ToolResult(
                success=True,
                output={
                    "base_roi": round(base_roi, 2),
                    "adjusted_roi": round(adjusted_roi, 2),
                    "tier": tier,
                    "points": points,
                    "effort_hours": effort_hours,
                    "complexity": complexity,
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error calculating ROI: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.calculate_roi")

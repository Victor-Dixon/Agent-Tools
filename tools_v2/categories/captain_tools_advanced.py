"""
Captain Advanced Operations Tools
==================================

Advanced tool adapters for Captain operations: points calculation,
mission assignment, and Markov optimization.

V2 Compliance: <300 lines
Author: Agent-4 (Captain) - Refactored 2025-01-27
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class PointsCalculatorTool(IToolAdapter):
    """Calculate points based on ROI, impact, and complexity."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.calc_points",
            version="1.0.0",
            category="captain",
            summary="Calculate task points based on ROI metrics",
            required_params=["task_type"],
            optional_params={
                "impact": "medium",
                "complexity": "medium",
                "time_saved": 0,
                "custom_multiplier": 1.0,
            },
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute points calculation."""
        try:
            task_type = params["task_type"]
            impact = params.get("impact", "medium")
            complexity = params.get("complexity", "medium")
            time_saved = params.get("time_saved", 0)
            multiplier = params.get("custom_multiplier", 1.0)

            # Base points by task type
            base_points = {
                "refactor": 500,
                "consolidation": 1000,
                "tooling": 400,
                "testing": 300,
                "documentation": 200,
                "bugfix": 300,
                "feature": 800,
                "infrastructure": 600,
            }

            # Impact multipliers
            impact_mult = {"low": 0.7, "medium": 1.0, "high": 1.5, "critical": 2.0}

            # Complexity multipliers
            complexity_mult = {
                "trivial": 0.5,
                "low": 0.8,
                "medium": 1.0,
                "high": 1.3,
                "expert": 1.6,
            }

            base = base_points.get(task_type, 400)
            impact_factor = impact_mult.get(impact, 1.0)
            complexity_factor = complexity_mult.get(complexity, 1.0)

            # Calculate total points
            calculated = int(base * impact_factor * complexity_factor * multiplier)

            # Add time-saved bonus
            if time_saved > 0:
                time_bonus = int(time_saved * 10)  # 10 pts per hour saved
                calculated += time_bonus

            return ToolResult(
                success=True,
                output={
                    "task_type": task_type,
                    "base_points": base,
                    "impact_multiplier": impact_factor,
                    "complexity_multiplier": complexity_factor,
                    "custom_multiplier": multiplier,
                    "time_bonus": int(time_saved * 10) if time_saved > 0 else 0,
                    "total_points": calculated,
                    "breakdown": f"{base} × {impact_factor} × {complexity_factor} × {multiplier}",
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error calculating points: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.calc_points")


class MissionAssignTool(IToolAdapter):
    """Create structured mission files in agent inboxes."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.assign_mission",
            version="1.0.0",
            category="captain",
            summary="Create structured mission file in agent inbox",
            required_params=["agent_id", "mission_title", "mission_description"],
            optional_params={
                "points": 0,
                "roi": 0.0,
                "complexity": "medium",
                "priority": "regular",
                "dependencies": [],
            },
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute mission assignment."""
        try:
            agent_id = params["agent_id"]
            mission_title = params["mission_title"]
            mission_desc = params["mission_description"]
            points = params.get("points", 0)
            roi = params.get("roi", 0.0)
            complexity = params.get("complexity", "medium")
            priority = params.get("priority", "regular")
            dependencies = params.get("dependencies", [])

            # Create mission file
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"C2A_MISSION_{mission_title.replace(' ', '_').upper()}_{timestamp}.md"
            inbox_path = Path(f"agent_workspaces/{agent_id}/inbox")
            inbox_path.mkdir(parents=True, exist_ok=True)

            mission_file = inbox_path / filename

            # Generate mission content
            content = f"""# [C2A] CAPTAIN → {agent_id}: {mission_title}

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Priority:** {priority}  
**Estimated Points:** {points}  
**ROI:** {roi}  
**Complexity:** {complexity}

---

## 🎯 MISSION OBJECTIVE

{mission_desc}

---

## 📊 MISSION METRICS

- **Points:** {points} pts
- **ROI:** {roi}
- **Complexity:** {complexity}
- **Priority:** {priority}

---

## 🔗 DEPENDENCIES

{chr(10).join(f'- {dep}' for dep in dependencies) if dependencies else 'None'}

---

## ✅ SUCCESS CRITERIA

- [ ] Implementation complete
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Git commit created
- [ ] Report delivered

---

## 📝 REPORTING

Report completion to: agent_workspaces/Agent-4/inbox/
Tag: #DONE-{mission_title.replace(' ', '-').upper()}

---

**🐝 WE. ARE. SWARM.** ⚡🔥
"""

            mission_file.write_text(content, encoding="utf-8")

            return ToolResult(
                success=True,
                output={
                    "agent_id": agent_id,
                    "mission_file": str(mission_file),
                    "mission_title": mission_title,
                    "points": points,
                    "created": True,
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error assigning mission: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.assign_mission")


class MarkovOptimizerTool(IToolAdapter):
    """Interface to Markov chain optimizer for task selection."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.markov_optimize",
            version="1.0.0",
            category="captain",
            summary="Use Markov optimizer for ROI-based task selection",
            required_params=["tasks"],
            optional_params={"agent_count": 8, "time_budget": 120},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute Markov optimization."""
        try:
            tasks = params["tasks"]  # List of task dicts with ROI, time, points
            agent_count = params.get("agent_count", 8)
            time_budget = params.get("time_budget", 120)

            # Simple greedy optimizer (real Markov would be more complex)
            # Sort tasks by ROI descending
            sorted_tasks = sorted(tasks, key=lambda t: t.get("roi", 0), reverse=True)

            assignments = []
            total_time = 0
            total_points = 0

            for task in sorted_tasks:
                task_time = task.get("time_estimate", 60)
                if total_time + task_time <= time_budget:
                    assignments.append(task)
                    total_time += task_time
                    total_points += task.get("points", 0)

            avg_roi = (
                sum(t.get("roi", 0) for t in assignments) / len(assignments) if assignments else 0
            )

            return ToolResult(
                success=True,
                output={
                    "recommended_tasks": assignments,
                    "total_tasks": len(assignments),
                    "total_time": total_time,
                    "total_points": total_points,
                    "average_roi": round(avg_roi, 2),
                    "efficiency": (
                        round((total_points / total_time) * 100, 2) if total_time > 0 else 0
                    ),
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error running Markov optimizer: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.markov_optimize")

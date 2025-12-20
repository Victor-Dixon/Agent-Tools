#!/usr/bin/env python3
"""
Intelligent Mission Advisor Tool Adapter
========================================

IToolAdapter wrapper for the masterpiece Intelligent Mission Advisor.

Author: Agent-5 (Business Intelligence & Team Beta Leader)
License: MIT
"""

import logging
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError
from .intelligent_mission_advisor import get_mission_advisor

logger = logging.getLogger(__name__)


class MissionAdvisorTool(IToolAdapter):
    """Get intelligent mission recommendation - THE MASTERPIECE TOOL."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="advisor.recommend",
            version="1.0.0",
            category="intelligent_advisor",
            summary="🧠 MASTERPIECE: AI-powered mission advisor - your personal senior engineer copilot",
            required_params=["agent_id"],
            optional_params={"context": None, "prefer_high_roi": True, "avoid_duplication": True},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        if "agent_id" not in params:
            return (False, ["Missing required parameter: agent_id"])
        return (True, [])

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        try:
            agent_id = params["agent_id"]
            advisor = get_mission_advisor(agent_id)

            recommendation = advisor.get_mission_recommendation(
                context=params.get("context"),
                prefer_high_roi=params.get("prefer_high_roi", True),
                avoid_duplication=params.get("avoid_duplication", True),
            )

            # Format output
            output = {
                "recommendation": recommendation,
                "summary": self._format_summary(recommendation),
            }

            return ToolResult(
                success=recommendation.get("recommended_task") is not None,
                output=output,
                exit_code=0 if recommendation.get("recommended_task") else 1,
            )
        except Exception as e:
            logger.error(f"Mission advisor failed: {e}")
            raise ToolExecutionError(str(e), tool_name="advisor.recommend")

    def _format_summary(self, recommendation: dict[str, Any]) -> str:
        """Format recommendation summary."""
        if recommendation.get("recommended_task"):
            task = recommendation["recommended_task"]
            return f"""
🎯 RECOMMENDED MISSION:
  File: {task.get('file', 'Unknown')}
  ROI: {task.get('roi', 0):.2f}
  Points: {task.get('points', 0)}
  Specialty Match: {task.get('specialty_match', 0):.0%}
  Status: {recommendation.get('verification_status', 'Unknown')}
  
{recommendation.get('intelligent_briefing', '')}
"""
        else:
            return "No suitable tasks found. " + str(recommendation.get("suggestions", []))


class OrderValidatorTool(IToolAdapter):
    """Validate Captain's orders before execution - CRITICAL SAFETY."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="advisor.validate",
            version="1.0.0",
            category="intelligent_advisor",
            summary="🛡️ Validate Captain's orders (prevent phantom tasks - Pattern #1!)",
            required_params=["agent_id", "order_file"],
            optional_params={},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        if "agent_id" not in params:
            errors.append("Missing required parameter: agent_id")
        if "order_file" not in params:
            errors.append("Missing required parameter: order_file")
        return (len(errors) == 0, errors)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        try:
            agent_id = params["agent_id"]
            order_file = params["order_file"]

            advisor = get_mission_advisor(agent_id)
            validation = advisor.validate_captain_order(order_file)

            # Format output
            output = {
                "validation": validation,
                "decision": validation.get("recommendation", "REVIEW_MANUALLY"),
                "summary": self._format_validation_summary(validation),
            }

            return ToolResult(
                success=validation.get("validated", False),
                output=output,
                exit_code=0 if validation.get("validated") else 1,
            )
        except Exception as e:
            logger.error(f"Order validation failed: {e}")
            raise ToolExecutionError(str(e), tool_name="advisor.validate")

    def _format_validation_summary(self, validation: dict[str, Any]) -> str:
        """Format validation summary."""
        if validation.get("validated"):
            return f"""
✅ ORDER VALIDATED - SAFE TO EXECUTE!
  Order exists: {validation.get('order_exists')}
  Task file exists: {validation.get('task_file_exists')}
  Task available: {validation.get('task_available')}
  Conflicts: {len(validation.get('conflicts', []))}
  
  → {validation.get('recommendation')}: {validation.get('message', '')}
"""
        else:
            return f"""
⚠️ ORDER VALIDATION FAILED!
  Issue: {validation.get('issue', 'Unknown')}
  Recommendation: {validation.get('recommendation', 'REVIEW_MANUALLY')}
  
  DO NOT EXECUTE - Report to Captain first!
"""


class SwarmAnalyzerTool(IToolAdapter):
    """Analyze overall swarm state - STRATEGIC INTELLIGENCE."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="advisor.swarm",
            version="1.0.0",
            category="intelligent_advisor",
            summary="📊 Analyze swarm state and identify opportunities",
            required_params=["agent_id"],
            optional_params={},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        if "agent_id" not in params:
            return (False, ["Missing required parameter: agent_id"])
        return (True, [])

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        try:
            agent_id = params["agent_id"]
            advisor = get_mission_advisor(agent_id)

            analysis = advisor.analyze_swarm_state()

            return ToolResult(success=True, output=analysis, exit_code=0)
        except Exception as e:
            logger.error(f"Swarm analysis failed: {e}")
            raise ToolExecutionError(str(e), tool_name="advisor.swarm")


class RealtimeGuidanceTool(IToolAdapter):
    """Get real-time execution guidance - CONTINUOUS INTELLIGENCE."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="advisor.guide",
            version="1.0.0",
            category="intelligent_advisor",
            summary="💡 Get real-time execution guidance during task",
            required_params=["agent_id", "current_step"],
            optional_params={"task_context": {}},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        if "agent_id" not in params:
            errors.append("Missing required parameter: agent_id")
        if "current_step" not in params:
            errors.append("Missing required parameter: current_step")
        return (len(errors) == 0, errors)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        try:
            agent_id = params["agent_id"]
            current_step = params["current_step"]
            task_context = params.get("task_context", {})

            advisor = get_mission_advisor(agent_id)
            guidance = advisor.get_realtime_guidance(current_step, task_context)

            return ToolResult(
                success=True, output={"guidance": guidance, "step": current_step}, exit_code=0
            )
        except Exception as e:
            logger.error(f"Realtime guidance failed: {e}")
            raise ToolExecutionError(str(e), tool_name="advisor.guide")


__all__ = ["MissionAdvisorTool", "OrderValidatorTool", "SwarmAnalyzerTool", "RealtimeGuidanceTool"]

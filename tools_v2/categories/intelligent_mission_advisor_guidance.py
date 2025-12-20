#!/usr/bin/env python3
"""
Intelligent Mission Advisor - Guidance Module
==============================================

Intelligent briefings, execution guidance, and real-time support.

This module handles the guidance and advisory features:
- Intelligent briefing generation
- Approach recommendations
- Pattern matching
- Execution guidance
- Real-time assistance during task execution

Author: Agent-5 (Business Intelligence & Team Beta Leader)
License: MIT
"""

import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class IntelligentMissionGuidance:
    """Guidance and advisory support for intelligent mission advisor."""

    def __init__(
        self,
        agent_id: str,
        agent_specialty: str,
        agent_status: dict[str, Any],
        swarm_brain: dict[str, Any],
        other_agents_work: dict[str, Any],
        leaderboard: dict[str, Any],
    ):
        """
        Initialize guidance module.

        Args:
            agent_id: Agent identifier
            agent_specialty: Agent's specialty area
            agent_status: Agent's current status
            swarm_brain: Swarm collective intelligence
            other_agents_work: Other agents' current work
            leaderboard: Competitive leaderboard
        """
        self.agent_id = agent_id
        self.agent_specialty = agent_specialty
        self.agent_status = agent_status
        self.swarm_brain = swarm_brain
        self.other_agents_work = other_agents_work
        self.leaderboard = leaderboard

    def generate_intelligent_briefing(self, task: dict[str, Any], verification: dict[str, Any]) -> str:
        """Generate comprehensive intelligent briefing for the task."""
        briefing = f"""
🧠 INTELLIGENT MISSION BRIEFING - {self.agent_id}
{'='*60}

FILE: {task['file']}
TYPE: {task.get('type', 'refactor')}
VERIFICATION: {verification['status']}

TASK INTELLIGENCE:
- File exists: {verification['file_exists']}
- Current lines: {verification.get('current_lines', 'unknown')}
- Estimated complexity: {task.get('complexity', 0):.1f}
- ROI score: {task.get('roi', 0):.2f}
- Specialty match: {task.get('specialty_match', 0):.0%}
- Estimated points: {task.get('points', 0)}

YOUR SPECIALTY: {self.agent_specialty}
Why this matches: {self.explain_specialty_match(task)}

WHAT YOU'RE REFACTORING:
{task.get('issue', 'V2 compliance needed')}

RECOMMENDED APPROACH:
{self.generate_approach_recommendation(task)}

SWARM CONTEXT:
- Other agents working on: {len(self.other_agents_work)} tasks
- Your current rank: {self.get_current_rank()}
- Patterns to apply: {len(self.swarm_brain.get('patterns', []))} available

VERIFICATION CHECKS PERFORMED:
{chr(10).join('  - ' + check for check in verification['checks_performed'])}

CONFIDENCE LEVEL: {self.calculate_confidence(task, verification):.0%}

🎯 This is the optimal task for you right now based on comprehensive analysis!
"""
        return briefing.strip()

    def explain_specialty_match(self, task: dict[str, Any]) -> str:
        """Explain why task matches agent specialty."""
        file_path = task["file"].lower()
        specialty = self.agent_specialty

        if specialty == "BI/Analytics":
            if "analytics" in file_path or "intelligence" in file_path:
                return "Perfect match - analytics/intelligence work aligns with your BI specialty"
            elif "metrics" in file_path or "reporting" in file_path:
                return "Strong match - metrics/reporting leverages your analytical skills"
            else:
                return "General development - can apply BI perspective"

        return "Task matches your capabilities"

    def generate_approach_recommendation(self, task: dict[str, Any]) -> str:
        """Generate recommended approach based on task analysis."""
        lines = task.get("lines", 0)
        functions = task.get("functions", 0)

        if lines > 600:
            return "Large file - split into 3-4 focused modules. Extract by responsibility."
        elif lines > 400:
            return "Medium file - split into 2-3 modules. Group related functionality."
        elif functions > 10:
            return "High function count - extract utilities and group by domain."
        else:
            return "Optimize structure - clean up, add type hints, improve documentation."

    def calculate_confidence(self, task: dict[str, Any], verification: dict[str, Any]) -> float:
        """Calculate confidence in recommendation."""
        confidence = 0.5

        if verification["status"] == "VERIFIED":
            confidence += 0.3

        if task.get("specialty_match", 0) > 0.7:
            confidence += 0.2

        return min(confidence, 1.0)

    def get_current_rank(self) -> str:
        """Get agent's current leaderboard rank."""
        if not self.leaderboard:
            return "Unknown"

        # Simple rank lookup
        for rank, data in self.leaderboard.items():
            if isinstance(data, dict) and data.get("agent") == self.agent_id:
                return rank

        return "Unranked"

    def find_relevant_patterns(self, task: dict[str, Any]) -> list[str]:
        """Find relevant swarm brain patterns for this task."""
        patterns = []

        # Always include Pattern #1
        patterns.append("Pattern #1: Verify reality before claiming work")

        # Add task-specific patterns
        if "refactor" in task.get("type", ""):
            patterns.append("Pattern: Clean architecture - split by responsibility")
            patterns.append("Pattern: Maintain backward compatibility")

        if self.agent_specialty == "BI/Analytics":
            patterns.append("Pattern: Add BI capabilities during refactoring")
            patterns.append("Pattern: Create intelligence interfaces")

        return patterns

    def generate_execution_guidance(self, task: dict[str, Any], patterns: list[str]) -> list[str]:
        """Generate step-by-step execution guidance."""
        guidance = []

        # Standard refactoring steps
        if task.get("type") == "v2_refactor":
            guidance.extend(
                [
                    "1. VERIFY: File exists and needs work (Pattern #1)",
                    "2. ANALYZE: Read entire file, understand structure",
                    "3. DESIGN: Plan module split (group by responsibility)",
                    "4. REFACTOR: Extract modules incrementally",
                    "5. TEST: Validate imports and functionality",
                    "6. DOCUMENT: Update documentation and create devlog",
                    "7. TAG: Mark completion #DONE-CXXX-" + self.agent_id,
                ]
            )

        # Add specialty-specific guidance
        if self.agent_specialty == "BI/Analytics":
            guidance.append("8. ENHANCE: Consider adding BI/analytics capabilities")

        return guidance

    def get_realtime_guidance(self, current_step: str, task_context: dict[str, Any]) -> str:
        """
        Get real-time guidance during task execution.

        Provides intelligent suggestions based on current progress.

        Args:
            current_step: Current step in execution (e.g., "refactoring")
            task_context: Context about current task and progress

        Returns:
            Real-time guidance message
        """
        if current_step == "verification":
            return "✅ Apply Pattern #1: Verify file exists, check if already done, scan for conflicts"

        elif current_step == "analysis":
            return "📊 Focus on: Structure, dependencies, functionality. Look for natural split points."

        elif current_step == "refactoring":
            specialty_tip = ""
            if self.agent_specialty == "BI/Analytics":
                specialty_tip = " Consider adding analytics interfaces!"
            return f"🔧 Extract by responsibility. Keep <400 lines per module.{specialty_tip}"

        elif current_step == "testing":
            return "🧪 Test imports first, then functionality. Zero linter errors required."

        elif current_step == "documentation":
            return "📝 Create devlog, update status, tag completion. Message Captain."

        else:
            return "💡 Executing task - stay focused on V2 compliance and quality!"

    def analyze_swarm_state(self) -> dict[str, Any]:
        """
        Analyze overall swarm state and provide strategic insights.

        Returns:
            Comprehensive swarm state analysis
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(self.other_agents_work) + 1,
            "agents_active": sum(
                1 for w in self.other_agents_work.values() if "COMPLETE" not in w.get("status", "")
            ),
            "your_position": self.get_current_rank(),
            "swarm_patterns_available": len(self.swarm_brain.get("patterns", [])),
            "opportunities": [],
        }

        # Identify opportunities
        active_areas = defaultdict(int)
        for work in self.other_agents_work.values():
            tasks_str = str(work.get("tasks", []))
            if "analytics" in tasks_str.lower():
                active_areas["analytics"] += 1
            if "error" in tasks_str.lower():
                active_areas["error_handling"] += 1
            if "messaging" in tasks_str.lower():
                active_areas["messaging"] += 1

        # Find underserved areas
        if active_areas.get("analytics", 0) < 2 and self.agent_specialty == "BI/Analytics":
            analysis["opportunities"].append("Analytics area underserved - opportunity for BI work!")

        return analysis

    def generate_fallback_suggestions(self) -> list[str]:
        """Generate fallback suggestions when no tasks found."""
        return [
            "Run project scanner to identify new V2 violations",
            "Check inbox for Captain's orders",
            "Review completed tasks and update documentation",
            "Scan for proactive opportunities in your specialty area",
            "Consider Team Beta coordination tasks",
        ]


__all__ = ["IntelligentMissionGuidance"]


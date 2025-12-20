#!/usr/bin/env python3
"""
Intelligent Mission Advisor - Analysis Module
==============================================

Task analysis, matching, ROI calculation, and verification functionality.

This module handles the analytical core of the mission advisor:
- Scanning for real available tasks
- Conflict detection with other agents
- Specialty matching
- ROI calculation and ranking
- Task verification (Pattern #1!)

Author: Agent-5 (Business Intelligence & Team Beta Leader)
License: MIT
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class IntelligentMissionAnalysis:
    """Task analysis and verification for intelligent mission advisor."""

    def __init__(self, agent_id: str, agent_specialty: str, project_root: Path, other_agents_work: dict[str, Any]):
        """
        Initialize analysis module.

        Args:
            agent_id: Agent identifier
            agent_specialty: Agent's specialty area
            project_root: Project root path
            other_agents_work: Dictionary of other agents' current work
        """
        self.agent_id = agent_id
        self.agent_specialty = agent_specialty
        self.project_root = project_root
        self.other_agents_work = other_agents_work

    def scan_real_available_tasks(self, context: str | None) -> list[dict[str, Any]]:
        """Scan for REAL available tasks (verify files actually exist)."""
        tasks = []

        # Load project analysis
        analysis_file = self.project_root / "project_analysis.json"
        if analysis_file.exists():
            try:
                analysis = json.loads(analysis_file.read_text(encoding="utf-8"))

                # Look for V2 violations (potential tasks)
                if "v2_violations" in analysis:
                    for violation in analysis["v2_violations"][:50]:  # Limit to first 50
                        file_path = violation.get("file", "")

                        # CRITICAL: Verify file actually exists!
                        if Path(file_path).exists():
                            tasks.append(
                                {
                                    "file": file_path,
                                    "type": "v2_refactor",
                                    "issue": violation.get("issue", ""),
                                    "lines": violation.get("lines", 0),
                                    "functions": violation.get("functions", 0),
                                    "verified": True,
                                }
                            )
            except:
                pass

        # Filter by context if provided
        if context:
            tasks = [t for t in tasks if context.lower() in t["file"].lower()]

        return tasks

    def check_conflicts(self, tasks: list[dict[str, Any]]) -> list[str]:
        """Check if other agents are working on these files."""
        conflicts = []

        for agent_name, work_info in self.other_agents_work.items():
            tasks_str = str(work_info.get("tasks", []))
            mission_str = str(work_info.get("mission", ""))

            for task in tasks:
                file_name = Path(task["file"]).name
                if file_name in tasks_str or file_name in mission_str:
                    conflicts.append(task["file"])

        return conflicts

    def match_specialty(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Match tasks to agent's specialty."""
        matched = []

        for task in tasks:
            match_score = 0
            file_path = task["file"].lower()

            # BI/Analytics specialty matching
            if self.agent_specialty == "BI/Analytics":
                if any(
                    word in file_path
                    for word in ["analytics", "intelligence", "metrics", "business", "reporting"]
                ):
                    match_score = 1.0
                elif any(word in file_path for word in ["engine", "processor", "calculator"]):
                    match_score = 0.7

            # Add match score
            task["specialty_match"] = match_score
            matched.append(task)

        # Sort by specialty match
        return sorted(matched, key=lambda t: t["specialty_match"], reverse=True)

    def calculate_roi(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Calculate ROI for tasks and rank them."""
        for task in tasks:
            # Simple ROI: reward / complexity
            lines = task.get("lines", 400)
            functions = task.get("functions", 10)

            complexity = (lines / 10) + (functions * 2)
            reward = 500 if lines > 500 else 300  # Simplified

            roi = reward / max(complexity, 1)
            points = reward

            task["roi"] = round(roi, 2)
            task["points"] = points
            task["complexity"] = complexity

        # Sort by ROI descending
        return sorted(tasks, key=lambda t: t["roi"], reverse=True)

    def verify_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """Verify task is real and actionable (Swarm Brain Pattern #1!)."""
        verification = {
            "status": "UNKNOWN",
            "file_exists": False,
            "already_refactored": False,
            "v2_compliant": False,
            "actionable": False,
            "checks_performed": [],
        }

        file_path = Path(task["file"])

        # Check 1: File exists
        verification["file_exists"] = file_path.exists()
        verification["checks_performed"].append(f"File existence: {verification['file_exists']}")

        if not verification["file_exists"]:
            verification["status"] = "PHANTOM_TASK"
            verification["message"] = "File does not exist! Phantom task detected."
            return verification

        # Check 2: Already refactored?
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = len(content.split("\n"))

            # Check if already V2 compliant
            if lines <= 400:
                # Count classes and functions
                classes = content.count("class ")
                functions = content.count("def ")

                if classes <= 5:
                    verification["already_refactored"] = True
                    verification["v2_compliant"] = True
                    verification["status"] = "ALREADY_DONE"
                    verification["message"] = f"File already V2 compliant ({lines}L, {classes} classes)"
                    return verification

            verification["current_lines"] = lines
            verification["checks_performed"].append(f"Current lines: {lines}")

        except Exception as e:
            verification["checks_performed"].append(f"File analysis error: {e}")

        # Check 3: Is actionable?
        if verification["file_exists"] and not verification["already_refactored"]:
            verification["actionable"] = True
            verification["status"] = "VERIFIED"
            verification["message"] = "Task verified - file exists and needs work"

        return verification

    def identify_risks(self, task: dict[str, Any]) -> list[str]:
        """Identify potential risks in task execution."""
        risks = []

        if task.get("lines", 0) > 800:
            risks.append("Very large file - may take multiple cycles")

        if task.get("functions", 0) > 30:
            risks.append("High function count - complex dependencies possible")

        if "deprecated" in task["file"].lower():
            risks.append("Deprecated file - verify if still in use")

        if "archive" in task["file"].lower():
            risks.append("Archive file - check if active or legacy")

        return risks or ["No significant risks identified"]

    def calculate_success_probability(self, task: dict[str, Any], agent_status: dict[str, Any]) -> float:
        """Calculate probability of successful completion."""
        score = 0.5  # Base 50%

        # Specialty match increases success
        score += task.get("specialty_match", 0) * 0.2

        # Lower complexity increases success
        complexity = task.get("complexity", 50)
        if complexity < 30:
            score += 0.2
        elif complexity < 50:
            score += 0.1

        # Agent experience (based on completed tasks)
        completed = len(agent_status.get("completed_tasks", []))
        score += min(completed / 100, 0.2)  # Up to +20% for experience

        return min(score, 0.99)  # Cap at 99%


__all__ = ["IntelligentMissionAnalysis"]


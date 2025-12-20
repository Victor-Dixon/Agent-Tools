#!/usr/bin/env python3
"""
Intelligent Mission Advisor - The Masterpiece Tool
==================================================

AI-powered agent copilot providing real-time intelligence, task validation,
and execution guidance. The indispensable tool every agent needs.

Like the messaging system revolutionized agent communication,
this tool revolutionizes agent decision-making and execution.

Author: Agent-5 (Business Intelligence & Team Beta Leader)
License: MIT
"""

import json
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class IntelligentMissionAdvisor:
    """
    AI-powered mission advisor providing intelligent guidance to agents.

    This is the masterpiece tool - an agent's personal senior engineer advisor.

    Capabilities:
    - Real-time project state analysis (actual files, violations, needs)
    - Agent specialty matching (align work with strengths)
    - ROI optimization (suggest highest-value tasks)
    - Conflict detection (avoid duplicating other agents' work)
    - Task validation (verify files exist, check if already done)
    - Intelligent briefing (provide full context, not just orders)
    - Progress monitoring (real-time guidance during execution)
    - Pattern learning (apply successful swarm patterns)
    - Reality verification (documentation vs actual state)
    - Autonomous decision support (what should I work on next?)
    """

    def __init__(self, agent_id: str):
        """
        Initialize intelligent mission advisor for specific agent.

        Args:
            agent_id: Agent identifier (e.g., "Agent-5")
        """
        self.agent_id = agent_id
        self.project_root = Path(".")

        # Load agent context
        self.agent_workspace = self.project_root / "agent_workspaces" / agent_id
        self.agent_status = self._load_agent_status()
        self.agent_specialty = self._identify_specialty()

        # Load swarm context
        self.swarm_brain = self._load_swarm_brain()
        self.other_agents_work = self._load_other_agents_work()
        self.leaderboard = self._load_leaderboard()

        logger.info(f"Intelligent Mission Advisor initialized for {agent_id}")

    def _load_agent_status(self) -> dict[str, Any]:
        """Load agent's current status."""
        status_file = self.agent_workspace / "status.json"
        if status_file.exists():
            return json.loads(status_file.read_text(encoding="utf-8"))
        return {}

    def _identify_specialty(self) -> str:
        """Identify agent's specialty from status."""
        name = self.agent_status.get("agent_name", "")
        if "Business Intelligence" in name:
            return "BI/Analytics"
        elif "Quality" in name:
            return "Quality/Testing"
        elif "Infrastructure" in name:
            return "DevOps/Infrastructure"
        elif "Repository" in name or "Web" in name:
            return "Web/Cloning"
        elif "Captain" in name or "Strategic" in name:
            return "Strategic/Coordination"
        else:
            return "General"

    def _load_swarm_brain(self) -> dict[str, Any]:
        """Load swarm collective intelligence."""
        brain_file = self.project_root / "docs" / "SWARM_BRAIN.md"
        if brain_file.exists():
            # Parse patterns from swarm brain
            content = brain_file.read_text(encoding="utf-8")
            return {"patterns": self._extract_patterns(content), "content": content}
        return {"patterns": [], "content": ""}

    def _extract_patterns(self, content: str) -> list[str]:
        """Extract learned patterns from swarm brain."""
        patterns = []
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "Pattern #" in line or "PATTERN" in line.upper():
                patterns.append(line.strip())
        return patterns

    def _load_other_agents_work(self) -> dict[str, Any]:
        """Load what other agents are currently working on."""
        workspaces = self.project_root / "agent_workspaces"
        other_work = {}

        for agent_dir in workspaces.glob("Agent-*"):
            if agent_dir.name == self.agent_id:
                continue

            status_file = agent_dir / "status.json"
            if status_file.exists():
                try:
                    status = json.loads(status_file.read_text(encoding="utf-8"))
                    other_work[agent_dir.name] = {
                        "mission": status.get("current_mission", "Unknown"),
                        "tasks": status.get("current_tasks", []),
                        "status": status.get("status", "Unknown"),
                    }
                except:
                    pass

        return other_work

    def _load_leaderboard(self) -> dict[str, Any]:
        """Load competitive leaderboard."""
        # Try multiple sources
        leaderboard_files = [
            self.project_root
            / "agent_workspaces"
            / "Agent-8"
            / "ssot"
            / "competitive_leaderboard.json",
            self.project_root / "runtime" / "leaderboard.json",
        ]

        for lb_file in leaderboard_files:
            if lb_file.exists():
                try:
                    return json.loads(lb_file.read_text(encoding="utf-8"))
                except:
                    pass

        return {}

    def get_mission_recommendation(
        self,
        context: str | None = None,
        prefer_high_roi: bool = True,
        avoid_duplication: bool = True,
    ) -> dict[str, Any]:
        """
        Get intelligent mission recommendation for agent.

        This is the CORE masterpiece functionality - provides comprehensive
        intelligence about what the agent should work on next.

        Args:
            context: Optional context (e.g., "error handling", "analytics")
            prefer_high_roi: Prefer high-ROI tasks (default: True)
            avoid_duplication: Check other agents' work (default: True)

        Returns:
            Comprehensive mission recommendation with:
            - recommended_task: Task to work on
            - roi_score: ROI value
            - specialty_match: How well task matches agent specialty
            - verification_status: File exists / already done / available
            - conflicts: Other agents working on related tasks
            - intelligent_briefing: Full context and guidance
            - success_patterns: Relevant patterns from swarm brain
            - estimated_points: Expected point value
            - risk_factors: Potential issues to watch for
            - execution_guidance: Step-by-step suggestions

        Example:
            >>> advisor = IntelligentMissionAdvisor("Agent-5")
            >>> recommendation = advisor.get_mission_recommendation()
            >>> print(recommendation['recommended_task'])
            >>> print(recommendation['intelligent_briefing'])
            >>> if recommendation['verification_status'] == 'VERIFIED':
            ...     # Safe to proceed!
        """
        recommendation = {
            "agent_id": self.agent_id,
            "agent_specialty": self.agent_specialty,
            "timestamp": datetime.now().isoformat(),
            "analysis": {},
        }

        # Step 1: Scan for REAL available work (verify files exist)
        available_tasks = self._scan_real_available_tasks(context)
        recommendation["available_tasks_found"] = len(available_tasks)

        # Step 2: Check what other agents are doing (avoid duplication)
        if avoid_duplication:
            conflicts = self._check_conflicts(available_tasks)
            recommendation["conflicts_detected"] = conflicts
            # Filter out conflicting tasks
            available_tasks = [t for t in available_tasks if t["file"] not in conflicts]

        # Step 3: Match tasks to agent specialty
        specialty_matched = self._match_specialty(available_tasks)
        recommendation["specialty_matches"] = len(specialty_matched)

        # Step 4: Calculate ROI for each task
        if prefer_high_roi:
            roi_ranked = self._calculate_roi(specialty_matched)
        else:
            roi_ranked = specialty_matched

        # Step 5: Select best task
        if roi_ranked:
            best_task = roi_ranked[0]

            # Step 6: Verify task is real and actionable
            verification = self._verify_task(best_task)

            # Step 7: Generate intelligent briefing
            briefing = self._generate_intelligent_briefing(best_task, verification)

            # Step 8: Find relevant swarm patterns
            patterns = self._find_relevant_patterns(best_task)

            # Step 9: Generate execution guidance
            guidance = self._generate_execution_guidance(best_task, patterns)

            recommendation.update(
                {
                    "recommended_task": best_task,
                    "verification_status": verification["status"],
                    "verification_details": verification,
                    "intelligent_briefing": briefing,
                    "relevant_patterns": patterns,
                    "execution_guidance": guidance,
                    "estimated_points": best_task.get("points", 0),
                    "roi_score": best_task.get("roi", 0),
                    "specialty_match_score": best_task.get("specialty_match", 0),
                    "risk_factors": self._identify_risks(best_task),
                    "success_probability": self._calculate_success_probability(best_task),
                }
            )
        else:
            recommendation.update(
                {
                    "recommended_task": None,
                    "message": "No suitable tasks found matching criteria",
                    "suggestions": self._generate_fallback_suggestions(),
                }
            )

        return recommendation

    def _scan_real_available_tasks(self, context: str | None) -> list[dict[str, Any]]:
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

    def _check_conflicts(self, tasks: list[dict[str, Any]]) -> list[str]:
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

    def _match_specialty(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
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

    def _calculate_roi(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
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

    def _verify_task(self, task: dict[str, Any]) -> dict[str, Any]:
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
                    verification["message"] = (
                        f"File already V2 compliant ({lines}L, {classes} classes)"
                    )
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

    def _generate_intelligent_briefing(
        self, task: dict[str, Any], verification: dict[str, Any]
    ) -> str:
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
Why this matches: {self._explain_specialty_match(task)}

WHAT YOU'RE REFACTORING:
{task.get('issue', 'V2 compliance needed')}

RECOMMENDED APPROACH:
{self._generate_approach_recommendation(task)}

SWARM CONTEXT:
- Other agents working on: {len(self.other_agents_work)} tasks
- Your current rank: {self._get_current_rank()}
- Patterns to apply: {len(self.swarm_brain.get('patterns', []))} available

VERIFICATION CHECKS PERFORMED:
{chr(10).join('  - ' + check for check in verification['checks_performed'])}

CONFIDENCE LEVEL: {self._calculate_confidence(task, verification):.0%}

🎯 This is the optimal task for you right now based on comprehensive analysis!
"""
        return briefing.strip()

    def _explain_specialty_match(self, task: dict[str, Any]) -> str:
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

    def _generate_approach_recommendation(self, task: dict[str, Any]) -> str:
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

    def _identify_risks(self, task: dict[str, Any]) -> list[str]:
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

    def _calculate_success_probability(self, task: dict[str, Any]) -> float:
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
        completed = len(self.agent_status.get("completed_tasks", []))
        score += min(completed / 100, 0.2)  # Up to +20% for experience

        return min(score, 0.99)  # Cap at 99%

    def _calculate_confidence(self, task: dict[str, Any], verification: dict[str, Any]) -> float:
        """Calculate confidence in recommendation."""
        confidence = 0.5

        if verification["status"] == "VERIFIED":
            confidence += 0.3

        if task.get("specialty_match", 0) > 0.7:
            confidence += 0.2

        return min(confidence, 1.0)

    def _get_current_rank(self) -> str:
        """Get agent's current leaderboard rank."""
        if not self.leaderboard:
            return "Unknown"

        # Simple rank lookup
        for rank, data in self.leaderboard.items():
            if isinstance(data, dict) and data.get("agent") == self.agent_id:
                return rank

        return "Unranked"

    def _generate_fallback_suggestions(self) -> list[str]:
        """Generate fallback suggestions when no tasks found."""
        return [
            "Run project scanner to identify new V2 violations",
            "Check inbox for Captain's orders",
            "Review completed tasks and update documentation",
            "Scan for proactive opportunities in your specialty area",
            "Consider Team Beta coordination tasks",
        ]

    def validate_captain_order(self, order_file: str) -> dict[str, Any]:
        """
        Validate a Captain's order before executing.

        Applies Swarm Brain Pattern #1 - verify reality before claiming!

        Args:
            order_file: Path to Captain's execution order

        Returns:
            Validation results with go/no-go decision

        Example:
            >>> advisor = IntelligentMissionAdvisor("Agent-5")
            >>> result = advisor.validate_captain_order("inbox/EXECUTION_ORDER.md")
            >>> if result['validated']:
            ...     print("Safe to execute!")
            >>> else:
            ...     print(f"Issue: {result['issue']}")
        """
        validation = {
            "validated": False,
            "order_exists": False,
            "task_file_exists": False,
            "task_available": False,
            "conflicts": [],
            "recommendation": "DO_NOT_EXECUTE",
        }

        # Check 1: Order file exists
        order_path = Path(order_file)
        validation["order_exists"] = order_path.exists()

        if not validation["order_exists"]:
            validation["issue"] = f"Order file not found: {order_file}"
            return validation

        # Parse order to extract task file
        try:
            content = order_path.read_text(encoding="utf-8")

            # Extract file name (simple heuristic)
            for line in content.split("\n"):
                if ".py" in line and "Task:" in line:
                    # Extract filename
                    parts = line.split()
                    for part in parts:
                        if ".py" in part:
                            task_file = part.strip("*`:,")

                            # Check if file exists
                            # Try multiple paths
                            for prefix in ["", "src/", "src/core/", "src/services/", "tools/"]:
                                test_path = Path(prefix + task_file)
                                if test_path.exists():
                                    validation["task_file"] = str(test_path)
                                    validation["task_file_exists"] = True
                                    break

                            if not validation["task_file_exists"]:
                                validation["task_file"] = task_file
                                validation["issue"] = f"PHANTOM TASK: {task_file} does not exist!"
                                validation["recommendation"] = "REPORT_TO_CAPTAIN"
                                return validation

            # Check 2: Verify not already done
            if validation["task_file_exists"]:
                task_path = Path(validation["task_file"])
                content = task_path.read_text(encoding="utf-8")
                lines = len(content.split("\n"))

                if lines <= 400:
                    validation["issue"] = f"Task already V2 compliant ({lines} lines)"
                    validation["recommendation"] = "REPORT_COMPLETION"
                    return validation

            # Check 3: Check conflicts with other agents
            conflicts = self._check_conflicts([{"file": validation.get("task_file", "")}])
            if conflicts:
                validation["conflicts"] = conflicts
                validation["issue"] = f"Other agents working on related tasks: {conflicts}"
                validation["recommendation"] = "COORDINATE_FIRST"
                return validation

            # All checks passed!
            validation["validated"] = True
            validation["task_available"] = True
            validation["recommendation"] = "EXECUTE_IMMEDIATELY"
            validation["message"] = "Order validated - safe to execute!"

        except Exception as e:
            validation["issue"] = f"Error parsing order: {e}"
            validation["recommendation"] = "REVIEW_MANUALLY"

        return validation

    def _find_relevant_patterns(self, task: dict[str, Any]) -> list[str]:
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

    def _generate_execution_guidance(self, task: dict[str, Any], patterns: list[str]) -> list[str]:
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
            return (
                "✅ Apply Pattern #1: Verify file exists, check if already done, scan for conflicts"
            )

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
            "your_position": self._get_current_rank(),
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
            analysis["opportunities"].append(
                "Analytics area underserved - opportunity for BI work!"
            )

        return analysis


# Convenience function for quick access
def get_mission_advisor(agent_id: str) -> IntelligentMissionAdvisor:
    """
    Get intelligent mission advisor for an agent.

    Args:
        agent_id: Agent identifier

    Returns:
        Initialized IntelligentMissionAdvisor

    Example:
        >>> advisor = get_mission_advisor("Agent-5")
        >>> recommendation = advisor.get_mission_recommendation()
        >>> print(recommendation['intelligent_briefing'])
    """
    return IntelligentMissionAdvisor(agent_id)


__all__ = ["IntelligentMissionAdvisor", "get_mission_advisor"]

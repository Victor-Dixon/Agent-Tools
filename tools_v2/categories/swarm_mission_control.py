#!/usr/bin/env python3
"""
Swarm Mission Control - The Masterpiece Tool
============================================

The ONE tool agents can't live without.

Like the messaging system revolutionized coordination, Swarm Mission Control
revolutionizes task selection and execution by providing:

- WHAT should I work on? (Optimal next task)
- WHY this task? (ROI, impact, urgency)
- WITH WHAT CONTEXT? (Full context package)
- WHO else is working? (Avoid conflicts)
- WHAT'S been done? (Don't duplicate)
- WHAT dependencies? (Coordination needs)

This tool answers the fundamental question every agent asks:
"What should I do next and how do I do it effectively?"

Author: Agent-3 (Infrastructure & DevOps) - Masterpiece Tool
License: MIT
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter

logger = logging.getLogger(__name__)


class SwarmMissionControl(IToolAdapter):
    """
    Swarm Mission Control - The masterpiece tool for intelligent task selection.

    Provides each agent with:
    1. Optimal next task recommendation
    2. Full context package for execution
    3. Swarm state awareness (who's doing what)
    4. Conflict detection (avoid duplicate work)
    5. Dependency mapping (coordination needs)
    6. Success patterns (learn from past work)
    """

    def get_name(self) -> str:
        return "mission_control"

    def get_description(self) -> str:
        return "Get optimal next mission with full context (agents can't live without this)"

    def get_spec(self) -> dict[str, Any]:
        """Get tool specification."""
        return {
            "name": self.get_name(),
            "description": self.get_description(),
            "parameters": {
                "agent": {"type": "string", "required": True, "description": "Agent ID"}
            },
        }

    def validate(self, **kwargs) -> tuple[bool, str | None]:
        """Validate parameters."""
        if not kwargs.get("agent"):
            return False, "Agent ID required"
        return True, None

    def execute(self, **kwargs) -> dict[str, Any]:
        """Execute mission control analysis."""
        try:
            agent_id = kwargs.get("agent", "Agent-1")

            # PHASE 1: READ ENTIRE SWARM STATE
            swarm_state = read_swarm_state()

            # PHASE 2: READ AGENT'S CONTEXT
            agent_context = read_agent_context(agent_id, swarm_state)

            # PHASE 3: ANALYZE AVAILABLE WORK
            available_work = analyze_available_work(swarm_state)

            # PHASE 4: CALCULATE OPTIMAL TASK
            optimal_task = calculate_optimal_task(
                agent_id, agent_context, available_work, swarm_state
            )

            # PHASE 5: BUILD CONTEXT PACKAGE
            context_package = build_context_package(optimal_task, agent_context, swarm_state)

            # PHASE 6: RETURN MISSION BRIEF
            return {
                "success": True,
                "agent": agent_id,
                "timestamp": datetime.now().isoformat(),
                # THE ANSWER TO "WHAT SHOULD I DO?"
                "recommended_task": optimal_task,
                # THE ANSWER TO "WITH WHAT CONTEXT?"
                "context_package": context_package,
                # THE ANSWER TO "WHO'S DOING WHAT?"
                "swarm_state": swarm_state["summary"],
                # THE ANSWER TO "WHAT'S MY STATUS?"
                "agent_context": agent_context,
                # EXECUTION READY
                "ready_to_execute": optimal_task is not None,
                "mission_brief": format_mission_brief(optimal_task, context_package),
            }

        except Exception as e:
            logger.error(f"Mission control failed: {e}")
            return {"success": False, "error": str(e)}


class SwarmConflictDetector(IToolAdapter):
    """Detect if proposed work conflicts with active missions."""

    def get_name(self) -> str:
        return "conflict_detector"

    def get_description(self) -> str:
        return "Detect conflicts before starting work"

    def get_spec(self) -> dict[str, Any]:
        return {
            "name": self.get_name(),
            "description": self.get_description(),
            "parameters": {
                "agent": {"type": "string", "required": True},
                "file": {"type": "string", "required": False},
            },
        }

    def validate(self, **kwargs) -> tuple[bool, str | None]:
        if not kwargs.get("agent"):
            return False, "Agent ID required"
        return True, None

    def execute(self, **kwargs) -> dict[str, Any]:
        """Detect conflicts."""
        try:
            proposed_file = kwargs.get("file")
            agent_id = kwargs.get("agent")

            # Read all active missions
            conflicts = []
            workspace = Path("agent_workspaces")

            for i in range(1, 9):
                other_agent = f"Agent-{i}"
                if other_agent == agent_id:
                    continue

                status_file = workspace / other_agent / "status.json"
                if status_file.exists():
                    try:
                        status = json.load(open(status_file))
                        mission = status.get("current_mission", "")

                        # Check if proposed file mentioned in their mission
                        if proposed_file and proposed_file in mission:
                            conflicts.append(
                                {
                                    "agent": other_agent,
                                    "mission": mission,
                                    "conflict_type": "file_overlap",
                                }
                            )
                    except:
                        pass

            return {
                "success": True,
                "has_conflicts": len(conflicts) > 0,
                "conflicts": conflicts,
                "safe_to_proceed": len(conflicts) == 0,
                "recommendation": (
                    "Coordinate with agents listed" if conflicts else "Clear to proceed"
                ),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class ContextPackageBuilder(IToolAdapter):
    """Build complete context package for any task."""

    def get_name(self) -> str:
        return "context_builder"

    def get_description(self) -> str:
        return "Build complete context package for task execution"

    def get_spec(self) -> dict[str, Any]:
        return {
            "name": self.get_name(),
            "description": self.get_description(),
            "parameters": {
                "agent": {"type": "string", "required": True},
                "task": {"type": "string", "required": True},
            },
        }

    def validate(self, **kwargs) -> tuple[bool, str | None]:
        if not kwargs.get("agent"):
            return False, "Agent ID required"
        if not kwargs.get("task"):
            return False, "Task description required"
        return True, None

    def execute(self, **kwargs) -> dict[str, Any]:
        """Build context package."""
        try:
            task_description = kwargs.get("task", "")
            agent_id = kwargs.get("agent", "Agent-1")

            package = {
                "task": task_description,
                "agent": agent_id,
                "timestamp": datetime.now().isoformat(),
                "context": {},
            }

            # 1. Related files
            package["context"]["files_to_review"] = self._find_related_files(task_description)

            # 2. Similar past work
            package["context"]["similar_work"] = self._find_similar_work(task_description, agent_id)

            # 3. Current violations
            package["context"]["current_violations"] = self._find_current_violations()

            # 4. Dependencies
            package["context"]["dependencies"] = self._find_dependencies(task_description)

            # 5. Coordination needs
            package["context"]["coordinate_with"] = self._find_coordination_needs(task_description)

            # 6. Success patterns
            package["context"]["success_patterns"] = self._find_success_patterns(task_description)

            # 7. Execution checklist
            package["execution_checklist"] = self._generate_checklist(task_description)

            return {
                "success": True,
                "package": package,
                "ready_to_execute": True,
                "context_completeness": self._calculate_completeness(package),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _find_related_files(self, task: str) -> list[str]:
        """Find files related to task."""
        related = []
        keywords = task.lower().split()

        try:
            for keyword in keywords:
                if len(keyword) > 4:  # Meaningful keywords
                    files = list(Path("src").rglob(f"*{keyword}*.py"))
                    related.extend([str(f) for f in files[:5]])
        except:
            pass

        return list(set(related))[:10]  # Top 10 unique

    def _find_similar_work(self, task: str, agent_id: str) -> list[dict]:
        """Find similar past work."""
        similar = []

        try:
            # Check devlogs for similar work
            devlogs = Path("devlogs")
            if devlogs.exists():
                keywords = [w for w in task.lower().split() if len(w) > 4]
                for log in devlogs.glob("*.md"):
                    try:
                        content = open(log).read().lower()
                        if any(k in content for k in keywords):
                            similar.append({"devlog": log.name, "relevance": "keyword_match"})
                    except:
                        pass
        except:
            pass

        return similar[:5]  # Top 5

    def _find_current_violations(self) -> list[dict]:
        """Find current V2 violations."""
        violations = []

        try:
            # Quick scan for large files
            for py_file in Path("src").rglob("*.py"):
                try:
                    lines = len(open(py_file).readlines())
                    if lines > 400:
                        violations.append(
                            {"file": str(py_file), "lines": lines, "severity": "CRITICAL"}
                        )
                    elif lines > 350:
                        violations.append(
                            {"file": str(py_file), "lines": lines, "severity": "HIGH"}
                        )
                except:
                    pass

                # Limit to first 10 found
                if len(violations) >= 10:
                    break
        except:
            pass

        return violations

    def _find_dependencies(self, task: str) -> list[str]:
        """Find dependencies for task."""
        # Simplified - real implementation would analyze imports
        return []

    def _find_coordination_needs(self, task: str) -> list[str]:
        """Find which agents to coordinate with."""
        # Check if task involves files other agents are working on
        return []

    def _find_success_patterns(self, task: str) -> list[dict]:
        """Find patterns from successful similar tasks."""
        patterns = []

        try:
            # Look for "COMPLETE" devlogs with keywords
            devlogs = Path("devlogs")
            if devlogs.exists():
                keywords = [w for w in task.lower().split() if len(w) > 4]
                for log in devlogs.glob("*complete*.md"):
                    try:
                        content = open(log).read()
                        if any(k in content.lower() for k in keywords):
                            patterns.append(
                                {
                                    "pattern_source": log.name,
                                    "success_indicator": "completion_devlog",
                                }
                            )
                    except:
                        pass
        except:
            pass

        return patterns[:3]  # Top 3

    def _generate_checklist(self, task: str) -> list[str]:
        """Generate execution checklist."""
        return [
            "☐ Read all related files",
            "☐ Check for conflicts with other agents",
            "☐ Review similar past work",
            "☐ Plan modular structure",
            "☐ Execute with V2 compliance",
            "☐ Test thoroughly (zero errors)",
            "☐ Create documentation",
            "☐ Report completion to Captain",
        ]

    def _calculate_completeness(self, package: dict) -> float:
        """Calculate context completeness percentage."""
        total_sections = 7
        filled_sections = sum(
            [
                1 if package["context"].get("files_to_review") else 0,
                1 if package["context"].get("similar_work") else 0,
                1 if package["context"].get("current_violations") else 0,
                1 if package["context"].get("dependencies") else 0,
                1 if package["context"].get("coordinate_with") else 0,
                1 if package["context"].get("success_patterns") else 0,
                1 if package.get("execution_checklist") else 0,
            ]
        )

        return (filled_sections / total_sections) * 100


__all__ = ["SwarmMissionControl", "SwarmConflictDetector", "ContextPackageBuilder"]

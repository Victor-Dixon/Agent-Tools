"""
Autonomous Task Engine - The Masterpiece Tool for Swarm Intelligence

PURPOSE: Enable agents to autonomously discover and select their OPTIMAL next task
REVOLUTIONARY: Transforms agents from reactive (waiting for orders) to autonomous
INSPIRED BY: Agent-7's proactive behavior, Captain's Markov optimizer

This is the tool that enables TRUE autonomous swarm intelligence.
"""

from .autonomous.task_models import TaskOpportunity, TaskRecommendation, AgentProfile
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict
import ast
import re

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_DEFAULT = 30
        HTTP_MEDIUM = 60
        HTTP_LONG = 120
        HTTP_EXTENDED = 300
        HTTP_SHORT = 10


@dataclass
class AgentProfile:
    """Agent's capabilities and history"""
    agent_id: str
    specializations: List[str]
    past_work_types: Dict[str, int]  # task_type -> count
    files_worked: List[str]
    avg_cycle_time: float
    total_points: int
    success_rate: float
    preferred_complexity: str  # SIMPLE, MODERATE, COMPLEX
    current_workload: int  # 0-5 scale


# TaskRecommendation imported from task_models
    match_score: float  # 0-1 (skill match)
    priority_score: float  # 0-1 (urgency + impact)
    total_score: float  # Combined score
    reasoning: List[str]
    pros: List[str]
    cons: List[str]
    suggested_approach: str
    coordination_plan: Optional[str]


class AutonomousTaskEngine:
    """
    The Masterpiece Tool - Autonomous Task Discovery & Selection Engine

    Enables agents to:
    1. Discover optimal tasks autonomously
    2. Get personalized recommendations based on skills
    3. Calculate ROI and impact automatically
    4. Claim and track tasks without Captain intervention
    5. Coordinate with other agents intelligently
    """

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.tasks_db_path = Path("runtime/autonomous_tasks.json")
        self.tasks: List[TaskOpportunity] = []
        self.agent_profiles: Dict[str, AgentProfile] = {}
        self._load_tasks()
        self._load_agent_profiles()

    def discover_tasks(self) -> List[TaskOpportunity]:
        """
        Scan codebase and discover ALL available task opportunities

        This is the heart of autonomous intelligence - finding work
        """
        discovered = []

        # 1. V2 Violations (highest priority)
        discovered.extend(self._discover_v2_violations())

        # 2. Technical Debt
        discovered.extend(self._discover_tech_debt())

        # 3. TODO/FIXME comments
        discovered.extend(self._discover_code_todos())

        # 4. Optimization opportunities
        discovered.extend(self._discover_optimizations())

        # 5. Missing tests
        discovered.extend(self._discover_test_gaps())

        # Calculate skill match for all agents
        for task in discovered:
            task.skill_match = self._calculate_skill_matches(task)

        self.tasks = discovered
        self._save_tasks()

        return discovered

    def get_optimal_task_for_agent(
        self,
        agent_id: str,
        exclude_types: Optional[List[str]] = None,
        min_roi: float = 0.0
    ) -> Optional[TaskRecommendation]:
        """
        Get the BEST task for a specific agent

        This is THE function that enables autonomous agent work selection
        """
        if not self.tasks:
            self.discover_tasks()

        # Get agent profile
        profile = self._get_or_create_agent_profile(agent_id)

        # Filter available tasks
        available = [
            t for t in self.tasks
            if t.status == "AVAILABLE"
            and t.claimed_by is None
            and (not exclude_types or t.task_type not in exclude_types)
            and t.roi_score >= min_roi
            and not self._has_unmet_blockers(t)
        ]

        if not available:
            return None

        # Score each task for this agent
        recommendations = []
        for task in available:
            rec = self._score_task_for_agent(task, profile)
            recommendations.append(rec)

        # Sort by total score
        recommendations.sort(key=lambda r: r.total_score, reverse=True)

        return recommendations[0] if recommendations else None

    def get_top_n_tasks_for_agent(
        self,
        agent_id: str,
        n: int = 5
    ) -> List[TaskRecommendation]:
        """Get top N task recommendations for agent"""
        if not self.tasks:
            self.discover_tasks()

        profile = self._get_or_create_agent_profile(agent_id)

        available = [
            t for t in self.tasks
            if t.status == "AVAILABLE"
            and t.claimed_by is None
            and not self._has_unmet_blockers(t)
        ]

        recommendations = [
            self._score_task_for_agent(t, profile)
            for t in available
        ]

        recommendations.sort(key=lambda r: r.total_score, reverse=True)
        return recommendations[:n]

    def claim_task(
        self,
        task_id: str,
        agent_id: str
    ) -> bool:
        """Claim a task for an agent"""
        task = self._find_task(task_id)
        if not task:
            return False

        if task.claimed_by is not None:
            return False

        task.claimed_by = agent_id
        task.claimed_at = datetime.now()
        task.status = "CLAIMED"

        self._save_tasks()
        return True

    def start_task(self, task_id: str, agent_id: str) -> bool:
        """Mark task as in progress"""
        task = self._find_task(task_id)
        if not task or task.claimed_by != agent_id:
            return False

        task.status = "IN_PROGRESS"
        self._save_tasks()
        return True

    def complete_task(
        self,
        task_id: str,
        agent_id: str,
        actual_effort: int,
        actual_points: int
    ) -> bool:
        """Mark task as complete and update agent profile"""
        task = self._find_task(task_id)
        if not task or task.claimed_by != agent_id:
            return False

        task.status = "COMPLETED"
        self._save_tasks()

        # Update agent profile
        self._update_agent_profile(
            agent_id, task.task_type, actual_effort, actual_points
        )

        return True

    def generate_autonomous_report(self, agent_id: str) -> str:
        """Generate a report for autonomous agent use"""
        recommendations = self.get_top_n_tasks_for_agent(agent_id, n=5)

        if not recommendations:
            return f"No tasks available for {agent_id}. Consider discovering new tasks."

        report = []
        report.append("=" * 80)
        report.append(f"AUTONOMOUS TASK RECOMMENDATIONS FOR {agent_id}")
        report.append(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")

        for i, rec in enumerate(recommendations, 1):
            task = rec.task
            report.append(
                f"#{i} RECOMMENDATION (Score: {rec.total_score:.2f})")
            report.append(f"Task ID: {task.task_id}")
            report.append(f"Title: {task.title}")
            report.append(
                f"Type: {task.task_type} | Severity: {task.severity}")
            report.append(f"File: {task.file_path}")
            report.append(
                f"Effort: {task.estimated_effort} cycles | Points: {task.estimated_points}")
            report.append(
                f"ROI: {task.roi_score:.2f} | Impact: {task.impact_score:.1f}/10")

            if task.current_lines and task.target_lines:
                report.append(
                    f"Lines: {task.current_lines}→{task.target_lines} ({task.reduction_percent:.0f}% reduction)")

            report.append(
                f"Match Score: {rec.match_score:.2f} | Priority: {rec.priority_score:.2f}")
            report.append("")
            report.append("WHY THIS TASK:")
            for reason in rec.reasoning:
                report.append(f"  ✓ {reason}")
            report.append("")

            if rec.pros:
                report.append("PROS:")
                for pro in rec.pros:
                    report.append(f"  + {pro}")
                report.append("")

            if rec.cons:
                report.append("CONS:")
                for con in rec.cons:
                    report.append(f"  - {con}")
                report.append("")

            report.append(f"SUGGESTED APPROACH: {rec.suggested_approach}")

            if rec.coordination_plan:
                report.append(f"COORDINATION: {rec.coordination_plan}")

            report.append("")
            report.append(
                f"TO CLAIM: python tools/autonomous_task_engine.py --claim {task.task_id} --agent {agent_id}")
            report.append("-" * 80)
            report.append("")

        return "\n".join(report)

    # === PRIVATE METHODS ===

    def _discover_v2_violations(self) -> List[TaskOpportunity]:
        """Discover V2 compliance violations"""
        tasks = []

        try:
            # Run V2 compliance checker
            result = subprocess.run(
                ["python", "tools/v2_compliance_checker.py", ".", "--json"],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_MEDIUM
            )

            if result.returncode == 0:
                report = json.loads(result.stdout)
                violations = report.get("violations", [])

                for v in violations:
                    severity = "CRITICAL" if "CRITICAL" in v.get(
                        "type", "") else "MAJOR"
                    file_path = v.get("file", "")

                    # Estimate effort based on violation type
                    effort = 2 if severity == "CRITICAL" else 1
                    points = 600 if severity == "CRITICAL" else 300

                    # Parse line count if available
                    current_lines = v.get("current_lines")
                    target_lines = v.get("target_lines")
                    reduction = None
                    if current_lines and target_lines:
                        reduction = (
                            (current_lines - target_lines) / current_lines) * 100

                    task = TaskOpportunity(
                        task_id=f"V2-{hash(file_path) % 10000:04d}",
                        title=f"Fix V2 violation in {Path(file_path).name}",
                        description=v.get(
                            "message", "V2 compliance violation"),
                        file_path=file_path,
                        task_type="V2_VIOLATION",
                        severity=severity,
                        estimated_effort=effort,
                        estimated_points=points,
                        roi_score=points / effort,
                        impact_score=9.0 if severity == "CRITICAL" else 7.0,
                        current_lines=current_lines,
                        target_lines=target_lines,
                        reduction_percent=reduction,
                        blockers=[],
                        dependencies=[],
                        coordination_needed=[],
                        skill_match={},
                        claimed_by=None,
                        claimed_at=None,
                        status="AVAILABLE"
                    )
                    tasks.append(task)

        except Exception:
            pass

        return tasks

    def _discover_tech_debt(self) -> List[TaskOpportunity]:
        """Discover technical debt opportunities"""
        tasks = []

        # Look for files with high complexity, long functions, etc.
        for py_file in self.repo_path.rglob("*.py"):
            if "venv" in str(py_file) or "node_modules" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                lines = content.count("\n")

                # Simple heuristic: files >300 lines might need refactoring
                if lines > 300:
                    effort = 3 if lines > 500 else 2
                    points = 400 if lines > 500 else 250

                    task = TaskOpportunity(
                        task_id=f"DEBT-{hash(str(py_file)) % 10000:04d}",
                        title=f"Refactor large file {py_file.name}",
                        description=f"File has {lines} lines, consider modularization",
                        file_path=str(py_file.relative_to(self.repo_path)),
                        task_type="TECH_DEBT",
                        severity="MAJOR",
                        estimated_effort=effort,
                        estimated_points=points,
                        roi_score=points / effort,
                        impact_score=6.0,
                        current_lines=lines,
                        target_lines=int(lines * 0.6),
                        reduction_percent=40.0,
                        blockers=[],
                        dependencies=[],
                        coordination_needed=[],
                        skill_match={},
                        claimed_by=None,
                        claimed_at=None,
                        status="AVAILABLE"
                    )
                    tasks.append(task)

            except Exception:
                pass

        return tasks[:20]  # Limit to top 20

    def _discover_code_todos(self) -> List[TaskOpportunity]:
        """Discover TODO and FIXME comments"""
        tasks = []

        try:
            result = subprocess.run(
                ["git", "grep", "-n", "-E", "TODO|FIXME"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )

            for line in result.stdout.split("\n")[:50]:  # Limit to 50
                if not line:
                    continue

                match = re.match(r"([^:]+):(\d+):(.*)", line)
                if match:
                    file_path, line_num, comment = match.groups()

                    severity = "MAJOR" if "FIXME" in comment else "MINOR"
                    effort = 1
                    points = 150 if severity == "MAJOR" else 50

                    task = TaskOpportunity(
                        task_id=f"TODO-{hash(line) % 10000:04d}",
                        title=f"Address TODO in {Path(file_path).name}:{line_num}",
                        description=comment.strip(),
                        file_path=file_path,
                        task_type="TECH_DEBT",
                        severity=severity,
                        estimated_effort=effort,
                        estimated_points=points,
                        roi_score=points / effort,
                        impact_score=5.0 if severity == "MAJOR" else 3.0,
                        current_lines=None,
                        target_lines=None,
                        reduction_percent=None,
                        blockers=[],
                        dependencies=[],
                        coordination_needed=[],
                        skill_match={},
                        claimed_by=None,
                        claimed_at=None,
                        status="AVAILABLE"
                    )
                    tasks.append(task)

        except Exception:
            pass

        return tasks

    def _discover_optimizations(self) -> List[TaskOpportunity]:
        """Discover optimization opportunities"""
        # Could integrate with complexity analyzer
        return []

    def _discover_test_gaps(self) -> List[TaskOpportunity]:
        """Discover files without tests"""
        tasks = []

        src_files = list(self.repo_path.glob("src/**/*.py"))
        test_files = set(self.repo_path.glob("tests/**/*.py"))

        for src_file in src_files[:30]:  # Limit
            # Check if test exists
            relative = src_file.relative_to(self.repo_path / "src")
            expected_test = self.repo_path / "tests" / f"test_{relative.name}"

            if expected_test not in test_files:
                task = TaskOpportunity(
                    task_id=f"TEST-{hash(str(src_file)) % 10000:04d}",
                    title=f"Add tests for {src_file.name}",
                    description=f"Missing test coverage for {relative}",
                    file_path=str(src_file.relative_to(self.repo_path)),
                    task_type="FEATURE",
                    severity="MINOR",
                    estimated_effort=2,
                    estimated_points=200,
                    roi_score=100.0,
                    impact_score=6.0,
                    current_lines=None,
                    target_lines=None,
                    reduction_percent=None,
                    blockers=[],
                    dependencies=[],
                    coordination_needed=[],
                    skill_match={},
                    claimed_by=None,
                    claimed_at=None,
                    status="AVAILABLE"
                )
                tasks.append(task)

        return tasks

    def _calculate_skill_matches(self, task: TaskOpportunity) -> Dict[str, float]:
        """Calculate how well each agent matches this task"""
        matches = {}

        for agent_id, profile in self.agent_profiles.items():
            score = 0.0

            # Has worked on similar tasks
            if task.task_type in profile.past_work_types:
                score += 0.3

            # Has worked on this file or nearby
            if task.file_path in profile.files_worked:
                score += 0.4

            # Complexity match
            if task.estimated_effort <= 2 and profile.preferred_complexity == "SIMPLE":
                score += 0.2
            elif 2 < task.estimated_effort <= 4 and profile.preferred_complexity == "MODERATE":
                score += 0.2
            elif task.estimated_effort > 4 and profile.preferred_complexity == "COMPLEX":
                score += 0.2

            # Success rate bonus
            score += profile.success_rate * 0.1

            matches[agent_id] = min(score, 1.0)

        return matches

    def _score_task_for_agent(
        self,
        task: TaskOpportunityOpportunity,
        profile: AgentProfile
    ) -> TaskRecommendation:
        """Score a task for a specific agent"""
        # Match score (skill alignment)
        match_score = task.skill_match.get(profile.agent_id, 0.5)

        # Priority score (urgency + impact)
        severity_weight = {"CRITICAL": 1.0, "MAJOR": 0.7, "MINOR": 0.4}
        priority_score = (
            severity_weight.get(task.severity, 0.5) * 0.6 +
            (task.impact_score / 10) * 0.4
        )

        # Total score
        total_score = (match_score * 0.5 + priority_score *
                       0.3 + (task.roi_score / 300) * 0.2)

        # Generate reasoning
        reasoning = []
        if match_score > 0.7:
            reasoning.append("Strong skill match based on past work")
        if task.roi_score > 200:
            reasoning.append(f"High ROI: {task.roi_score:.0f} points/cycle")
        if task.severity == "CRITICAL":
            reasoning.append("Critical priority - high impact")
        if task.estimated_effort <= 2:
            reasoning.append("Quick win - low effort")

        pros = []
        cons = []

        if task.roi_score > 200:
            pros.append(f"Excellent ROI: {task.roi_score:.0f}")
        if task.estimated_effort <= 2:
            pros.append("Fast completion possible")
        if not task.coordination_needed:
            pros.append("No coordination required")

        if task.estimated_effort >= 4:
            cons.append("High effort required")
        if task.coordination_needed:
            cons.append(
                f"Needs coordination with: {', '.join(task.coordination_needed)}")
        if match_score < 0.5:
            cons.append("Outside usual expertise area")

        approach = f"Refactor {task.file_path} into modular components, target {task.reduction_percent:.0f}% reduction" if task.reduction_percent else f"Address {task.task_type.lower()} in {task.file_path}"

        coord_plan = None
        if task.coordination_needed:
            coord_plan = f"Coordinate with {', '.join(task.coordination_needed)} before starting"

        return TaskRecommendation(
            agent_id=profile.agent_id,
            task=task,
            match_score=match_score,
            priority_score=priority_score,
            total_score=total_score,
            reasoning=reasoning,
            pros=pros,
            cons=cons,
            suggested_approach=approach,
            coordination_plan=coord_plan
        )

    def _get_or_create_agent_profile(self, agent_id: str) -> AgentProfile:
        """Get agent profile or create default"""
        if agent_id in self.agent_profiles:
            return self.agent_profiles[agent_id]

        # Create default profile
        profile = AgentProfile(
            agent_id=agent_id,
            specializations=[],
            past_work_types={},
            files_worked=[],
            avg_cycle_time=2.0,
            total_points=0,
            success_rate=0.8,
            preferred_complexity="MODERATE",
            current_workload=0
        )

        self.agent_profiles[agent_id] = profile
        return profile

    def _has_unmet_blockers(self, task: TaskOpportunity) -> bool:
        """Check if task has unmet blockers"""
        # Could check if blocker tasks are completed
        return len(task.blockers) > 0

    def _find_task(self, task_id: str) -> Optional[TaskOpportunity]:
        """Find task by ID"""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def _update_agent_profile(
        self,
        agent_id: str,
        task_type: str,
        effort: int,
        points: int
    ):
        """Update agent profile after task completion"""
        profile = self._get_or_create_agent_profile(agent_id)

        if task_type not in profile.past_work_types:
            profile.past_work_types[task_type] = 0
        profile.past_work_types[task_type] += 1

        profile.total_points += points

        self._save_agent_profiles()

    def _load_tasks(self):
        """Load tasks from disk"""
        if self.tasks_db_path.exists():
            try:
                with open(self.tasks_db_path) as f:
                    data = json.load(f)
                    self.tasks = [TaskOpportunity(**t) for t in data]
            except Exception:
                self.tasks = []

    def _save_tasks(self):
        """Save tasks to disk"""
        self.tasks_db_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tasks_db_path, "w") as f:
            json.dump([asdict(t)
                      for t in self.tasks], f, indent=2, default=str)

    def _load_agent_profiles(self):
        """Load agent profiles"""
        profiles_path = Path("runtime/agent_profiles.json")
        if profiles_path.exists():
            try:
                with open(profiles_path) as f:
                    data = json.load(f)
                    self.agent_profiles = {
                        k: AgentProfile(**v) for k, v in data.items()
                    }
            except Exception:
                pass

    def _save_agent_profiles(self):
        """Save agent profiles"""
        profiles_path = Path("runtime/agent_profiles.json")
        profiles_path.parent.mkdir(parents=True, exist_ok=True)
        with open(profiles_path, "w") as f:
            json.dump(
                {k: asdict(v) for k, v in self.agent_profiles.items()},
                f, indent=2, default=str
            )


def main():
    """CLI for Autonomous Task Engine"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Autonomous Task Discovery & Selection Engine"
    )

    parser.add_argument(
        "--discover",
        action="store_true",
        help="Discover all available tasks"
    )
    parser.add_argument(
        "--agent",
        help="Agent ID for personalized recommendations"
    )
    parser.add_argument(
        "--recommend",
        action="store_true",
        help="Get task recommendations for agent"
    )
    parser.add_argument(
        "--claim",
        help="Claim a task by ID"
    )
    parser.add_argument(
        "--start",
        help="Mark task as in progress"
    )
    parser.add_argument(
        "--complete",
        help="Mark task as complete"
    )
    parser.add_argument(
        "--effort",
        type=int,
        help="Actual effort in cycles (for complete)"
    )
    parser.add_argument(
        "--points",
        type=int,
        help="Actual points earned (for complete)"
    )

    args = parser.parse_args()

    engine = AutonomousTaskEngine()

    if args.discover:
        print("\n🔍 Discovering tasks...")
        tasks = engine.discover_tasks()
        print(f"✅ Discovered {len(tasks)} tasks!")
        print(f"   Saved to: {engine.tasks_db_path}")

        # Summary by type
        by_type = defaultdict(int)
        for t in tasks:
            by_type[t.task_type] += 1

        print("\nBreakdown:")
        for task_type, count in sorted(by_type.items()):
            print(f"  {task_type}: {count}")

    elif args.agent and args.recommend:
        print(engine.generate_autonomous_report(args.agent))

    elif args.claim and args.agent:
        success = engine.claim_task(args.claim, args.agent)
        if success:
            print(f"✅ Task {args.claim} claimed by {args.agent}!")
            print(
                f"To start: python tools/autonomous_task_engine.py --start {args.claim} --agent {args.agent}")
        else:
            print(f"❌ Failed to claim task {args.claim}")

    elif args.start and args.agent:
        success = engine.start_task(args.start, args.agent)
        if success:
            print(f"✅ Task {args.start} started by {args.agent}!")
        else:
            print(f"❌ Failed to start task {args.start}")

    elif args.complete and args.agent and args.effort and args.points:
        success = engine.complete_task(
            args.complete, args.agent, args.effort, args.points
        )
        if success:
            print(f"✅ Task {args.complete} completed by {args.agent}!")
            print(f"   Effort: {args.effort} cycles, Points: {args.points}")
        else:
            print(f"❌ Failed to complete task {args.complete}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

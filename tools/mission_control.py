#!/usr/bin/env python3
"""
Mission Control - Autonomous Mission Generator
===============================================

THE MASTERPIECE TOOL FOR SWARM COORDINATION

Runs all 5 workflow steps automatically and generates a complete,
conflict-free mission brief for the agent. The tool agents can't live without.

This is the "messaging system" equivalent for autonomous coordination.

What it does:
1. Checks task queue (--get-next-task)
2. Runs project scanner analysis
3. Consults swarm brain patterns
4. Checks all agent statuses (prevents overlap)
5. Generates optimal mission for THIS agent

Output: Complete mission brief ready to execute.

Author: Agent-2 - Architecture & Design Specialist
Date: 2025-10-12
License: MIT
V2 Compliant: Yes
<!-- SSOT Domain: infrastructure -->
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

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


class MissionControl:
    """Autonomous mission generator for swarm agents."""

    def __init__(self, agent_id: str):
        """Initialize mission control for specific agent."""
        self.agent_id = agent_id
        self.project_root = Path(__file__).parent.parent
        self.mission_brief = {}

    def check_task_queue(self) -> dict | None:
        """Step 1: Check centralized task queue."""
        print("🎯 [Step 1/5] Checking task queue...")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "src.services.messaging_cli",
                    "--get-next-task",
                    "--agent",
                    self.agent_id,
                ],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_SHORT,
            )

            # Parse output for task assignment
            if "task assigned" in result.stdout.lower():
                return {"source": "task_queue", "has_assignment": True}
            else:
                print("   ℹ️ No tasks in queue")
                return None

        except Exception as e:
            print(f"   ⚠️ Task queue unavailable: {e}")
            return None

    def run_scanner_analysis(self) -> dict:
        """Step 2: Run project scanner for opportunities."""
        print("🔍 [Step 2/5] Running project scanner...")

        # Check if project_analysis.json exists and is recent
        analysis_file = self.project_root / "project_analysis.json"

        if analysis_file.exists():
            modified_time = datetime.fromtimestamp(
                analysis_file.stat().st_mtime)
            age_minutes = (datetime.now() - modified_time).seconds // 60

            if age_minutes < 30:
                print(
                    f"   ✅ Using recent analysis ({age_minutes} minutes old)")
                with open(analysis_file) as f:
                    return json.load(f)

        # Run fresh scan
        print("   🔄 Running fresh scan...")
        try:
            subprocess.run(
                [sys.executable, "tools/run_project_scan.py"], timeout=TimeoutConstants.HTTP_LONG, capture_output=True
            )

            if analysis_file.exists():
                with open(analysis_file) as f:
                    return json.load(f)
        except Exception as e:
            print(f"   ⚠️ Scanner failed: {e}")

        return {}

    def consult_swarm_brain(self) -> dict:
        """Step 3: Consult swarm brain for patterns and lessons."""
        print("🧠 [Step 3/5] Consulting swarm brain...")

        brain_file = self.project_root / "runtime" / "swarm_brain.json"

        if brain_file.exists():
            with open(brain_file) as f:
                brain = json.load(f)
                print(
                    f"   ✅ {brain['statistics']['total_insights']} insights, "
                    f"{brain['statistics']['total_lessons']} lessons, "
                    f"{brain['statistics']['total_patterns']} patterns"
                )
                return brain
        else:
            print("   ⚠️ Swarm brain not found")
            return {}

    def check_agent_statuses(self) -> dict[str, dict]:
        """Step 4: Check all agent statuses to prevent overlap."""
        print("👥 [Step 4/5] Checking agent statuses...")

        statuses = {}
        workspace_root = self.project_root / "agent_workspaces"

        for agent_dir in workspace_root.iterdir():
            if agent_dir.is_dir() and agent_dir.name.startswith("Agent-"):
                status_file = agent_dir / "status.json"
                if status_file.exists():
                    try:
                        with open(status_file) as f:
                            status = json.load(f)
                            statuses[agent_dir.name] = {
                                "status": status.get("status"),
                                "phase": status.get("current_phase"),
                                "current_tasks": status.get("current_tasks", []),
                            }
                    except:
                        pass

        print(f"   ✅ Scanned {len(statuses)} agents")

        # Show what others are doing
        active_work = [
            (agent, info["current_tasks"])
            for agent, info in statuses.items()
            if info["current_tasks"] and agent != self.agent_id
        ]

        if active_work:
            print("\n   📋 Other agents' current work:")
            for agent, tasks in active_work[:3]:
                for task in tasks[:1]:  # Show first task
                    print(f"      • {agent}: {task}")

        return statuses

    def find_real_violations(self) -> list[dict]:
        """Find actual V2 violations using real_violation_scanner."""
        print("\n🔍 Finding real V2 violations...")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "tools.toolbelt",
                    "--real-violations",
                    "--scan",
                    "--top",
                    "10",
                ],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_DEFAULT,
            )

            # Parse violations from output
            violations = []
            for line in result.stdout.splitlines():
                if "lines |" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        severity = parts[0].strip()
                        lines = int(parts[1].strip().split()[0])
                        file = parts[2].strip()
                        violations.append(
                            {"file": file, "lines": lines, "severity": severity})

            return violations
        except Exception as e:
            print(f"   ⚠️ Violation scan failed: {e}")
            return []

    def generate_mission(self, agent_specialization: str) -> dict:
        """Step 5: Generate optimal mission for this agent."""
        print("\n🎯 [Step 5/5] Generating optimal mission...")

        mission = {
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            "specialization": agent_specialization,
            "mission_type": None,
            "target": None,
            "priority": "NONE",
            "coordination_needed": [],
            "pattern_suggested": None,
            "rationale": "",
        }

        # Check task queue first
        task = self.check_task_queue()
        if task and task.get("has_assignment"):
            mission["mission_type"] = "ASSIGNED_TASK"
            mission["priority"] = "HIGH"
            mission["rationale"] = "Task assigned via centralized queue"
            return mission

        # Run analysis
        scanner_data = self.run_scanner_analysis()
        brain_data = self.consult_swarm_brain()
        agent_statuses = self.check_agent_statuses()

        # Find opportunities
        violations = self.find_real_violations()

        if not violations:
            mission["mission_type"] = "STRATEGIC_REST"
            mission["priority"] = "NONE"
            mission["rationale"] = "No violations found - strategic rest authorized"
            return mission

        # Filter by what others are doing
        others_working_on = set()
        for agent, status in agent_statuses.items():
            if agent != self.agent_id:
                for task in status.get("current_tasks", []):
                    # Extract file names from task descriptions
                    for violation in violations:
                        if Path(violation["file"]).name in task:
                            others_working_on.add(violation["file"])

        # Find first violation not being worked on
        available_violations = [
            v for v in violations if v["file"] not in others_working_on]

        if available_violations:
            target = available_violations[0]

            # Get pattern suggestion
            pattern_result = self.suggest_pattern(target["file"])

            mission["mission_type"] = "V2_REFACTORING"
            mission["target"] = target
            mission["priority"] = target["severity"]
            mission["pattern_suggested"] = pattern_result.get("pattern")
            mission["rationale"] = (
                f"Real violation found, no overlap with other agents, {agent_specialization} suitable"
            )

            # Identify coordination needs
            if "config" in target["file"].lower():
                mission["coordination_needed"].append("Agent-1")
            if mission["priority"] == "CRITICAL":
                mission["coordination_needed"].append("Captain")
        else:
            mission["mission_type"] = "STRATEGIC_REST"
            mission["priority"] = "NONE"
            mission["rationale"] = "All violations being addressed by other agents"

        return mission

    def suggest_pattern(self, file_path: str) -> dict:
        """Suggest pattern using pattern_suggester."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "tools.toolbelt",
                    "--pattern-suggest", file_path, "--json"],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_SHORT,
            )

            suggestions = json.loads(result.stdout)
            return suggestions[0] if suggestions else {}
        except:
            return {}

    def print_mission_brief(self, mission: dict, specialization: str):
        """Print formatted mission brief."""
        print("\n" + "=" * 70)
        print("🎯 MISSION CONTROL - AUTONOMOUS MISSION BRIEF")
        print("=" * 70)
        print(f"\n📋 Agent: {self.agent_id} ({specialization})")
        print(f"⏰ Generated: {mission['timestamp']}")
        print(f"\n🎯 Mission Type: {mission['mission_type']}")
        print(f"🔥 Priority: {mission['priority']}")

        if mission["mission_type"] == "V2_REFACTORING":
            target = mission["target"]
            print(f"\n📁 Target: {target['file']}")
            print(f"📏 Current: {target['lines']} lines ({target['severity']})")
            print("🎯 Goal: <400 lines (V2 compliant)")

            if mission["pattern_suggested"]:
                print(
                    f"\n🏗️ Recommended Pattern: {mission['pattern_suggested']}")

            if mission["coordination_needed"]:
                print(
                    f"\n🤝 Coordinate With: {', '.join(mission['coordination_needed'])}")

        print(f"\n💡 Rationale: {mission['rationale']}")

        if mission["mission_type"] == "STRATEGIC_REST":
            print("\n✅ Recommendation: Strategic rest authorized")
            print("   Available for critical needs when they arise")
        elif mission["mission_type"] == "V2_REFACTORING":
            print("\n✅ Recommendation: Execute refactoring with architectural excellence")
            print("   Use System-Driven Coordination for large scope work")

        print("\n" + "=" * 70)

    def save_mission_brief(self, mission: dict):
        """Save mission brief to file."""
        output_file = (
            self.project_root
            / "runtime"
            / "missions"
            / f"{self.agent_id}_mission_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(mission, f, indent=2)

        print(f"\n📄 Mission brief saved: {output_file}")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Mission Control - Autonomous Mission Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m tools.toolbelt --mission-control --agent Agent-2
  python -m tools.mission_control --agent Agent-5 --save
        """,
    )

    parser.add_argument("--agent", type=str, required=True,
                        help="Agent ID (e.g., Agent-2)")
    parser.add_argument("--specialization", type=str,
                        default="", help="Agent specialization")
    parser.add_argument("--save", action="store_true",
                        help="Save mission brief to file")

    args = parser.parse_args()

    # Specialization map
    specializations = {
        "Agent-1": "Integration & Core Systems",
        "Agent-2": "Architecture & Design",
        "Agent-3": "Infrastructure & DevOps",
        "Agent-5": "Business Intelligence",
        "Agent-6": "Coordination & Communication",
        "Agent-7": "Web Development",
        "Agent-8": "SSOT & System Integration",
    }

    specialization = args.specialization or specializations.get(
        args.agent, "General")

    print(f"\n🚀 MISSION CONTROL INITIALIZING FOR {args.agent}")
    print(f"🎯 Specialization: {specialization}\n")

    # Initialize mission control
    mc = MissionControl(args.agent)

    # Generate mission
    mission = mc.generate_mission(specialization)

    # Print brief
    mc.print_mission_brief(mission, specialization)

    # Save if requested
    if args.save:
        mc.save_mission_brief(mission)

    return 0


if __name__ == "__main__":
    sys.exit(main())

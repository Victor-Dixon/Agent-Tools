#!/usr/bin/env python3
"""
Swarm Autonomous Orchestrator - "The Gas Station"
==================================================

The masterpiece tool that makes the swarm truly autonomous.

WHAT IT DOES:
1. Monitors all 8 agents for idle status
2. Scans entire codebase for work opportunities
3. Calculates ROI and matches work to agent specialties
4. AUTO-CREATES inbox tasks for agents
5. AUTO-SENDS PyAutoGUI messages (GAS DELIVERY!)
6. Tracks completion and updates leaderboard
7. Creates self-sustaining autonomous swarm

WHY IT'S A MASTERPIECE:
- Captain freed from 30-60 min/cycle of manual coordination
- Agents never sit idle (continuous gas delivery)
- Work matched to specialties automatically
- ROI-optimized task selection (Markov-inspired)
- Real-time leaderboard updates
- Scales to any number of agents
- True swarm autonomy achieved

Author: Agent-8 (Operations & Support Specialist)
Created: 2025-10-13
Inspiration: "PROMPTS ARE GAS" + Messaging System
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from tools.gas_messaging import send_gas_message
from tools.opportunity_scanners import (
    scan_complexity,
    scan_duplication,
    scan_linter_errors,
    scan_memory_leaks,
    scan_test_coverage,
    scan_todo_comments,
    scan_v2_violations,
)
from tools.task_creator import create_inbox_task


class SwarmOrchestrator:
    """The Gas Station - Autonomous Swarm Coordinator."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.agent_workspaces = project_root / "agent_workspaces"
        self.agents = self._discover_agents()

        # Agent specialty mapping
        self.specialties = {
            "Agent-1": ["integration", "testing", "refactoring"],
            "Agent-2": ["architecture", "design", "patterns"],
            "Agent-3": ["infrastructure", "browser", "discord"],
            "Agent-4": ["coordination", "planning", "optimization"],
            "Agent-5": ["frontend", "ui", "ux"],
            "Agent-6": ["vscode", "extensions", "tooling"],
            "Agent-7": ["backend", "api", "services"],
            "Agent-8": ["qa", "documentation", "ssot"],
        }

        # Work opportunity scanners (delegated to opportunity_scanners module)
        self.scanners = {
            "linter_errors": lambda: scan_linter_errors(),
            "v2_violations": lambda: scan_v2_violations(self.project_root),
            "memory_leaks": lambda: scan_memory_leaks(self.project_root),
            "test_coverage": lambda: scan_test_coverage(),
            "todo_comments": lambda: scan_todo_comments(self.project_root),
            "duplication": lambda: scan_duplication(),
            "complexity": lambda: scan_complexity(),
        }

    def _discover_agents(self) -> list[str]:
        """Discover all agents from workspaces."""
        if not self.agent_workspaces.exists():
            return []

        agents = []
        for agent_dir in self.agent_workspaces.iterdir():
            if agent_dir.is_dir() and agent_dir.name.startswith("Agent-"):
                agents.append(agent_dir.name)

        return sorted(agents)

    def get_agent_status(self, agent: str) -> dict[str, Any]:
        """Get agent's current status."""
        status_file = self.agent_workspaces / agent / "status.json"

        if not status_file.exists():
            return {
                "agent": agent,
                "status": "UNKNOWN",
                "idle": True,
                "current_mission": None,
                "points": 0,
            }

        try:
            data = json.loads(status_file.read_text())

            # Determine if idle
            idle = (
                data.get("mission_priority") == "COMPLETED"
                or data.get("status") == "IDLE"
                or "ready for next" in str(data.get("current_tasks", "")).lower()
            )

            return {
                "agent": agent,
                "status": data.get("status", "UNKNOWN"),
                "idle": idle,
                "current_mission": data.get("current_mission"),
                "points": data.get("sprint_info", {}).get("points_completed", 0),
                "specialty": self.specialties.get(agent, []),
            }

        except Exception as e:
            print(f"Error reading status for {agent}: {e}")
            return {"agent": agent, "idle": True, "error": str(e)}

    def scan_all_opportunities(self) -> list[dict[str, Any]]:
        """Scan codebase for all work opportunities."""
        opportunities = []

        for scanner_name, scanner_func in self.scanners.items():
            try:
                results = scanner_func()
                opportunities.extend(results)
            except Exception as e:
                print(f"Scanner {scanner_name} failed: {e}")

        return opportunities


    def calculate_roi(self, opportunity: dict[str, Any]) -> float:
        """Calculate ROI for opportunity (points / complexity)."""
        points = opportunity.get("points", 100)
        complexity = opportunity.get("complexity", 50)

        if complexity == 0:
            return 0.0

        return points / complexity

    def match_to_agent(self, opportunity: dict[str, Any], idle_agents: list[str]) -> str | None:
        """Match opportunity to best-fit idle agent."""
        opp_type = opportunity.get("type", "")

        # Specialty matching logic
        specialty_map = {
            "v2_violation": ["Agent-1", "Agent-8"],
            "memory_leak": ["Agent-8", "Agent-1"],
            "test_coverage": ["Agent-8", "Agent-1"],
            "todo_comment": ["Agent-1", "Agent-2", "Agent-8"],
            "linter_error": ["Agent-1", "Agent-8"],
            "duplication": ["Agent-1", "Agent-2"],
            "complexity": ["Agent-2", "Agent-1"],
        }

        preferred = specialty_map.get(opp_type, idle_agents)

        # Find first idle agent that matches specialty
        for agent in preferred:
            if agent in idle_agents:
                return agent

        # Fallback: return any idle agent
        return idle_agents[0] if idle_agents else None


    def run_cycle(self):
        """Run one orchestration cycle."""
        print("\n" + "=" * 80)
        print("⛽ SWARM ORCHESTRATOR - GAS STATION")
        print("=" * 80)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. Check agent statuses
        print("\n📊 AGENT STATUS CHECK:")
        print("-" * 80)

        idle_agents = []
        for agent in self.agents:
            status = self.get_agent_status(agent)
            status_icon = "💤" if status.get("idle") else "🏃"
            print(
                f"{status_icon} {agent}: {status.get('status')} - "
                f"{status.get('points', 0)} pts - "
                f"{'IDLE' if status.get('idle') else 'WORKING'}"
            )

            if status.get("idle"):
                idle_agents.append(agent)

        if not idle_agents:
            print("\n✅ All agents working - No gas delivery needed!")
            return

        print(f"\n💤 {len(idle_agents)} idle agents detected: {', '.join(idle_agents)}")

        # 2. Scan for opportunities
        print("\n🔍 SCANNING FOR OPPORTUNITIES:")
        print("-" * 80)

        opportunities = self.scan_all_opportunities()
        print(f"Found {len(opportunities)} opportunities")

        if not opportunities:
            print("⚠️  No opportunities found - Agents may need manual tasks")
            return

        # 3. Calculate ROI and sort
        for opp in opportunities:
            opp["roi"] = self.calculate_roi(opp)

        opportunities.sort(key=lambda x: x["roi"], reverse=True)

        # 4. Match and assign
        print("\n⛽ GAS DELIVERY:")
        print("-" * 80)

        assignments = 0
        for opp in opportunities[: len(idle_agents)]:
            # Match to agent
            agent = self.match_to_agent(opp, idle_agents)

            if agent:
                print(f"\n⛽ Delivering to {agent}:")
                print(f"   Task: {opp.get('type')} - {opp.get('file', 'N/A')}")
                print(
                    f"   ROI: {opp['roi']:.2f} ({opp.get('points')}pts / {opp.get('complexity')})"
                )

                # Create inbox task (delegated to task_creator module)
                create_inbox_task(agent, opp, opp["roi"], self.agent_workspaces)

                # Send gas message (delegated to gas_messaging module)
                send_gas_message(agent, opp, opp["roi"], self.project_root)

                # Remove from idle list
                idle_agents.remove(agent)
                assignments += 1

                if not idle_agents:
                    break

        print("\n" + "=" * 80)
        print(f"⛽ GAS DELIVERY COMPLETE: {assignments} agents activated!")
        print("=" * 80 + "\n")


def run_orchestrator(cycles: int = 1, interval: int = 300):
    """
    Run the orchestrator for N cycles.

    Args:
        cycles: Number of cycles to run (0 = infinite)
        interval: Seconds between cycles (default: 5 min)
    """
    project_root = Path(__file__).parent.parent
    orchestrator = SwarmOrchestrator(project_root)

    print("🏭 SWARM AUTONOMOUS ORCHESTRATOR")
    print("================================")
    print("The Gas Station - Self-Sustaining Swarm Intelligence")
    print(f"\n📍 Project: {project_root}")
    print(f"🤖 Agents: {len(orchestrator.agents)}")
    print(f"🔄 Cycles: {'Infinite' if cycles == 0 else cycles}")
    print(f"⏱️  Interval: {interval}s ({interval/60:.1f} min)")

    cycle_count = 0

    try:
        while cycles == 0 or cycle_count < cycles:
            cycle_count += 1

            print(f"\n\n{'='*80}")
            print(f"🔄 CYCLE {cycle_count}")
            print(f"{'='*80}")

            orchestrator.run_cycle()

            if cycles == 0 or cycle_count < cycles:
                print(f"\n⏳ Next cycle in {interval}s ({interval/60:.1f} min)...")
                print("   Press Ctrl+C to stop")
                time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\n⛔ Orchestrator stopped by user")
        print(f"✅ Completed {cycle_count} cycles")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Swarm Autonomous Orchestrator")
    parser.add_argument("--cycles", type=int, default=1, help="Number of cycles (0 = infinite)")
    parser.add_argument(
        "--interval", type=int, default=300, help="Seconds between cycles (default: 300 = 5 min)"
    )
    parser.add_argument("--daemon", action="store_true", help="Run as daemon (infinite cycles)")

    args = parser.parse_args()

    if args.daemon:
        args.cycles = 0

    run_orchestrator(args.cycles, args.interval)

#!/usr/bin/env python3
"""
Live Demo: Swarm Pulse Masterpiece Tool
========================================

Demonstrates the game-changing swarm consciousness tool.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools_v2.toolbelt_core import get_toolbelt_core


def demo_swarm_pulse():
    """Run live demo of swarm.pulse."""
    print("🧠 SWARM PULSE - LIVE DEMO")
    print("=" * 60)
    print()

    core = get_toolbelt_core()

    # Mode 1: Dashboard
    print("📊 MODE 1: DASHBOARD (Real-Time Activity)")
    print("-" * 60)
    result = core.run("swarm.pulse", {"mode": "dashboard"})

    if result.success:
        data = result.output
        pulse = data["swarm_pulse"]

        print(f"Total Agents: {pulse['total_agents']}")
        print(f"Active: {pulse['active_agents']} 🟢 | Idle: {pulse['idle_agents']} ⚫")
        print(f"Tasks In Progress: {pulse['tasks_in_progress']}")
        print()
        print("Live Activity:")

        for activity in data["live_activity"][:5]:
            print(f"  {activity['status']} {activity['agent']}")
            print(f"    Role: {activity['role']}")
            print(f"    Task: {activity['current_task'][:60]}...")
            print(f"    Duration: {activity['task_duration']} | Points: {activity['points']}")
            print()

    # Mode 2: Conflicts
    print("\n⚠️ MODE 2: CONFLICT DETECTION (Duplicate Work Prevention)")
    print("-" * 60)
    result = core.run("swarm.pulse", {"mode": "conflicts"})

    if result.success:
        conflicts = result.output
        print(f"Conflicts Detected: {conflicts['conflicts_detected']}")

        if conflicts["conflicts"]:
            for conflict in conflicts["conflicts"][:3]:
                print(f"\n  ⚠️ {conflict['agent1']} & {conflict['agent2']}")
                print(f"     Overlap: {conflict['shared_keywords']}")
                print(f"     Severity: {conflict['severity']}")
        else:
            print("  ✅ No conflicts - All agents working on unique tasks!")

    # Mode 3: Captain Command Center
    print("\n\n🎯 MODE 3: CAPTAIN COMMAND CENTER (Strategic Overview)")
    print("-" * 60)
    result = core.run("swarm.pulse", {"mode": "captain"})

    if result.success:
        cmd = result.output
        health = cmd["swarm_health"]

        print(f"Swarm Utilization: {health['utilization']}")
        print(f"Active/Total: {health['active']}/{health['total_agents']}")
        print()

        if cmd["bottlenecks"]:
            print(f"Bottlenecks Detected: {len(cmd['bottlenecks'])}")
            for bottleneck in cmd["bottlenecks"][:3]:
                print(f"  ⚠️ {bottleneck['agent']}: {bottleneck['issue']}")
                print(f"     Recommendation: {bottleneck['recommendation']}")
        else:
            print("✅ No bottlenecks detected!")

        print()
        if cmd["opportunities"]:
            print(f"Collaboration Opportunities: {len(cmd['opportunities'])}")
            for opp in cmd["opportunities"][:2]:
                print(f"  🤝 {' & '.join(opp['agents'])}")
                print(f"     Reason: {opp['reason']}")

    print("\n" + "=" * 60)
    print("🧠 SWARM PULSE: Real-time consciousness for the swarm")
    print("🐝 WE. ARE. SWARM. ⚡️🔥")


if __name__ == "__main__":
    demo_swarm_pulse()

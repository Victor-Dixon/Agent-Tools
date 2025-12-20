"""
Captain's Tool: Quick Leaderboard Update
=========================================

⚠️ DEPRECATED: This tool has been migrated to tools_v2.
Use 'python -m tools_v2.toolbelt captain.update_leaderboard_coord' instead.
This file will be removed in future version.

Migrated to: tools_v2/categories/captain_coordination_tools.py → LeaderboardUpdateTool
Also available in: tools_v2/categories/captain_tools.py → LeaderboardUpdateTool
Registry: captain.update_leaderboard_coord OR captain.update_leaderboard

Updates leaderboard with new points.

Usage: python tools/captain_leaderboard_update.py --agent Agent-1 --points 2000 --task "shared_utilities"

Author: Agent-4 (Captain)
Date: 2025-10-13
Deprecated: 2025-01-27 (Agent-6 - V2 Tools Flattening)
"""

import warnings

warnings.warn(
    "⚠️ DEPRECATED: This tool has been migrated to tools_v2. "
    "Use 'python -m tools_v2.toolbelt captain.update_leaderboard_coord' instead. "
    "This file will be removed in future version.",
    DeprecationWarning,
    stacklevel=2
)

# Legacy compatibility - delegate to tools_v2
# For migration path, use: python -m tools_v2.toolbelt captain.update_leaderboard_coord

import json
from datetime import datetime
from pathlib import Path


def update_leaderboard(agent_id: str, points: int, task: str = ""):
    """Update leaderboard with new completion."""
    # Delegate to tools_v2 adapter
    try:
        from tools_v2.categories.captain_coordination_tools import LeaderboardUpdateTool
        
        tool = LeaderboardUpdateTool()
        result = tool.execute({
            "agent_id": agent_id,
            "points": points,
            "task": task
        }, None)
        
        if result.success:
            print(f"\n{'='*80}")
            print("🏆 LEADERBOARD UPDATED")
            print(f"{'='*80}\n")
            print(f"✅ {agent_id}: +{points} points ({task})")
            print(f"   Total: {result.output.get('total_points', 0)} points")
            print(f"   Completed: {result.output.get('tasks_completed', 0)} tasks\n")
        else:
            print(f"❌ Error: {result.error_message}")
        
        return result.success
    except ImportError:
        # Fallback to original implementation
        leaderboard_file = Path("runtime/leaderboard.json")

        # Load existing
        if leaderboard_file.exists():
            with open(leaderboard_file) as f:
                leaderboard = json.load(f)
        else:
            leaderboard = {}

        # Update agent
        if agent_id not in leaderboard:
            leaderboard[agent_id] = {"total_points": 0, "tasks_completed": 0, "completions": []}

        leaderboard[agent_id]["total_points"] += points
        leaderboard[agent_id]["tasks_completed"] += 1
        leaderboard[agent_id]["completions"].append(
            {"task": task, "points": points, "timestamp": datetime.now().isoformat()}
        )

        # Save
        leaderboard_file.parent.mkdir(parents=True, exist_ok=True)
        with open(leaderboard_file, "w") as f:
            json.dump(leaderboard, f, indent=2)

        # Display
        print(f"\n{'='*80}")
        print("🏆 LEADERBOARD UPDATED")
        print(f"{'='*80}\n")

        print(f"✅ {agent_id}: +{points} points ({task})")
        print(f"   Total: {leaderboard[agent_id]['total_points']} points")
        print(f"   Completed: {leaderboard[agent_id]['tasks_completed']} tasks")

        # Show top agents
        sorted_agents = sorted(leaderboard.items(), key=lambda x: x[1]["total_points"], reverse=True)

        print(f"\n{'='*80}")
        print("🏆 CURRENT LEADERBOARD")
        print(f"{'='*80}\n")

        for i, (agent, data) in enumerate(sorted_agents[:5], 1):
            print(f"{i}. {agent}: {data['total_points']} pts ({data['tasks_completed']} tasks)")

        print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update leaderboard")
    parser.add_argument("--agent", "-a", required=True, help="Agent ID")
    parser.add_argument("--points", "-p", type=int, required=True, help="Points to award")
    parser.add_argument("--task", "-t", default="", help="Task description")

    args = parser.parse_args()

    update_leaderboard(args.agent, args.points, args.task)

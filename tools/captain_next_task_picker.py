"""
Captain's Tool: Next Task Picker (Markov + ROI)
================================================

⚠️ DEPRECATED: This tool has been migrated to tools_v2.
Use 'python -m tools_v2.toolbelt captain.pick_next_task' instead.
This file will be removed in future version.

Migrated to: tools_v2/categories/captain_coordination_tools.py → NextTaskPickerTool
Registry: captain.pick_next_task

Uses Markov optimizer to pick the next optimal task for an agent.

Usage: python tools/captain_next_task_picker.py --agent Agent-1

Author: Agent-4 (Captain)
Date: 2025-10-13
Deprecated: 2025-01-27 (Agent-6 - V2 Tools Flattening)
"""

import json
import argparse
import warnings

warnings.warn(
    "⚠️ DEPRECATED: This tool has been migrated to tools_v2. "
    "Use 'python -m tools_v2.toolbelt captain.pick_next_task' instead. "
    "This file will be removed in future version.",
    DeprecationWarning,
    stacklevel=2
)

# Legacy compatibility - delegate to tools_v2
# For migration path, use: python -m tools_v2.toolbelt captain.pick_next_task


def calculate_roi(points: int, complexity: int, v2: int, autonomy: int):
    """Calculate ROI."""
    reward = points + (v2 * 100) + (autonomy * 200)
    return reward / max(complexity, 1)


def get_next_task_for_agent(agent_id: str, specialty_match_only: bool = False):
    """Get next optimal task for specific agent using ROI."""
    # Delegate to tools_v2 adapter
    try:
        from tools_v2.categories.captain_coordination_tools import NextTaskPickerTool

        tool = NextTaskPickerTool()
        result = tool.execute({
            "agent_id": agent_id,
            "specialty_match_only": specialty_match_only
        }, None)

        if result.success:
            task = result.output.get("recommended_task", {})
            print(f"\n🎯 RECOMMENDED TASK FOR {agent_id}")
            print(f"{'='*80}\n")
            print(f"Task: {task.get('task', 'Unknown')}")
            print(f"ROI: {task.get('roi', 0):.2f}")
            print(f"Points: {task.get('points', 0)}")
            print(f"Complexity: {task.get('complexity', 0)}\n")
            return task
        else:
            print(f"❌ Error: {result.error_message}")
            return None
    except ImportError:
        # Fallback to original implementation (abbreviated for deprecation)
        print("⚠️  Tools_v2 adapter not available. Please migrate to tools_v2.")
        return None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Pick next task for agent")
    parser.add_argument("--agent", "-a", required=True, help="Agent ID")
    parser.add_argument("--specialty-only",
                        action="store_true", help="Only match specialty")

    args = parser.parse_args()

    get_next_task_for_agent(args.agent, args.specialty_only)


if __name__ == "__main__":
    main()

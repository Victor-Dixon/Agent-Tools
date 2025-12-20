#!/usr/bin/env python3
"""
Captain's Tool: Check All Agent Status
=======================================

Quickly check status.json for all 8 agents to see who needs tasks.

⚠️ DEPRECATED: This tool has been migrated to tools_v2.
Use 'python -m tools_v2.toolbelt captain.status_check' instead.
This file will be removed in future version.

Migrated to: tools_v2/categories/captain_tools.py → StatusCheckTool
Registry: captain.status_check

Author: Agent-4 (Captain)
Date: 2025-10-13
Deprecated: 2025-01-27 (Agent-6 - V2 Tools Flattening)
"""

import warnings

warnings.warn(
    "⚠️ DEPRECATED: This tool has been migrated to tools_v2. "
    "Use 'python -m tools_v2.toolbelt captain.status_check' instead. "
    "This file will be removed in future version.",
    DeprecationWarning,
    stacklevel=2
)

# Legacy compatibility - delegate to tools_v2
# For migration path, use: python -m tools_v2.toolbelt captain.status_check

import json
from pathlib import Path


def check_all_agent_status():
    """Check status.json for all agents."""
    # Delegate to tools_v2 adapter
    try:
        from tools_v2.categories.captain_tools import StatusCheckTool
        
        tool = StatusCheckTool()
        result = tool.execute({}, None)
        
        if result.success:
            print("\n" + "=" * 80)
            print("📊 AGENT STATUS OVERVIEW")
            print("=" * 80 + "\n")
            
            for agent, status in result.output.get("all_status", {}).items():
                if "error" not in status:
                    current_task = status.get("current_task", "None")
                    agent_status = status.get("status", "Unknown")
                    print(f"🟢 {agent}: {agent_status} - {current_task}")
                else:
                    print(f"⚠️  {agent}: {status.get('error')}")
            
            idle = result.output.get("idle_agents", [])
            if idle:
                print(f"\n⚠️  IDLE AGENTS: {len(idle)}")
                for agent_info in idle:
                    print(f"  - {agent_info['agent']}: {agent_info['hours_idle']:.1f}h idle")
            print()
        else:
            print(f"❌ Error: {result.error_message}")
    except ImportError:
        # Fallback to original implementation (SSOT)
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.core.constants.agent_constants import AGENT_LIST
        agents = AGENT_LIST

        print("\n" + "=" * 80)
        print("📊 AGENT STATUS OVERVIEW")
        print("=" * 80 + "\n")

        needs_tasks = []
        active = []

        for agent in agents:
            status_file = Path(f"agent_workspaces/{agent}/status.json")

            if status_file.exists():
                try:
                    with open(status_file) as f:
                        status = json.load(f)

                    current_task = status.get("current_task", "None")
                    last_updated = status.get("last_updated", "Unknown")
                    agent_status = status.get("status", "Unknown")

                    # Determine if needs task
                    if not current_task or current_task == "None" or "idle" in agent_status.lower():
                        needs_tasks.append(agent)
                        print(f"⚠️  {agent}: IDLE - Needs task assignment!")
                    else:
                        active.append(agent)
                        print(f"🟢 {agent}: ACTIVE - {current_task}")

                except Exception as e:
                    print(f"⚠️  {agent}: ERROR - {e}")
            else:
                needs_tasks.append(agent)
                print(f"⚠️  {agent}: NO STATUS FILE - Likely idle!")

        print("\n" + "=" * 80)
        print(f"SUMMARY: {len(active)} active, {len(needs_tasks)} need tasks")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    check_all_agent_status()

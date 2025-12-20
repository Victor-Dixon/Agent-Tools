#!/usr/bin/env python3
"""Analyze agent statuses to identify incomplete loops and unclosed work."""

import json
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

agents = ["Agent-1", "Agent-2", "Agent-3", "Agent-5", "Agent-6", "Agent-7", "Agent-8"]

print("=" * 80)
print("INCOMPLETE LOOPS ANALYSIS")
print("=" * 80)

incomplete_loops = []

for agent_id in agents:
    status_file = project_root / f"agent_workspaces/{agent_id}/status.json"
    if not status_file.exists():
        continue
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        current_tasks = status.get('current_tasks', [])
        next_actions = status.get('next_actions', [])
        completed_tasks = status.get('completed_tasks', [])
        
        # Identify incomplete work
        incomplete = []
        
        # Check current tasks for work in progress
        for task in current_tasks if isinstance(current_tasks, list) else []:
            if any(keyword in task.lower() for keyword in ['in progress', 'continue', 'pending', 'awaiting', 'coordinate']):
                incomplete.append({
                    "type": "current_task",
                    "task": task,
                    "status": "in_progress"
                })
        
        # Check next actions for unstarted work
        for action in next_actions if isinstance(next_actions, list) else []:
            if action.startswith("⏳") or "await" in action.lower() or "continue" in action.lower():
                incomplete.append({
                    "type": "next_action",
                    "action": action,
                    "status": "pending"
                })
        
        if incomplete:
            incomplete_loops.append({
                "agent": agent_id,
                "mission": status.get('current_mission', 'N/A'),
                "incomplete_items": incomplete,
                "total_incomplete": len(incomplete)
            })
    
    except Exception as e:
        print(f"❌ Error processing {agent_id}: {e}")

print("\n📋 INCOMPLETE LOOPS BY AGENT:\n")

for loop in incomplete_loops:
    print(f"🔴 {loop['agent']}: {loop['total_incomplete']} incomplete items")
    print(f"   Mission: {loop['mission'][:80]}")
    for item in loop['incomplete_items'][:5]:  # Show first 5
        if item['type'] == 'current_task':
            print(f"   - [IN PROGRESS] {item['task'][:100]}")
        else:
            print(f"   - [PENDING] {item['action'][:100]}")
    if len(loop['incomplete_items']) > 5:
        print(f"   ... and {len(loop['incomplete_items']) - 5} more")
    print()

print("=" * 80)
print(f"TOTAL: {len(incomplete_loops)} agents with incomplete loops")
print("=" * 80)

# Export for assignment creation
output_file = project_root / "docs/captain_reports/incomplete_loops_analysis_2025-12-13.md"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write("# Incomplete Loops Analysis\n")
    f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
    f.write("## Summary\n\n")
    f.write(f"**Total Agents with Incomplete Loops:** {len(incomplete_loops)}\n\n")
    f.write("## Details\n\n")
    for loop in incomplete_loops:
        f.write(f"### {loop['agent']}\n\n")
        f.write(f"**Mission:** {loop['mission']}\n\n")
        f.write(f"**Incomplete Items:** {loop['total_incomplete']}\n\n")
        for i, item in enumerate(loop['incomplete_items'], 1):
            if item['type'] == 'current_task':
                f.write(f"{i}. **Current Task (In Progress):** {item['task']}\n")
            else:
                f.write(f"{i}. **Next Action (Pending):** {item['action']}\n")
        f.write("\n")

print(f"\n✅ Analysis exported to: {output_file}")




#!/usr/bin/env python3
"""
Captain Morning Briefing - Daily Status Summary
Quick overview of swarm status, recent activity, and priorities.

⚠️ DEPRECATED: This tool has been migrated to tools_v2.
Use 'python -m tools_v2.toolbelt captain.morning_briefing' instead.
This file will be removed in future version.

Migrated to: tools_v2/categories/captain_tools_advanced.py → MorningBriefingTool
Registry: captain.morning_briefing

Author: Agent-4 (Captain)
Deprecated: 2025-01-27 (Agent-8 - V2 Tools Flattening)
"""

import warnings

warnings.warn(
    "⚠️ DEPRECATED: This tool has been migrated to tools_v2. "
    "Use 'python -m tools_v2.toolbelt captain.morning_briefing' instead. "
    "This file will be removed in future version.",
    DeprecationWarning,
    stacklevel=2
)

import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))


def get_agent_last_activity(agent_id: str) -> dict:
    """Get last activity timestamp for an agent."""
    workspace = repo_root / "agent_workspaces" / agent_id
    
    if not workspace.exists():
        return {'status': 'unknown', 'last_activity': None}
    
    # Check inbox for recent messages
    inbox = workspace / "inbox"
    if inbox.exists():
        messages = list(inbox.glob("*.md"))
        if messages:
            latest = max(messages, key=lambda p: p.stat().st_mtime)
            last_activity = datetime.fromtimestamp(latest.stat().st_mtime)
            minutes_ago = (datetime.now() - last_activity).total_seconds() / 60
            
            return {
                'status': 'active' if minutes_ago < 60 else 'idle',
                'last_activity': last_activity,
                'minutes_ago': int(minutes_ago)
            }
    
    return {'status': 'idle', 'last_activity': None, 'minutes_ago': None}


def get_recent_completions() -> list:
    """Get recent completion messages from agents."""
    completions = []
    
    for agent_dir in (repo_root / "agent_workspaces").iterdir():
        if not agent_dir.is_dir():
            continue
        
        agent_id = agent_dir.name
        inbox = agent_dir / "inbox"
        
        if not inbox.exists():
            continue
        
        # Check for completion messages in last 24 hours
        for msg_file in inbox.glob("*.md"):
            mtime = datetime.fromtimestamp(msg_file.stat().st_mtime)
            if (datetime.now() - mtime) < timedelta(hours=24):
                content = msg_file.read_text(encoding='utf-8')
                if 'COMPLETE' in content.upper() or 'DONE' in content.upper():
                    completions.append({
                        'agent': agent_id,
                        'file': msg_file.name,
                        'time': mtime,
                        'snippet': content[:200]
                    })
    
    return sorted(completions, key=lambda x: x['time'], reverse=True)


def get_pending_tasks() -> list:
    """Get pending execution orders."""
    tasks = []
    
    for agent_dir in (repo_root / "agent_workspaces").iterdir():
        if not agent_dir.is_dir():
            continue
        
        agent_id = agent_dir.name
        
        # Check for execution orders
        for order_file in agent_dir.glob("*EXECUTION_ORDER*.md"):
            mtime = datetime.fromtimestamp(order_file.stat().st_mtime)
            tasks.append({
                'agent': agent_id,
                'file': order_file.name,
                'assigned': mtime,
                'age_hours': (datetime.now() - mtime).total_seconds() / 3600
            })
    
    return sorted(tasks, key=lambda x: x['assigned'], reverse=True)


def main():
    """Generate morning briefing."""
    
    print(f"☀️  CAPTAIN'S MORNING BRIEFING")
    print(f"=" * 70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"=" * 70)
    print()
    
    # Agent Status
    print("🤖 AGENT STATUS")
    print("-" * 70)
    
    active_count = 0
    idle_count = 0
    
    for i in range(1, 9):
        agent_id = f"Agent-{i}"
        activity = get_agent_last_activity(agent_id)
        
        if activity['status'] == 'active':
            active_count += 1
            emoji = "🟢"
        elif activity['status'] == 'idle':
            idle_count += 1
            emoji = "🟡"
        else:
            emoji = "⚪"
        
        status_str = f"{emoji} {agent_id}: {activity['status'].upper()}"
        if activity['minutes_ago'] is not None:
            status_str += f" (last activity: {activity['minutes_ago']}m ago)"
        
        print(status_str)
    
    print()
    print(f"Summary: {active_count} active, {idle_count} idle, {8-active_count-idle_count} unknown")
    print()
    
    # Recent Completions
    completions = get_recent_completions()
    print("✅ RECENT COMPLETIONS (Last 24h)")
    print("-" * 70)
    
    if completions:
        for comp in completions[:5]:  # Show top 5
            time_str = comp['time'].strftime('%H:%M')
            print(f"{time_str} - {comp['agent']}: {comp['file']}")
            print(f"       {comp['snippet'][:100]}...")
            print()
    else:
        print("No recent completions found.")
        print()
    
    # Pending Tasks
    tasks = get_pending_tasks()
    print("📋 PENDING TASKS")
    print("-" * 70)
    
    if tasks:
        for task in tasks[:5]:  # Show top 5
            age = f"{int(task['age_hours'])}h ago" if task['age_hours'] < 24 else f"{int(task['age_hours']/24)}d ago"
            print(f"{task['agent']}: {task['file']} (assigned {age})")
    else:
        print("No pending execution orders found.")
    
    print()
    
    # Captain's Priorities
    print("🎯 RECOMMENDED PRIORITIES")
    print("-" * 70)
    print("1. ⛽ Send gas to idle agents (activate with messages)")
    print("2. 📨 Process any recent completions (award points)")
    print("3. 📊 Review pending tasks (reassign if stale)")
    print("4. 🔍 Run project scanner for fresh ROI assignments")
    print("5. 💼 Work on own task (lead by example)")
    print()
    
    # Quick Stats
    print("📊 QUICK STATS")
    print("-" * 70)
    print(f"Active agents: {active_count}/8")
    print(f"Recent completions: {len(completions)}")
    print(f"Pending tasks: {len(tasks)}")
    print()
    
    print("=" * 70)
    print("🐝 WE. ARE. SWARM. ⚡")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())


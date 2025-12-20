#!/usr/bin/env python3
"""
Progress Auto-Tracker - Automatic status.json Updates
Agent-8 (QA & Autonomous Systems Specialist)

Purpose: Auto-update status.json based on git commits and work progress
Impact: Never forget status updates, always current!
"""

import argparse
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def get_recent_commits(count: int = 10) -> list:
    """Get recent git commits."""
    try:
        result = subprocess.run(
            ['git', 'log', f'-{count}', '--format=%H|%s|%ad', '--date=short'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        commits = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                hash_val, msg, date = line.split('|', 2)
                commits.append({"hash": hash_val[:8], "message": msg, "date": date})
        return commits
    except Exception as e:
        print(f"⚠️  Could not get git commits: {e}")
        return []


def extract_tasks_from_commits(commits: list) -> Dict[str, list]:
    """Extract completed and current tasks from commit messages."""
    completed = []
    current = []
    
    for commit in commits:
        msg = commit['message']
        
        # Pattern: "feat(agent-8): Something complete"
        if 'complete' in msg.lower() or 'extracted' in msg.lower():
            task = msg.split(':', 1)[-1].strip()
            if task not in completed:
                completed.append(task)
        
        # Pattern: "feat(agent-8): Something in progress"
        elif 'progress' in msg.lower() or 'started' in msg.lower():
            task = msg.split(':', 1)[-1].strip()
            if task not in current:
                current.append(task)
    
    return {"completed": completed[:10], "current": current[:5]}


def update_status_json(agent_id: str, auto_update: bool = True, mission: str = None):
    """Update agent's status.json file."""
    status_file = Path(f"agent_workspaces/{agent_id}/status.json")
    
    if not status_file.exists():
        print(f"❌ Status file not found: {status_file}")
        return False
    
    # Load current status
    try:
        status = json.loads(status_file.read_text())
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in status file: {e}")
        return False
    
    print(f"\n🔄 UPDATING STATUS FOR {agent_id}")
    print(f"   Current last_updated: {status.get('last_updated', 'N/A')}")
    
    # Update timestamp
    old_timestamp = status.get('last_updated')
    status['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Auto-detect tasks from commits if enabled
    if auto_update:
        print(f"\n🔍 Auto-detecting tasks from git commits...")
        commits = get_recent_commits(20)
        tasks = extract_tasks_from_commits(commits)
        
        if tasks['completed']:
            print(f"\n✅ Detected {len(tasks['completed'])} completed tasks:")
            for task in tasks['completed'][:5]:
                print(f"   - {task}")
            
            # Add to completed_tasks (avoiding duplicates)
            current_completed = status.get('completed_tasks', [])
            for task in tasks['completed']:
                if task not in current_completed:
                    current_completed.insert(0, task)
            status['completed_tasks'] = current_completed[:20]  # Keep last 20
        
        if tasks['current']:
            print(f"\n⏳ Detected {len(tasks['current'])} current tasks:")
            for task in tasks['current']:
                print(f"   - {task}")
            status['current_tasks'] = tasks['current']
    
    # Update mission if provided
    if mission:
        old_mission = status.get('current_mission')
        status['current_mission'] = mission
        print(f"\n🎯 Mission updated:")
        print(f"   From: {old_mission}")
        print(f"   To: {mission}")
    
    # Save updated status
    try:
        status_file.write_text(json.dumps(status, indent=2))
        print(f"\n✅ STATUS UPDATED!")
        print(f"   From: {old_timestamp}")
        print(f"   To: {status['last_updated']}")
        return True
    except Exception as e:
        print(f"\n❌ Failed to save status: {e}")
        return False


def show_status(agent_id: str):
    """Show current agent status."""
    status_file = Path(f"agent_workspaces/{agent_id}/status.json")
    
    if not status_file.exists():
        print(f"❌ Status file not found: {status_file}")
        return
    
    try:
        status = json.loads(status_file.read_text())
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return
    
    print(f"\n📊 STATUS: {agent_id}")
    print(f"="*70)
    print(f"Last Updated: {status.get('last_updated', 'N/A')}")
    print(f"Current Mission: {status.get('current_mission', 'N/A')}")
    print(f"FSM State: {status.get('fsm_state', 'N/A')}")
    print(f"Current Cycle: {status.get('current_cycle', 'N/A')}")
    
    print(f"\n📋 Current Tasks:")
    for task in status.get('current_tasks', [])[:5]:
        print(f"  - {task}")
    
    print(f"\n✅ Recent Completions:")
    for task in status.get('completed_tasks', [])[:5]:
        print(f"  - {task}")
    
    print(f"\n🏆 Recent Achievements:")
    for achievement in status.get('achievements', [])[:3]:
        print(f"  - {achievement}")
    
    print(f"="*70)


def main():
    parser = argparse.ArgumentParser(
        description="Swarm Brain CLI - Easy knowledge sharing",
        epilog="Examples:\n"
               "  Share: python tools/swarm_brain_cli.py share --agent Agent-8 --title 'My Learning' --content 'Details'\n"
               "  Search: python tools/swarm_brain_cli.py search --agent Agent-8 --query 'patterns'\n"
               "  Update status: python tools/progress_auto_tracker.py update --agent Agent-8\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update status.json')
    update_parser.add_argument('--agent', required=True, help='Agent ID (e.g., Agent-8)')
    update_parser.add_argument('--mission', help='Update current mission')
    update_parser.add_argument('--no-auto', action='store_true', help='Disable auto-detection from commits')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show current status')
    show_parser.add_argument('--agent', required=True, help='Agent ID')
    
    # Quick update (just timestamp)
    quick_parser = subparsers.add_parser('quick', help='Quick timestamp update')
    quick_parser.add_argument('--agent', required=True, help='Agent ID')
    
    args = parser.parse_args()
    
    if args.command == 'update':
        update_status_json(
            agent_id=args.agent,
            auto_update=not args.no_auto,
            mission=args.mission
        )
    elif args.command == 'show':
        show_status(args.agent)
    elif args.command == 'quick':
        # Just update timestamp
        status_file = Path(f"agent_workspaces/{args.agent}/status.json")
        if status_file.exists():
            status = json.loads(status_file.read_text())
            status['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            status_file.write_text(json.dumps(status, indent=2))
            print(f"✅ {args.agent} timestamp updated!")
        else:
            print(f"❌ Status file not found!")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()


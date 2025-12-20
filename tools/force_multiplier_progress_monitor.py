#!/usr/bin/env python3
"""
Force Multiplier Progress Monitor
=================================

Monitors progress across all force multiplier work for V2 violations refactoring.
Tracks Agent-1, Agent-7, Agent-3, and Agent-8 progress.

Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-12
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

FORCE_MULTIPLIER_AGENTS = ["Agent-1", "Agent-7", "Agent-3", "Agent-8"]
COORDINATOR_AGENT = "Agent-2"

def load_agent_status(agent_id: str) -> Dict[str, Any]:
    """Load agent status.json file."""
    status_file = project_root / "agent_workspaces" / agent_id / "status.json"
    if not status_file.exists():
        return {"error": "status.json not found"}
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}

def extract_v2_progress(status: Dict[str, Any]) -> Dict[str, Any]:
    """Extract V2 violations refactoring progress from agent status."""
    tasks = status.get("current_tasks", [])
    completed = status.get("completed_tasks", [])
    
    # Filter V2-related tasks
    v2_current = [t for t in tasks if any(keyword in str(t).lower() 
                 for keyword in ['v2', 'violation', 'refactor', 'compliance'])]
    v2_completed = [t for t in completed if any(keyword in str(t).lower() 
                    for keyword in ['v2', 'violation', 'refactor', 'compliance'])]
    
    return {
        "v2_tasks_active": len(v2_current),
        "v2_tasks_completed": len(v2_completed),
        "v2_current_tasks": v2_current[:5],  # Top 5
        "v2_completed_tasks": v2_completed[:5],  # Top 5
        "total_tasks": len(tasks),
        "total_completed": len(completed),
    }

def check_recent_activity(agent_id: str) -> Dict[str, Any]:
    """Check for recent activity indicators."""
    workspace = project_root / "agent_workspaces" / agent_id
    
    # Check for recent file modifications
    recent_files = []
    if workspace.exists():
        for file_path in workspace.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.py', '.md', '.json']:
                try:
                    mtime = file_path.stat().st_mtime
                    age_hours = (datetime.now().timestamp() - mtime) / 3600
                    if age_hours < 24:  # Modified in last 24 hours
                        recent_files.append({
                            "file": str(file_path.relative_to(workspace)),
                            "age_hours": round(age_hours, 1)
                        })
                except Exception:
                    pass
    
    # Check inbox for recent messages
    inbox = workspace / "inbox"
    recent_messages = []
    if inbox.exists():
        for msg_file in inbox.glob("*.md"):
            try:
                mtime = msg_file.stat().st_mtime
                age_hours = (datetime.now().timestamp() - mtime) / 3600
                if age_hours < 24:
                    recent_messages.append({
                        "file": msg_file.name,
                        "age_hours": round(age_hours, 1)
                    })
            except Exception:
                pass
    
    return {
        "recent_files": len(recent_files),
        "recent_messages": len(recent_messages),
        "activity_level": "HIGH" if len(recent_files) > 5 or len(recent_messages) > 3 else "MODERATE" if len(recent_files) > 0 or len(recent_messages) > 0 else "LOW"
    }

def generate_progress_report() -> str:
    """Generate comprehensive progress report."""
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("FORCE MULTIPLIER PROGRESS MONITORING REPORT")
    report_lines.append("=" * 70)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Coordinator: {COORDINATOR_AGENT}")
    report_lines.append(f"Monitoring: {', '.join(FORCE_MULTIPLIER_AGENTS)}")
    report_lines.append("")
    
    total_v2_tasks = 0
    total_v2_completed = 0
    
    for agent_id in FORCE_MULTIPLIER_AGENTS:
        status = load_agent_status(agent_id)
        if "error" in status:
            report_lines.append(f"{agent_id}: ❌ {status['error']}")
            continue
        
        v2_progress = extract_v2_progress(status)
        activity = check_recent_activity(agent_id)
        
        total_v2_tasks += v2_progress["v2_tasks_active"]
        total_v2_completed += v2_progress["v2_tasks_completed"]
        
        report_lines.append(f"{agent_id}:")
        report_lines.append(f"  Status: {status.get('status', 'UNKNOWN')}")
        report_lines.append(f"  Mission: {status.get('current_mission', 'N/A')[:80]}")
        report_lines.append(f"  V2 Tasks: {v2_progress['v2_tasks_active']} active, {v2_progress['v2_tasks_completed']} completed")
        report_lines.append(f"  Activity: {activity['activity_level']} ({activity['recent_files']} files, {activity['recent_messages']} messages)")
        
        if v2_progress["v2_current_tasks"]:
            report_lines.append(f"  Current V2 Tasks:")
            for task in v2_progress["v2_current_tasks"]:
                report_lines.append(f"    - {str(task)[:70]}...")
        
        report_lines.append("")
    
    # Summary
    report_lines.append("=" * 70)
    report_lines.append("SUMMARY")
    report_lines.append("=" * 70)
    report_lines.append(f"Total V2 Tasks Active: {total_v2_tasks}")
    report_lines.append(f"Total V2 Tasks Completed: {total_v2_completed}")
    report_lines.append(f"Progress Rate: {round((total_v2_completed / (total_v2_tasks + total_v2_completed) * 100) if (total_v2_tasks + total_v2_completed) > 0 else 0, 1)}%")
    report_lines.append("")
    
    return "\n".join(report_lines)

def main():
    """Main entry point."""
    report = generate_progress_report()
    print(report)
    
    # Save report
    report_file = project_root / "tools" / f"FORCE_MULTIPLIER_PROGRESS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.write_text(report, encoding='utf-8')
    print(f"\n✅ Report saved to: {report_file.name}")

if __name__ == "__main__":
    main()








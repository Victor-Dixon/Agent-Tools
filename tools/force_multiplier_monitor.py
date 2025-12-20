#!/usr/bin/env python3
"""
Force Multiplier Monitor - Real-Time Idle Detection & Task Assignment
======================================================================

Monitors all agents for idleness and automatically assigns tasks to prevent downtime.
Implements force multiplier principles: parallel execution, zero idle time, proactive assignment.

Author: Agent-4 (Captain)
Date: 2025-12-13
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def get_agent_status(agent_id: str) -> Dict:
    """Get agent status with idle detection."""
    status_file = project_root / f"agent_workspaces/{agent_id}/status.json"
    if not status_file.exists():
        return {"exists": False, "idle": True, "reason": "status.json missing"}
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        last_updated_str = status.get('last_updated', '')
        if not last_updated_str:
            return {"exists": True, "idle": True, "reason": "no timestamp"}
        
        # Parse timestamp
        try:
            last_updated = datetime.strptime(last_updated_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                last_updated = datetime.strptime(last_updated_str, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                return {"exists": True, "idle": True, "reason": "timestamp parse error"}
        
        now = datetime.now()
        time_diff = now - last_updated
        minutes_idle = time_diff.total_seconds() / 60
        
        # Idle thresholds
        if minutes_idle > 60:
            idle_status = "IDLE"  # >60 min = definitely idle
        elif minutes_idle > 30:
            idle_status = "WARNING"  # 30-60 min = warning
        else:
            idle_status = "ACTIVE"  # <30 min = active
        
        current_tasks = status.get('current_tasks', [])
        completed_tasks = status.get('completed_tasks', [])
        
        return {
            "exists": True,
            "idle": minutes_idle > 30,
            "idle_status": idle_status,
            "minutes_idle": minutes_idle,
            "last_updated": last_updated_str,
            "current_tasks_count": len(current_tasks),
            "completed_tasks_count": len(completed_tasks),
            "is_finishing": len(current_tasks) <= 1,  # 1 or 0 tasks = finishing soon
        }
    except Exception as e:
        return {"exists": True, "idle": True, "reason": f"error: {e}"}

def get_active_agents() -> List[str]:
    """Get active agents for current mode."""
    try:
        from src.core.agent_mode_manager import get_active_agents
        return get_active_agents()
    except:
        # Fallback to 4-agent mode
        return ["Agent-1", "Agent-2", "Agent-3", "Agent-4"]

def identify_idle_agents() -> Tuple[List[str], List[str], List[str]]:
    """Identify idle, warning, and finishing agents.
    
    Returns:
        (idle_agents, warning_agents, finishing_agents)
    """
    active_agents = get_active_agents()
    idle = []
    warning = []
    finishing = []
    
    for agent_id in active_agents:
        status = get_agent_status(agent_id)
        if not status.get("exists"):
            continue
        
        if status.get("idle_status") == "IDLE":
            idle.append((agent_id, status))
        elif status.get("idle_status") == "WARNING":
            warning.append((agent_id, status))
        elif status.get("is_finishing"):
            finishing.append((agent_id, status))
    
    return idle, warning, finishing

def check_dependency_resolution() -> Dict:
    """Check if any dependencies have been resolved."""
    # Check if Agent-2 approval delivered to Agent-1
    inbox_dir = project_root / "agent_workspaces/Agent-1/inbox"
    approval_received = False
    
    if inbox_dir.exists():
        approval_keywords = ['approval', 'approved', 'A2-ARCH', 'architecture review']
        inbox_files = list(inbox_dir.glob("*.md"))
        
        for inbox_file in inbox_files[-10:]:  # Check last 10 files
            try:
                content = inbox_file.read_text(encoding='utf-8')
                if any(kw.lower() in content.lower() for kw in approval_keywords):
                    approval_received = True
                    break
            except:
                pass
    
    return {
        "a2_approval_received": approval_received,
        "a1_unblocked": approval_received,
    }

def main():
    """Main monitoring loop."""
    print("=" * 70)
    print("FORCE MULTIPLIER MONITOR - 4-AGENT MODE")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Get active agents
    active_agents = get_active_agents()
    print(f"Active Agents ({len(active_agents)}): {', '.join(active_agents)}\n")
    
    # Check all agent statuses
    idle, warning, finishing = identify_idle_agents()
    
    # Dependency check
    deps = check_dependency_resolution()
    
    # Report idle agents
    print("🔴 IDLE AGENTS (>60 min):")
    print("-" * 70)
    if idle:
        for agent_id, status in idle:
            minutes = status.get('minutes_idle', 0)
            print(f"  {agent_id}: {minutes:.1f} min idle - RECOVERY REQUIRED")
    else:
        print("  ✅ None")
    print()
    
    # Report warning agents
    print("🟡 WARNING AGENTS (30-60 min):")
    print("-" * 70)
    if warning:
        for agent_id, status in warning:
            minutes = status.get('minutes_idle', 0)
            print(f"  {agent_id}: {minutes:.1f} min - Monitor closely")
    else:
        print("  ✅ None")
    print()
    
    # Report finishing agents
    print("🟢 FINISHING AGENTS (1 or 0 tasks remaining):")
    print("-" * 70)
    if finishing:
        for agent_id, status in finishing:
            tasks = status.get('current_tasks_count', 0)
            print(f"  {agent_id}: {tasks} tasks remaining - Prepare next round")
    else:
        print("  ℹ️  All agents have 2+ tasks")
    print()
    
    # Dependency status
    print("🔗 DEPENDENCY CHAIN STATUS:")
    print("-" * 70)
    if deps["a2_approval_received"]:
        print("  ✅ Agent-2 approval received - Agent-1 UNBLOCKED")
    else:
        print("  ⏳ Agent-2 approval pending - Agent-1 BLOCKED")
    print()
    
    # Action recommendations
    print("=" * 70)
    print("RECOMMENDED ACTIONS:")
    print("=" * 70)
    
    if idle:
        print(f"🚨 URGENT: Assign recovery tasks to {len(idle)} idle agent(s)")
        for agent_id, _ in idle:
            print(f"   - {agent_id}: Send immediate recovery task")
    
    if finishing:
        print(f"📋 PREPARE: Next round for {len(finishing)} finishing agent(s)")
        for agent_id, _ in finishing:
            print(f"   - {agent_id}: Queue next 3 tasks (ready to assign)")
    
    if deps["a2_approval_received"]:
        print("✅ UNBLOCK: Agent-1 ready to proceed with refactors")
        print("   - Send A1-REFAC-EXEC-001 & 002 tasks immediately")
    
    if not idle and not finishing and not deps["a2_approval_received"]:
        print("✅ All systems normal - Continue monitoring")
    
    print("\n💡 Run every 15 minutes for continuous monitoring")

if __name__ == "__main__":
    main()



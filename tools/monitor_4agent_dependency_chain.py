#!/usr/bin/env python3
"""
4-Agent Mode Dependency Chain Monitor
=====================================

Monitors the dependency chain for 4-agent mode tasks:
- A2-ARCH-REVIEW-001 (Agent-2) - BLOCKER
- A1-REFAC-EXEC-001 & 002 (Agent-1) - BLOCKED by A2
- A3-SSOT-TAGS-REMAINDER-001 (Agent-3) - READY

Author: Agent-4 (Captain)
Date: 2025-12-13
"""

import json
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def check_agent_status(agent_id: str) -> dict:
    """Check agent status.json for task progress."""
    status_file = project_root / f"agent_workspaces/{agent_id}/status.json"
    if not status_file.exists():
        return {"exists": False}
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        current_tasks = status.get('current_tasks', [])
        completed_tasks = status.get('completed_tasks', [])
        last_updated = status.get('last_updated', 'N/A')
        
        # Check for task-specific keywords
        task_keywords = {
            'Agent-2': ['architecture', 'review', 'approval', 'A2-ARCH'],
            'Agent-1': ['refactor', 'messaging_infrastructure', 'synthetic_github', 'A1-REFAC'],
            'Agent-3': ['SSOT', 'tags', 'infrastructure', 'A3-SSOT'],
        }
        
        keywords = task_keywords.get(agent_id, [])
        task_mentions = sum(1 for task in current_tasks + completed_tasks 
                          if any(kw.lower() in str(task).lower() for kw in keywords))
        
        return {
            "exists": True,
            "last_updated": last_updated,
            "current_tasks_count": len(current_tasks),
            "completed_tasks_count": len(completed_tasks),
            "task_mentions": task_mentions,
            "current_tasks": current_tasks[:3],  # First 3 for preview
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}

def check_inbox_for_approval(agent_id: str) -> bool:
    """Check if Agent-1 has received approval in inbox."""
    if agent_id != "Agent-1":
        return False
    
    inbox_dir = project_root / f"agent_workspaces/{agent_id}/inbox"
    if not inbox_dir.exists():
        return False
    
    # Check for recent approval messages
    approval_keywords = ['approval', 'approved', 'A2-ARCH', 'architecture review']
    inbox_files = list(inbox_dir.glob("*.md"))
    
    for inbox_file in inbox_files[-10:]:  # Check last 10 files
        try:
            content = inbox_file.read_text(encoding='utf-8')
            if any(kw.lower() in content.lower() for kw in approval_keywords):
                return True
        except:
            pass
    
    return False

def main():
    """Monitor dependency chain status."""
    print("=" * 70)
    print("4-AGENT MODE DEPENDENCY CHAIN MONITOR")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Check Agent-2 (BLOCKER)
    print("🔴 BLOCKER: A2-ARCH-REVIEW-001 (Agent-2)")
    print("-" * 70)
    a2_status = check_agent_status("Agent-2")
    if a2_status.get("exists"):
        print(f"  Last Updated: {a2_status.get('last_updated', 'N/A')}")
        print(f"  Current Tasks: {a2_status.get('current_tasks_count', 0)}")
        print(f"  Task Mentions: {a2_status.get('task_mentions', 0)}")
        if a2_status.get('current_tasks'):
            print(f"  Preview: {a2_status['current_tasks'][0][:80]}...")
    else:
        print("  ❌ Status file not found")
    print()
    
    # Check Agent-1 (BLOCKED)
    print("⏳ BLOCKED: A1-REFAC-EXEC-001 & 002 (Agent-1)")
    print("-" * 70)
    a1_status = check_agent_status("Agent-1")
    approval_received = check_inbox_for_approval("Agent-1")
    
    if a1_status.get("exists"):
        print(f"  Last Updated: {a1_status.get('last_updated', 'N/A')}")
        print(f"  Current Tasks: {a1_status.get('current_tasks_count', 0)}")
        print(f"  Approval Received: {'✅ YES' if approval_received else '❌ NO'}")
        if approval_received:
            print("  ✅ UNBLOCKED - Can proceed with refactors")
        else:
            print("  ⏳ BLOCKED - Waiting for Agent-2 approval")
    else:
        print("  ❌ Status file not found")
    print()
    
    # Check Agent-3 (READY)
    print("🟢 READY: A3-SSOT-TAGS-REMAINDER-001 (Agent-3)")
    print("-" * 70)
    a3_status = check_agent_status("Agent-3")
    if a3_status.get("exists"):
        print(f"  Last Updated: {a3_status.get('last_updated', 'N/A')}")
        print(f"  Current Tasks: {a3_status.get('current_tasks_count', 0)}")
        print(f"  Task Mentions: {a3_status.get('task_mentions', 0)}")
        print("  ✅ READY - Can start immediately (no dependencies)")
    else:
        print("  ❌ Status file not found")
    print()
    
    # Summary
    print("=" * 70)
    print("DEPENDENCY CHAIN STATUS")
    print("=" * 70)
    
    if a2_status.get("task_mentions", 0) > 0:
        print("🟡 Agent-2: Review in progress")
    else:
        print("🔴 Agent-2: Review not started")
    
    if approval_received:
        print("✅ Agent-1: Approval received - UNBLOCKED")
    else:
        print("⏳ Agent-1: Waiting for approval - BLOCKED")
    
    if a3_status.get("task_mentions", 0) > 0:
        print("🟢 Agent-3: SSOT tagging in progress")
    else:
        print("🟡 Agent-3: Ready to start")
    
    print("\n💡 Run this monitor regularly to track dependency chain progress")

if __name__ == "__main__":
    main()



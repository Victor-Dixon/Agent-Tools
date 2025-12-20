#!/usr/bin/env python3
"""
Auto-Assign Next Round - Proactive Task Assignment System
=========================================================

Automatically assigns next round of tasks when agents finish current work.
Implements zero-idle-time strategy with proactive task queuing.

Author: Agent-4 (Captain)
Date: 2025-12-13
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.services.messaging_infrastructure import ConsolidatedMessagingService

# Task templates for next rounds (contextually grouped)
NEXT_ROUND_TASKS = {
    "Agent-1": {
        "round_after_refactor": """🚨 NEXT ROUND TASKS (3) - Agent-1

After completing messaging_infrastructure.py + synthetic_github.py refactors:

TASK 1: Integration Testing
- Create integration tests for refactored modules
- Test backward compatibility
- Verify no regressions

TASK 2: Self-Validation (QA Workflow)
- Run QA validation on your own refactored modules
- Create validation report
- Fix any issues found

TASK 3: Agent-7 Phase 2D Refactoring
- Begin unified_discord_bot.py Phase 2D refactoring
- Extract remaining command modules
- Target ~900 lines total reduction""",
        
        "recovery_task": """🚨 IMMEDIATE TASK - Agent-1

Quick coordination task while waiting for Agent-2 approval:

TASK: Prepare Refactor Execution Plan
- Document module extraction strategy for messaging_infrastructure.py
- Document module extraction strategy for synthetic_github.py
- Create execution checklist
- Prepare test plan

This prepares you for immediate execution once approval received."""
    },
    
    "Agent-2": {
        "round_after_approval": """🚨 NEXT ROUND TASKS (3) - Agent-2

After completing A2-ARCH-REVIEW-001 approval:

TASK 1: SSOT Verification (FROM Agent-8)
- Verify SSOT tags for 25 core files
- Create verification report
- Coordinate with Agent-3 for infrastructure files

TASK 2: Audit Report Generation (FROM Agent-5)
- Generate Phase 3 audit reports (Web ↔ Analytics, Core ↔ Analytics)
- Complete pre-public audit documentation
- Post audit completion status

TASK 3: Architecture Review for Web Components (FROM Agent-7)
- Review Agent-1 refactored modules
- Review Agent-3 infrastructure refactoring
- Provide architecture guidance as needed""",
        
        "recovery_task": """🚨 IMMEDIATE TASK - Agent-2

Continue architecture review while preparing:

TASK: Architecture Review Progress
- Complete module boundary review
- Finalize import graph analysis
- Prepare approval notes document
- Verify shims strategy"""
    },
    
    "Agent-3": {
        "round_after_ssot": """🚨 NEXT ROUND TASKS (3) - Agent-3

After completing SSOT tags (25 files):

TASK 1: Batch 1 Module 3 Completion
- Complete thea_browser_operations.py extraction (~280 lines)
- Continue Batch 1 Module 4 (thea_browser_core.py)
- Continue Batch 1 Module 5 (main service refactor)

TASK 2: Repository Cleanup Coordination (FROM Agent-6)
- Coordinate repository cleanup with team
- Review cleanup priorities
- Execute approved cleanup actions

TASK 3: Infrastructure Integration Testing (FROM Agent-7)
- Create integration tests for infrastructure refactoring
- Test deployment coordination
- Verify infrastructure stability""",
        
        "recovery_task": """🚨 IMMEDIATE TASK - Agent-3

Continue SSOT tagging work:

TASK: SSOT Tagging Progress
- Complete next 5 infrastructure files
- Run verifier script
- Update coverage report
- Commit progress"""
    },
    
    "Agent-4": {
        "round_after_gates": """🚨 NEXT ROUND TASKS (3) - Agent-4 (Captain)

After completing gatekeeping cycle:

TASK 1: Force Multiplier Optimization
- Analyze parallel execution efficiency
- Optimize task assignment timing
- Improve dependency chain management

TASK 2: QA Validation Coordination
- Coordinate QA validation for Agent-1 refactors
- Coordinate QA validation for Agent-3 infrastructure
- Establish QA workflow improvements

TASK 3: Loop Closure Campaign
- Track incomplete loops across system
- Coordinate loop closure efforts
- Report closure rates and acceleration"""
    }
}

def get_agent_status(agent_id: str) -> dict:
    """Get agent status."""
    status_file = project_root / f"agent_workspaces/{agent_id}/status.json"
    if not status_file.exists():
        return {"exists": False}
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status = json.load(f)
        return {
            "exists": True,
            "current_tasks_count": len(status.get('current_tasks', [])),
            "last_updated": status.get('last_updated', ''),
        }
    except:
        return {"exists": False}

def should_assign_next_round(agent_id: str) -> tuple[bool, str]:
    """Determine if agent needs next round assignment."""
    status = get_agent_status(agent_id)
    if not status.get("exists"):
        return False, "status.json missing"
    
    current_tasks = status.get("current_tasks_count", 0)
    
    # Assign next round if:
    # - 0 tasks (idle)
    # - 1 task (finishing soon)
    if current_tasks == 0:
        return True, "idle - 0 tasks"
    elif current_tasks == 1:
        return True, "finishing - 1 task remaining"
    
    return False, f"active - {current_tasks} tasks remaining"

def get_task_for_agent(agent_id: str, situation: str) -> str:
    """Get appropriate task for agent based on situation."""
    tasks = NEXT_ROUND_TASKS.get(agent_id, {})
    
    if situation == "idle":
        return tasks.get("recovery_task", "⚠️ No recovery task template for this agent")
    elif situation == "finishing":
        return tasks.get("round_after_approval") or tasks.get("round_after_refactor") or tasks.get("round_after_ssot") or "⚠️ No next round template for this agent"
    else:
        return tasks.get("recovery_task", "⚠️ No task template for this agent")

def main():
    """Auto-assign next round to finishing/idle agents."""
    print("=" * 70)
    print("AUTO-ASSIGN NEXT ROUND - PROACTIVE TASK ASSIGNMENT")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        from src.core.agent_mode_manager import get_active_agents
        active_agents = get_active_agents()
    except:
        active_agents = ["Agent-1", "Agent-2", "Agent-3", "Agent-4"]
    
    service = ConsolidatedMessagingService()
    assignments_made = []
    
    print("Checking agents for next round assignment...")
    print("-" * 70)
    
    for agent_id in active_agents:
        should_assign, reason = should_assign_next_round(agent_id)
        
        if should_assign:
            print(f"📋 {agent_id}: {reason} - Assigning next round...")
            
            task_message = get_task_for_agent(agent_id, reason.split()[0])
            
            try:
                result = service.send_message(
                    agent=agent_id,
                    message=task_message,
                    priority="urgent",
                    use_pyautogui=True,
                    wait_for_delivery=False,
                )
                
                if result.get("success"):
                    queue_id = result.get("queue_id", "N/A")
                    assignments_made.append(agent_id)
                    print(f"   ✅ Next round queued (Queue ID: {queue_id})")
                else:
                    print(f"   ❌ Failed: {result.get('message', 'Unknown error')[:60]}")
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:60]}")
        else:
            print(f"✅ {agent_id}: {reason}")
        
        time.sleep(0.5)  # Brief pause between checks
    
    print("\n" + "=" * 70)
    if assignments_made:
        print(f"✅ Next round assigned to {len(assignments_made)} agent(s): {', '.join(assignments_made)}")
    else:
        print("✅ All agents have sufficient tasks - No assignments needed")
    print("\n💡 Run every 15 minutes for continuous proactive assignment")

if __name__ == "__main__":
    main()



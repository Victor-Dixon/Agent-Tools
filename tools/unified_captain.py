#!/usr/bin/env python3
"""
Unified Captain - Consolidated Captain Operations Tool
====================================================

<!-- SSOT Domain: coordination -->

Consolidates all Captain (Agent-4) operations into a single unified tool.
Replaces 23+ individual captain tools with modular captain system.

Captain Categories:
- inbox - Inbox management operations
- coordination - Swarm coordination
- monitoring - Status monitoring
- tasks - Task assignment
- cleanup - Workspace cleanup

Author: Agent-5 (Business Intelligence Specialist) - Executing Agent-8's Consolidation Plan
Date: 2025-12-06
V2 Compliant: Yes
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedCaptain:
    """Unified captain operations system consolidating all captain capabilities."""
    
    def __init__(self):
        """Initialize unified captain."""
        self.project_root = project_root
        self.agent_workspaces = project_root / "agent_workspaces"
        self.captain_inbox = self.agent_workspaces / "Agent-4" / "inbox"
    
    def inbox_analyze(self) -> Dict[str, Any]:
        """Analyze Captain's inbox messages."""
        try:
            from tools.captain_inbox_manager import analyze_inbox
            
            if not self.captain_inbox.exists():
                return {
                    "category": "inbox",
                    "error": f"Inbox not found: {self.captain_inbox}",
                    "timestamp": datetime.now().isoformat()
                }
            
            analysis = analyze_inbox(self.captain_inbox)
            return {
                "category": "inbox",
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Inbox analysis failed: {e}")
            return {
                "category": "inbox",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def inbox_summary(self) -> Dict[str, Any]:
        """Generate inbox summary report."""
        try:
            from tools.captain_inbox_manager import analyze_inbox, generate_summary_report
            
            if not self.captain_inbox.exists():
                return {
                    "category": "inbox",
                    "error": f"Inbox not found: {self.captain_inbox}",
                    "timestamp": datetime.now().isoformat()
                }
            
            analysis = analyze_inbox(self.captain_inbox)
            report = generate_summary_report(analysis)
            
            return {
                "category": "inbox",
                "summary": report,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Inbox summary failed: {e}")
            return {
                "category": "inbox",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def coordination_assign_tasks(self, tasks: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Assign tasks to agents using swarm coordinator."""
        try:
            from tools.captain_task_assigner import CaptainTaskAssigner
            
            assigner = CaptainTaskAssigner()
            
            if tasks:
                # Assign provided tasks
                assignments = []
                for task in tasks:
                    assignment = assigner.coordinator.assign_task_to_agent(
                        agent_id=task.get("agent"),
                        task=task.get("task"),
                        priority=task.get("priority", "NORMAL"),
                        description=task.get("description", ""),
                    )
                    assignments.append(assignment)
                return {
                    "category": "coordination",
                    "action": "assign_tasks",
                    "assignments": assignments,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Assign critical tasks
                assigner.assign_critical_tasks()
                return {
                    "category": "coordination",
                    "action": "assign_critical_tasks",
                    "status": "completed",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Task assignment failed: {e}")
            return {
                "category": "coordination",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def coordination_close_loops(self) -> Dict[str, Any]:
        """Close open loops using loop closer."""
        try:
            from tools.captain_loop_closer import CaptainLoopCloser
            
            closer = CaptainLoopCloser()
            closer.load_loop_tracker()
            
            closable = closer.identify_closable_loops()
            blockers = closer.identify_blockers()
            
            return {
                "category": "coordination",
                "action": "close_loops",
                "closable_loops": closable,
                "blockers": blockers,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Loop closing failed: {e}")
            return {
                "category": "coordination",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def monitoring_status_check(self) -> Dict[str, Any]:
        """Check all agent statuses."""
        try:
            from tools.captain_swarm_coordinator import CaptainSwarmCoordinator
            
            coordinator = CaptainSwarmCoordinator()
            statuses = coordinator.check_all_agent_statuses()
            
            return {
                "category": "monitoring",
                "action": "status_check",
                "agent_statuses": statuses,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {
                "category": "monitoring",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def monitoring_find_idle(self, hours_threshold: int = 1) -> Dict[str, Any]:
        """Find idle agents."""
        try:
            from tools.captain_find_idle_agents import find_idle_agents
            
            idle_agents = find_idle_agents(hours_threshold)
            
            return {
                "category": "monitoring",
                "action": "find_idle",
                "idle_agents": idle_agents,
                "threshold_hours": hours_threshold,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Find idle agents failed: {e}")
            return {
                "category": "monitoring",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def tasks_assign(self, agent: str = None, task: str = None, priority: str = "NORMAL") -> Dict[str, Any]:
        """Assign a task to an agent."""
        try:
            from tools.captain_task_assigner import CaptainTaskAssigner
            
            assigner = CaptainTaskAssigner()
            
            if agent and task:
                assignment = assigner.coordinator.assign_task_to_agent(
                    agent_id=agent,
                    task=task,
                    priority=priority,
                    description="",
                )
                return {
                    "category": "tasks",
                    "action": "assign",
                    "assignment": assignment,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "category": "tasks",
                    "error": "Agent and task required",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Task assignment failed: {e}")
            return {
                "category": "tasks",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def cleanup_workspace(self, days_old: int = 30, dry_run: bool = False) -> Dict[str, Any]:
        """Clean up Captain workspace."""
        try:
            from tools.captain_workspace_cleanup import CaptainWorkspaceCleanup
            
            cleanup = CaptainWorkspaceCleanup()
            result = cleanup.cleanup_workspace(days_old=days_old, dry_run=dry_run)
            
            return {
                "category": "cleanup",
                "action": "workspace",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Workspace cleanup failed: {e}")
            return {
                "category": "cleanup",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


def main():
    """CLI entry point for unified captain tool."""
    parser = argparse.ArgumentParser(
        description="Unified Captain Operations Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m tools.unified_captain inbox analyze
  python -m tools.unified_captain inbox summary
  python -m tools.unified_captain coordination assign-tasks
  python -m tools.unified_captain coordination close-loops
  python -m tools.unified_captain monitoring status-check
  python -m tools.unified_captain monitoring find-idle
  python -m tools.unified_captain tasks assign --agent Agent-1 --task "Test task"
  python -m tools.unified_captain cleanup workspace --agent Agent-1
        """
    )
    
    parser.add_argument(
        "category",
        choices=["inbox", "coordination", "monitoring", "tasks", "cleanup"],
        help="Captain operation category"
    )
    
    parser.add_argument(
        "action",
        help="Action to perform within category"
    )
    
    # Inbox actions
    parser.add_argument("--output", type=Path, help="Output file for reports")
    
    # Task assignment
    parser.add_argument("--agent", help="Agent ID for task assignment")
    parser.add_argument("--task", help="Task description")
    parser.add_argument("--priority", default="NORMAL", help="Task priority")
    
    # Monitoring
    parser.add_argument("--hours", type=int, default=1, help="Hours threshold for idle detection")
    
    # Cleanup
    parser.add_argument("--days", type=int, default=30, help="Archive files older than N days")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be cleaned without cleaning")
    
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    captain = UnifiedCaptain()
    results = {}
    
    # Route to appropriate category method
    if args.category == "inbox":
        if args.action == "analyze":
            results = captain.inbox_analyze()
        elif args.action == "summary":
            results = captain.inbox_summary()
        else:
            results = {"error": f"Unknown inbox action: {args.action}"}
    
    elif args.category == "coordination":
        if args.action == "assign-tasks" or args.action == "assign":
            results = captain.coordination_assign_tasks()
        elif args.action == "close-loops" or args.action == "close":
            results = captain.coordination_close_loops()
        else:
            results = {"error": f"Unknown coordination action: {args.action}"}
    
    elif args.category == "monitoring":
        if args.action == "status-check" or args.action == "status":
            results = captain.monitoring_status_check()
        elif args.action == "find-idle" or args.action == "idle":
            results = captain.monitoring_find_idle(args.hours)
        else:
            results = {"error": f"Unknown monitoring action: {args.action}"}
    
    elif args.category == "tasks":
        if args.action == "assign":
            if args.agent and args.task:
                results = captain.tasks_assign(args.agent, args.task, args.priority)
            else:
                results = {"error": "Agent and task required for assignment"}
        else:
            results = {"error": f"Unknown tasks action: {args.action}"}
    
    elif args.category == "cleanup":
        if args.action == "workspace":
            results = captain.cleanup_workspace(days_old=args.days, dry_run=args.dry_run)
        else:
            results = {"error": f"Unknown cleanup action: {args.action}"}
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        if "error" in results:
            print(f"❌ Error: {results['error']}")
        elif "summary" in results:
            print(results["summary"])
        else:
            print(json.dumps(results, indent=2, default=str))
    
    return 0 if "error" not in results else 1


if __name__ == "__main__":
    sys.exit(main())

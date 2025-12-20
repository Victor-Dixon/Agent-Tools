#!/usr/bin/env python3
"""
Captain Loop Closer
===================

Automates closing of open loops by tracking task completion,
identifying blockers, and reassigning as needed.

Author: Agent-5 (Acting as Captain)
Date: 2025-12-02
Priority: HIGH - Captain Operations
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from captain_swarm_coordinator import CaptainSwarmCoordinator


class CaptainLoopCloser:
    """Automates closing of open loops."""

    def __init__(self):
        """Initialize loop closer."""
        self.coordinator = CaptainSwarmCoordinator()
        self.loop_tracker_file = Path("agent_workspaces/Agent-5/loop_tracker.json")
        self.loop_tracker: Dict[str, Any] = {}

    def load_loop_tracker(self):
        """Load loop tracking data."""
        if self.loop_tracker_file.exists():
            try:
                with open(self.loop_tracker_file, "r", encoding="utf-8") as f:
                    self.loop_tracker = json.load(f)
            except Exception:
                self.loop_tracker = self._create_empty_tracker()
        else:
            self.loop_tracker = self._create_empty_tracker()

    def _create_empty_tracker(self) -> Dict[str, Any]:
        """Create empty loop tracker."""
        return {
            "loops": {},
            "closed_loops": [],
            "blockers": [],
            "last_updated": datetime.now().isoformat(),
        }

    def save_loop_tracker(self):
        """Save loop tracking data."""
        self.loop_tracker["last_updated"] = datetime.now().isoformat()
        self.loop_tracker_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.loop_tracker_file, "w", encoding="utf-8") as f:
            json.dump(self.loop_tracker, f, indent=2)

    def identify_closable_loops(self) -> List[Dict[str, Any]]:
        """Identify loops that can be closed immediately."""
        closable = []
        
        # Check agent statuses for completed tasks
        agent_statuses = self.coordinator.check_all_agent_statuses()
        
        for agent_id, status in agent_statuses.items():
            current_tasks = status.get("current_tasks", [])
            completed_tasks = status.get("completed_tasks", [])
            
            # Find tasks marked complete
            for task in current_tasks:
                if task.startswith("✅") and "COMPLETE" in task:
                    closable.append({
                        "agent": agent_id,
                        "type": "completed_task",
                        "task": task,
                        "status": "ready_to_close",
                    })
        
        return closable

    def identify_blockers(self) -> List[Dict[str, Any]]:
        """Identify blockers preventing loop closure."""
        blockers = []
        
        # Check for critical blockers from technical debt assessment
        tech_debt_file = Path("docs/organization/TECHNICAL_DEBT_ASSESSMENT_2025-12-02.md")
        if tech_debt_file.exists():
            blockers.append({
                "type": "technical_debt",
                "description": "Technical debt blocking next phase",
                "priority": "CRITICAL",
                "blocks": ["Output Flywheel", "File Deletion", "PR Blockers"],
            })
        
        # Check agent statuses for blockers
        agent_statuses = self.coordinator.check_all_agent_statuses()
        for agent_id, status in agent_statuses.items():
            mission = status.get("current_mission", "")
            if "BLOCKED" in mission.upper() or "BLOCKER" in mission.upper():
                blockers.append({
                    "agent": agent_id,
                    "type": "mission_blocker",
                    "description": mission,
                    "priority": status.get("mission_priority", "HIGH"),
                })
        
        return blockers

    def assign_follow_up_tasks(self, closed_loops: List[Dict[str, Any]]):
        """Assign follow-up tasks after closing loops."""
        follow_ups = []
        
        # Identify follow-up opportunities
        for loop in closed_loops:
            if loop.get("type") == "completed_task":
                agent_id = loop.get("agent")
                
                # Check for next actions
                agent_status = self.coordinator.status_cache.get(agent_id, {})
                next_actions = agent_status.get("next_actions", [])
                
                for action in next_actions:
                    if not action.startswith("✅"):
                        follow_ups.append({
                            "agent": agent_id,
                            "task": action,
                            "priority": "MEDIUM",
                            "source": "next_action",
                        })
        
        return follow_ups

    def generate_closure_report(self) -> Dict[str, Any]:
        """Generate loop closure report."""
        closable_loops = self.identify_closable_loops()
        blockers = self.identify_blockers()
        
        report = {
            "report_date": datetime.now().isoformat(),
            "closable_loops": {
                "total": len(closable_loops),
                "by_agent": {},
                "loops": closable_loops,
            },
            "blockers": {
                "total": len(blockers),
                "critical": len([b for b in blockers if b.get("priority") == "CRITICAL"]),
                "blockers": blockers,
            },
            "recommendations": [],
        }
        
        # Analyze closable loops by agent
        for loop in closable_loops:
            agent = loop.get("agent", "UNKNOWN")
            report["closable_loops"]["by_agent"][agent] = (
                report["closable_loops"]["by_agent"].get(agent, 0) + 1
            )
        
        # Generate recommendations
        if len(closable_loops) > 10:
            report["recommendations"].append(
                f"Close {len(closable_loops)} completed tasks to clear status"
            )
        
        critical_blockers = [b for b in blockers if b.get("priority") == "CRITICAL"]
        if critical_blockers:
            report["recommendations"].append(
                f"Address {len(critical_blockers)} critical blockers immediately"
            )
        
        return report


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Captain Loop Closer")
    parser.add_argument("--identify-closable", action="store_true", help="Identify closable loops")
    parser.add_argument("--identify-blockers", action="store_true", help="Identify blockers")
    parser.add_argument("--generate-report", action="store_true", help="Generate closure report")
    
    args = parser.parse_args()
    
    closer = CaptainLoopCloser()
    closer.load_loop_tracker()
    
    if args.identify_closable:
        closable = closer.identify_closable_loops()
        print(json.dumps(closable, indent=2))
    
    if args.identify_blockers:
        blockers = closer.identify_blockers()
        print(json.dumps(blockers, indent=2))
    
    if args.generate_report:
        report = closer.generate_closure_report()
        
        report_file = Path("agent_workspaces/Agent-5/loop_closure_report.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Loop closure report generated: {report_file}")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()





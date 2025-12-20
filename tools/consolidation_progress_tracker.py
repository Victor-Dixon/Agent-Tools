#!/usr/bin/env python3
"""
Consolidation Progress Tracker
==============================

Tool to track consolidation progress across all agents and patterns.
Helps identify what's been consolidated, what's remaining, and progress metrics.

V2 Compliance: < 300 lines, single responsibility.

Author: Agent-2 (Architecture & Design Specialist)
Date: 2025-12-06
License: MIT
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class ConsolidationProgressTracker:
    """Track consolidation progress across all agents and patterns."""

    def __init__(self, workspace_root: str = "agent_workspaces"):
        """Initialize tracker."""
        self.workspace_root = Path(workspace_root)
        self.agents = ["Agent-1", "Agent-2", "Agent-3", "Agent-4", "Agent-5", "Agent-6", "Agent-7", "Agent-8"]

    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status for a specific agent."""
        status_file = self.workspace_root / agent_id / "status.json"
        if not status_file.exists():
            return {"error": f"Status file not found for {agent_id}"}

        try:
            with open(status_file, "r") as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Error reading status: {e}"}

    def get_all_agent_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all agents."""
        statuses = {}
        for agent_id in self.agents:
            statuses[agent_id] = self.get_agent_status(agent_id)
        return statuses

    def get_consolidation_progress(self) -> Dict[str, Any]:
        """Get overall consolidation progress."""
        statuses = self.get_all_agent_statuses()
        
        progress = {
            "timestamp": datetime.now().isoformat(),
            "agents": {},
            "summary": {
                "total_agents": len(self.agents),
                "active_agents": 0,
                "completed_tasks": 0,
                "in_progress_tasks": 0
            }
        }

        for agent_id, status in statuses.items():
            if "error" in status:
                continue

            agent_progress = {
                "agent_id": agent_id,
                "agent_name": status.get("agent_name", "Unknown"),
                "status": status.get("status", "Unknown"),
                "current_mission": status.get("current_mission", "None"),
                "mission_priority": status.get("mission_priority", "Unknown"),
                "current_tasks_count": len(status.get("current_tasks", [])),
                "completed_tasks_count": len(status.get("completed_tasks", [])),
                "current_tasks": status.get("current_tasks", []),
                "completed_tasks": status.get("completed_tasks", [])
            }

            progress["agents"][agent_id] = agent_progress

            if status.get("status") == "ACTIVE_AGENT_MODE":
                progress["summary"]["active_agents"] += 1

            progress["summary"]["completed_tasks"] += len(status.get("completed_tasks", []))
            progress["summary"]["in_progress_tasks"] += len(status.get("current_tasks", []))

        return progress

    def print_progress_summary(self):
        """Print progress summary to console."""
        progress = self.get_consolidation_progress()
        
        print("=" * 60)
        print("📊 CONSOLIDATION PROGRESS SUMMARY")
        print("=" * 60)
        print(f"Timestamp: {progress['timestamp']}")
        print(f"\nSummary:")
        print(f"  Total Agents: {progress['summary']['total_agents']}")
        print(f"  Active Agents: {progress['summary']['active_agents']}")
        print(f"  Completed Tasks: {progress['summary']['completed_tasks']}")
        print(f"  In Progress Tasks: {progress['summary']['in_progress_tasks']}")
        
        print(f"\nAgent Status:")
        for agent_id, agent_data in progress["agents"].items():
            if "error" in agent_data:
                continue
            print(f"\n  {agent_id} ({agent_data['agent_name']}):")
            print(f"    Status: {agent_data['status']}")
            print(f"    Mission: {agent_data['current_mission']}")
            print(f"    Priority: {agent_data['mission_priority']}")
            print(f"    Current Tasks: {agent_data['current_tasks_count']}")
            print(f"    Completed Tasks: {agent_data['completed_tasks_count']}")

    def export_progress_json(self, output_file: str = "consolidation_progress.json"):
        """Export progress to JSON file."""
        progress = self.get_consolidation_progress()
        
        with open(output_file, "w") as f:
            json.dump(progress, f, indent=2)
        
        print(f"✅ Progress exported to {output_file}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Track consolidation progress")
    parser.add_argument("--agent", help="Get status for specific agent")
    parser.add_argument("--summary", action="store_true", help="Print progress summary")
    parser.add_argument("--export", help="Export progress to JSON file")
    
    args = parser.parse_args()
    
    tracker = ConsolidationProgressTracker()
    
    if args.agent:
        status = tracker.get_agent_status(args.agent)
        print(json.dumps(status, indent=2))
    elif args.summary:
        tracker.print_progress_summary()
    elif args.export:
        tracker.export_progress_json(args.export)
    else:
        tracker.print_progress_summary()


if __name__ == "__main__":
    main()

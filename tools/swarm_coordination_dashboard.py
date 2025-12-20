#!/usr/bin/env python3
"""
Swarm Coordination Dashboard - Tool I Wished I Had
==================================================

A comprehensive dashboard tool for Agent-4 (Captain) to monitor swarm coordination,
active work streams, task progress, and coordination metrics in real-time.

Features:
- Real-time swarm status overview
- Active work stream monitoring
- Coordination message tracking
- Task progress visualization
- Blocker identification
- Force multiplier metrics
- Bilateral coordination status

Usage:
    python tools/swarm_coordination_dashboard.py
    python tools/swarm_coordination_dashboard.py --agent Agent-1
    python tools/swarm_coordination_dashboard.py --refresh 30

Author: Agent-4 (Captain - Strategic Oversight)
V2 Compliant: <400 lines
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class SwarmCoordinationDashboard:
    """Comprehensive swarm coordination dashboard for Captain."""
    
    def __init__(self):
        self.agent_workspaces = project_root / "agent_workspaces"
        self.master_task_log = project_root / "MASTER_TASK_LOG.md"
        self.swarm_brain = project_root / "swarm_brain"
        
    def load_agent_status(self, agent_id: str) -> Optional[Dict]:
        """Load agent status.json."""
        status_file = self.agent_workspaces / agent_id / "status.json"
        if not status_file.exists():
            return None
        
        try:
            return json.loads(status_file.read_text(encoding='utf-8'))
        except Exception:
            return None
    
    def get_all_agents(self) -> List[str]:
        """Get list of all agents."""
        agents = []
        for i in range(1, 9):
            agent_id = f"Agent-{i}"
            status_file = self.agent_workspaces / agent_id / "status.json"
            if status_file.exists():
                agents.append(agent_id)
        return agents
    
    def parse_master_task_log(self) -> Dict:
        """Parse MASTER_TASK_LOG.md for task information."""
        if not self.master_task_log.exists():
            return {"inbox": [], "this_week": [], "waiting_on": [], "parked": []}
        
        content = self.master_task_log.read_text(encoding='utf-8')
        
        tasks = {
            "inbox": [],
            "this_week": [],
            "waiting_on": [],
            "parked": []
        }
        
        current_section = None
        for line in content.split('\n'):
            if line.startswith('## INBOX'):
                current_section = "inbox"
            elif line.startswith('## THIS_WEEK'):
                current_section = "this_week"
            elif line.startswith('## WAITING_ON'):
                current_section = "waiting_on"
            elif line.startswith('## PARKED'):
                current_section = "parked"
            elif line.strip().startswith('- [') and current_section:
                tasks[current_section].append(line.strip())
        
        return tasks
    
    def get_coordination_metrics(self, agent_id: str) -> Dict:
        """Get coordination metrics for an agent."""
        status = self.load_agent_status(agent_id)
        if not status:
            return {}
        
        metrics = {
            "bilateral_coordinations": len(status.get("bilateral_coordination", {})),
            "completed_tasks": len(status.get("completed_tasks", [])),
            "current_tasks": len(status.get("current_tasks", [])),
            "next_actions": len(status.get("next_actions", [])),
            "status": status.get("status", "UNKNOWN"),
            "last_updated": status.get("last_updated", "UNKNOWN")
        }
        
        return metrics
    
    def get_work_stream_summary(self) -> Dict:
        """Get summary of active work streams."""
        work_streams = defaultdict(list)
        
        for agent_id in self.get_all_agents():
            status = self.load_agent_status(agent_id)
            if not status:
                continue
            
            current_tasks = status.get("current_tasks", [])
            for task in current_tasks:
                # Extract work stream category from task
                if "V2 compliance" in task or "refactoring" in task:
                    work_streams["V2 Compliance"].append({
                        "agent": agent_id,
                        "task": task
                    })
                elif "duplicate" in task.lower() or "consolidation" in task.lower():
                    work_streams["Duplicate Consolidation"].append({
                        "agent": agent_id,
                        "task": task
                    })
                elif "toolbelt" in task.lower() or "health check" in task.lower():
                    work_streams["Toolbelt Health"].append({
                        "agent": agent_id,
                        "task": task
                    })
                elif "file splitting" in task.lower():
                    work_streams["File Splitting"].append({
                        "agent": agent_id,
                        "task": task
                    })
                else:
                    work_streams["Other"].append({
                        "agent": agent_id,
                        "task": task
                    })
        
        return dict(work_streams)
    
    def get_blockers(self) -> List[Dict]:
        """Identify current blockers."""
        blockers = []
        
        for agent_id in self.get_all_agents():
            status = self.load_agent_status(agent_id)
            if not status:
                continue
            
            current_blockers = status.get("blockers", {}).get("current", [])
            for blocker in current_blockers:
                blockers.append({
                    "agent": agent_id,
                    "blocker": blocker
                })
        
        return blockers
    
    def generate_dashboard(self, agent_filter: Optional[str] = None) -> str:
        """Generate comprehensive dashboard."""
        lines = []
        lines.append("=" * 80)
        lines.append("SWARM COORDINATION DASHBOARD")
        lines.append("=" * 80)
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # Agent Status Overview
        lines.append("## AGENT STATUS OVERVIEW")
        lines.append("-" * 80)
        
        agents = self.get_all_agents()
        if agent_filter:
            agents = [a for a in agents if agent_filter.lower() in a.lower()]
        
        for agent_id in agents:
            metrics = self.get_coordination_metrics(agent_id)
            status_icon = "✅" if metrics.get("status") == "ACTIVE_AGENT_MODE" else "⏳"
            lines.append(f"{status_icon} {agent_id}:")
            lines.append(f"   Status: {metrics.get('status', 'UNKNOWN')}")
            lines.append(f"   Completed Tasks: {metrics.get('completed_tasks', 0)}")
            lines.append(f"   Current Tasks: {metrics.get('current_tasks', 0)}")
            lines.append(f"   Bilateral Coordinations: {metrics.get('bilateral_coordinations', 0)}")
            lines.append(f"   Last Updated: {metrics.get('last_updated', 'UNKNOWN')}")
            lines.append("")
        
        # Active Work Streams
        lines.append("## ACTIVE WORK STREAMS")
        lines.append("-" * 80)
        
        work_streams = self.get_work_stream_summary()
        for stream_name, tasks in work_streams.items():
            lines.append(f"\n### {stream_name} ({len(tasks)} tasks)")
            for task_info in tasks[:5]:  # Show top 5
                lines.append(f"  - {task_info['agent']}: {task_info['task'][:60]}...")
            if len(tasks) > 5:
                lines.append(f"  ... and {len(tasks) - 5} more")
        
        # Blockers
        lines.append("\n## CURRENT BLOCKERS")
        lines.append("-" * 80)
        
        blockers = self.get_blockers()
        if blockers:
            for blocker_info in blockers:
                lines.append(f"⚠️ {blocker_info['agent']}: {blocker_info['blocker']}")
        else:
            lines.append("✅ No blockers detected")
        
        # Task Summary
        lines.append("\n## TASK SUMMARY")
        lines.append("-" * 80)
        
        tasks = self.parse_master_task_log()
        lines.append(f"Inbox: {len(tasks['inbox'])} tasks")
        lines.append(f"This Week: {len(tasks['this_week'])} tasks")
        lines.append(f"Waiting On: {len(tasks['waiting_on'])} tasks")
        lines.append(f"Parked: {len(tasks['parked'])} tasks")
        
        # Coordination Metrics
        lines.append("\n## COORDINATION METRICS")
        lines.append("-" * 80)
        
        total_bilateral = sum(
            self.get_coordination_metrics(agent_id).get("bilateral_coordinations", 0)
            for agent_id in self.get_all_agents()
        )
        total_completed = sum(
            self.get_coordination_metrics(agent_id).get("completed_tasks", 0)
            for agent_id in self.get_all_agents()
        )
        total_current = sum(
            self.get_coordination_metrics(agent_id).get("current_tasks", 0)
            for agent_id in self.get_all_agents()
        )
        
        lines.append(f"Total Bilateral Coordinations: {total_bilateral}")
        lines.append(f"Total Completed Tasks: {total_completed}")
        lines.append(f"Total Current Tasks: {total_current}")
        lines.append(f"Active Agents: {len([a for a in agents if self.get_coordination_metrics(a).get('status') == 'ACTIVE_AGENT_MODE'])}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def print_dashboard(self, agent_filter: Optional[str] = None):
        """Print dashboard to console."""
        dashboard = self.generate_dashboard(agent_filter)
        print(dashboard)
    
    def save_dashboard(self, output_file: Path, agent_filter: Optional[str] = None):
        """Save dashboard to file."""
        dashboard = self.generate_dashboard(agent_filter)
        output_file.write_text(dashboard, encoding='utf-8')
        print(f"✅ Dashboard saved to: {output_file}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Swarm Coordination Dashboard - Real-time swarm status monitoring"
    )
    
    parser.add_argument('--agent', '-a',
                       help='Filter by agent ID (e.g., Agent-1)')
    parser.add_argument('--output', '-o',
                       help='Save dashboard to file')
    parser.add_argument('--refresh', '-r', type=int,
                       help='Auto-refresh interval in seconds')
    
    args = parser.parse_args()
    
    dashboard = SwarmCoordinationDashboard()
    
    if args.refresh:
        import time
        while True:
            os.system('clear' if os.name != 'nt' else 'cls')
            dashboard.print_dashboard(args.agent)
            print(f"\n🔄 Auto-refreshing every {args.refresh} seconds... (Ctrl+C to stop)")
            time.sleep(args.refresh)
    else:
        dashboard.print_dashboard(args.agent)
        
        if args.output:
            output_file = Path(args.output)
            dashboard.save_dashboard(output_file, args.agent)


if __name__ == '__main__':
    main()

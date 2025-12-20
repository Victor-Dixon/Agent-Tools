#!/usr/bin/env python3
"""
Captain Swarm Coordinator
=========================

Automates captain duties: status checks, task assignment, loop closure,
and swarm coordination as a force multiplier.

Author: Agent-5 (Acting as Captain)
Date: 2025-12-02
Priority: HIGH - Captain Operations
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CaptainSwarmCoordinator:
    """Coordinates swarm operations as Captain."""

    AGENT_WORKSPACES = Path("agent_workspaces")
    
    # Agent specializations for task assignment
    AGENT_SPECIALIZATIONS = {
        "Agent-1": {
            "name": "Integration & Core Systems",
            "focus": ["integration", "core systems", "pipelines", "processors"],
            "coordinates": (-1269, 481),
        },
        "Agent-2": {
            "name": "Architecture & Design",
            "focus": ["architecture", "design", "refactoring", "PR management"],
            "coordinates": (-308, 480),
        },
        "Agent-3": {
            "name": "Infrastructure & DevOps",
            "focus": ["infrastructure", "devops", "testing", "validation"],
            "coordinates": (-1269, 1001),
        },
        "Agent-5": {
            "name": "Business Intelligence",
            "focus": ["analytics", "metrics", "monitoring", "tracking"],
            "coordinates": (652, 421),
        },
        "Agent-6": {
            "name": "Coordination & Communication",
            "focus": ["coordination", "communication", "swarm management"],
            "coordinates": (1612, 419),
        },
        "Agent-7": {
            "name": "Web Development",
            "focus": ["web development", "frontend", "integration", "deployment"],
            "coordinates": (653, 940),
        },
        "Agent-8": {
            "name": "Testing & Quality Assurance",
            "focus": ["testing", "quality_assurance", "test_coverage", "test_infrastructure", "integration_testing"],
            "coordinates": (1611, 941),
        },
    }

    def __init__(self):
        """Initialize coordinator."""
        self.status_cache: Dict[str, Dict[str, Any]] = {}
        self.open_loops: List[Dict[str, Any]] = []
        self.pending_tasks: List[Dict[str, Any]] = []

    def check_all_agent_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Check status of all agents."""
        agent_statuses = {}
        
        for agent_id in self.AGENT_SPECIALIZATIONS.keys():
            status_file = self.AGENT_WORKSPACES / agent_id / "status.json"
            
            if status_file.exists():
                try:
                    with open(status_file, "r", encoding="utf-8") as f:
                        status = json.load(f)
                    agent_statuses[agent_id] = status
                except Exception as e:
                    logger.error(f"Error reading {agent_id} status: {e}")
                    agent_statuses[agent_id] = {"error": str(e)}
            else:
                agent_statuses[agent_id] = {"status": "missing"}
        
        self.status_cache = agent_statuses
        return agent_statuses

    def identify_open_loops(self) -> List[Dict[str, Any]]:
        """Identify open loops from agent statuses and assignments."""
        open_loops = []
        
        # Check each agent's status for incomplete tasks
        for agent_id, status in self.status_cache.items():
            current_tasks = status.get("current_tasks", [])
            next_actions = status.get("next_actions", [])
            
            # Check for incomplete tasks
            for task in current_tasks:
                if not task.startswith("✅"):
                    open_loops.append({
                        "agent": agent_id,
                        "type": "incomplete_task",
                        "description": task,
                        "priority": status.get("mission_priority", "MEDIUM"),
                    })
            
            # Check for pending next actions
            for action in next_actions:
                open_loops.append({
                    "agent": agent_id,
                    "type": "pending_action",
                    "description": action,
                    "priority": "MEDIUM",
                })
        
        # Check for technical debt tasks
        technical_debt_file = Path("docs/organization/TECHNICAL_DEBT_ASSESSMENT_2025-12-02.md")
        if technical_debt_file.exists():
            # This would need parsing, simplified for now
            open_loops.append({
                "type": "technical_debt",
                "description": "Technical debt resolution across swarm",
                "priority": "HIGH",
            })
        
        self.open_loops = open_loops
        return open_loops

    def assign_task_to_agent(
        self,
        agent_id: str,
        task: str,
        priority: str = "MEDIUM",
        description: str = None,
    ) -> Dict[str, Any]:
        """Assign task to agent via inbox message."""
        # Validate agent ID
        valid_agent_ids = {f"Agent-{i}" for i in range(1, 9)}
        if agent_id not in valid_agent_ids:
            raise ValueError(
                f"Invalid agent ID: '{agent_id}'. Must be one of: {', '.join(sorted(valid_agent_ids))}"
            )
        
        inbox_dir = self.AGENT_WORKSPACES / agent_id / "inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        message_file = inbox_dir / f"CAPTAIN_TASK_{timestamp}.md"
        
        message_content = f"""# 🚨 CAPTAIN MESSAGE - TASK ASSIGNMENT

**From**: Captain Agent-5
**To**: {agent_id}
**Priority**: {priority}
**Message ID**: task_{timestamp}
**Timestamp**: {datetime.now().isoformat()}

---

## 📋 TASK ASSIGNMENT

**Task**: {task}

**Priority**: {priority}

{f'**Description**: {description}' if description else ''}

**Assigned**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## ✅ COMPLETION REQUIREMENTS

1. Update your status.json with this task
2. Begin work immediately
3. Report progress regularly
4. Mark complete when done

---

*Message delivered via Captain Swarm Coordinator*

🐝 WE. ARE. SWARM. ⚡🔥
"""
        
        with open(message_file, "w", encoding="utf-8") as f:
            f.write(message_content)
        
        return {
            "agent": agent_id,
            "task": task,
            "message_file": str(message_file),
            "timestamp": timestamp,
        }

    def generate_captain_report(self) -> Dict[str, Any]:
        """Generate comprehensive captain status report."""
        agent_statuses = self.check_all_agent_statuses()
        open_loops = self.identify_open_loops()
        
        report = {
            "report_date": datetime.now().isoformat(),
            "captain": "Agent-5",
            "swarm_status": {
                "total_agents": len(self.AGENT_SPECIALIZATIONS),
                "active_agents": len([s for s in agent_statuses.values() if s.get("status") == "ACTIVE_AGENT_MODE"]),
                "agent_statuses": agent_statuses,
            },
            "open_loops": {
                "total": len(open_loops),
                "by_priority": {},
                "by_agent": {},
                "loops": open_loops,
            },
            "recommendations": [],
        }
        
        # Analyze open loops
        for loop in open_loops:
            priority = loop.get("priority", "MEDIUM")
            agent = loop.get("agent", "UNASSIGNED")
            
            report["open_loops"]["by_priority"][priority] = (
                report["open_loops"]["by_priority"].get(priority, 0) + 1
            )
            
            report["open_loops"]["by_agent"][agent] = (
                report["open_loops"]["by_agent"].get(agent, 0) + 1
            )
        
        # Generate recommendations
        if len(open_loops) > 10:
            report["recommendations"].append(
                "High number of open loops - prioritize and assign tasks immediately"
            )
        
        high_priority_loops = [l for l in open_loops if l.get("priority") == "HIGH"]
        if high_priority_loops:
            report["recommendations"].append(
                f"{len(high_priority_loops)} HIGH priority loops - assign immediately"
            )
        
        return report

    def optimize_captain_pattern(self) -> Dict[str, Any]:
        """Analyze and optimize captain coordination pattern."""
        pattern_analysis = {
            "current_pattern": {
                "status_check_frequency": "on-demand",
                "task_assignment_method": "inbox messages",
                "loop_closure_tracking": "manual",
            },
            "optimizations": [
                {
                    "area": "Status Monitoring",
                    "current": "Manual status file reading",
                    "recommended": "Automated status aggregation with alerts",
                    "impact": "HIGH",
                },
                {
                    "area": "Task Assignment",
                    "current": "Inbox message creation",
                    "recommended": "Automated task queue with priority management",
                    "impact": "HIGH",
                },
                {
                    "area": "Loop Closure",
                    "current": "Manual identification",
                    "recommended": "Automated loop detection and tracking",
                    "impact": "MEDIUM",
                },
                {
                    "area": "Force Multiplier",
                    "current": "Sequential task assignment",
                    "recommended": "Parallel task assignment with dependency tracking",
                    "impact": "HIGH",
                },
            ],
        }
        
        return pattern_analysis


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Captain Swarm Coordinator")
    parser.add_argument("--check-status", action="store_true", help="Check all agent statuses")
    parser.add_argument("--identify-loops", action="store_true", help="Identify open loops")
    parser.add_argument("--generate-report", action="store_true", help="Generate captain report")
    parser.add_argument("--optimize-pattern", action="store_true", help="Optimize captain pattern")
    
    args = parser.parse_args()
    
    coordinator = CaptainSwarmCoordinator()
    
    if args.check_status:
        statuses = coordinator.check_all_agent_statuses()
        print(json.dumps(statuses, indent=2))
    
    if args.identify_loops:
        loops = coordinator.identify_open_loops()
        print(json.dumps(loops, indent=2))
    
    if args.generate_report:
        report = coordinator.generate_captain_report()
        
        report_file = Path("agent_workspaces/Agent-5/CAPTAIN_SWARM_REPORT.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Captain report generated: {report_file}")
        print(json.dumps(report, indent=2))
    
    if args.optimize_pattern:
        analysis = coordinator.optimize_captain_pattern()
        print(json.dumps(analysis, indent=2))


if __name__ == "__main__":
    main()





#!/usr/bin/env python3
"""
Create Cycle Planner Tasks
===========================

Creates cycle planner task files for agents based on identified priorities.

Usage:
    python tools/create_cycle_planner_tasks.py
    python tools/create_cycle_planner_tasks.py --agent Agent-4 --priority high
"""

import argparse
import json
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Any

# Priority tasks identified
PRIORITY_TASKS = {
    "Agent-4": [
        {
            "task_id": "CP-001",
            "title": "Verify CI/CD pipeline is passing after fixes",
            "description": "Monitor latest CI/CD runs to confirm all fixes are working. Check GitHub Actions status and resolve any remaining failures.",
            "priority": "high",
            "status": "pending",
            "assigned_to": "Agent-4",
            "category": "infrastructure",
            "estimated_points": 50,
            "due_date": date.today().isoformat()
        },
        {
            "task_id": "CP-002",
            "title": "Update README to reflect accurate V2 compliance status",
            "description": "README currently claims '100% V2 Compliant' but actual status is ~90% (57 unapproved violations). Update README to reflect accurate status with note about approved exceptions.",
            "priority": "high",
            "status": "completed",
            "assigned_to": "Agent-4",
            "category": "documentation",
            "estimated_points": 75,
            "due_date": date.today().isoformat(),
            "completed_at": datetime.now().isoformat()
        }
    ],
    "Agent-2": [
        {
            "task_id": "CP-005",
            "title": "Review and document V2 compliance exceptions",
            "description": "Document rationale for 57 unapproved violations. Review against exception criteria and either approve exceptions or create refactoring plan.",
            "priority": "medium",
            "status": "pending",
            "assigned_to": "Agent-2",
            "category": "code_quality",
            "estimated_points": 150,
            "due_date": date.today().isoformat()
        },
        {
            "task_id": "CP-006",
            "title": "Refactor top 10 largest V2 violations (>1000 lines)",
            "description": "Refactor largest violations: registry.py (2,380), unified_discord_bot.py (2,321), agent_activity_detector.py (1,666), messaging_infrastructure.py (1,655), repo_safe_merge.py (1,259), enhanced_agent_activity_detector.py (1,215). Break into smaller modules.",
            "priority": "high",
            "status": "pending",
            "assigned_to": "Agent-2",
            "category": "code_quality",
            "estimated_points": 500,
            "due_date": date.today().isoformat()
        }
    ],
    "Agent-3": [
        {
            "task_id": "CP-003",
            "title": "Resolve freerideinvestor.com WordPress admin login issue",
            "description": "WordPress admin login not accessible. Diagnostic tool created. Need to investigate security plugins, .htaccess rules, or access restrictions blocking wp-admin.",
            "priority": "medium",
            "status": "completed",
            "assigned_to": "Agent-3",
            "category": "infrastructure",
            "estimated_points": 100,
            "due_date": date.today().isoformat(),
            "completed_at": datetime.now().isoformat()
        },
        {
            "task_id": "CP-004",
            "title": "Address GitHub CLI authentication blockers",
            "description": "Coordinate resolution of GitHub CLI auth issues preventing repository operations. Document solution for future reference.",
            "priority": "medium",
            "status": "pending",
            "assigned_to": "Agent-3",
            "category": "infrastructure",
            "estimated_points": 75,
            "due_date": date.today().isoformat()
        },
        {
            "task_id": "CP-009",
            "title": "Fix Dream.os CI/CD pipeline failures",
            "description": "CI/CD pipeline failing due to linting errors (ruff), timeout issues (black/isort/pytest), and pyproject.toml deprecation warnings. Fix ruff configuration, exclude archive/temp directories, update pyproject.toml lint section, optimize CI workflow.",
            "priority": "high",
            "status": "in_progress",
            "assigned_to": "Agent-3",
            "category": "infrastructure",
            "estimated_points": 150,
            "due_date": date.today().isoformat()
        },
        {
            "task_id": "CP-010",
            "title": "Optimize CI workflow performance",
            "description": "CI steps timing out (black, isort, pytest). Exclude unnecessary directories (archive, temp_repos, temp), add proper exclusions to pyproject.toml, optimize test execution.",
            "priority": "high",
            "status": "pending",
            "assigned_to": "Agent-3",
            "category": "infrastructure",
            "estimated_points": 100,
            "due_date": date.today().isoformat()
        }
    ],
    "Agent-7": [
        {
            "task_id": "CP-007",
            "title": "Review and refactor medium-sized V2 violations (400-1000 lines)",
            "description": "Review 47 files in 400-1000 line range. Determine which can be refactored vs approved as exceptions. Create refactoring plan for actionable items.",
            "priority": "medium",
            "status": "pending",
            "assigned_to": "Agent-7",
            "category": "code_quality",
            "estimated_points": 300,
            "due_date": date.today().isoformat()
        }
    ],
    "Agent-1": [
        {
            "task_id": "CP-008",
            "title": "Verify all CI workflows are passing consistently",
            "description": "After CI fixes, verify all 8 workflows pass. Monitor for any intermittent failures and ensure stability.",
            "priority": "high",
            "status": "pending",
            "assigned_to": "Agent-1",
            "category": "infrastructure",
            "estimated_points": 50,
            "due_date": date.today().isoformat()
        }
    ]
}


def create_cycle_planner_file(agent_id: str, tasks: List[Dict[str, Any]], output_dir: Path):
    """Create cycle planner JSON file for agent."""
    agent_dir = output_dir / agent_id
    agent_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = date.today().isoformat()
    filename = f"cycle_planner_tasks_{date_str}.json"
    filepath = agent_dir / filename
    
    task_data = {
        "created": datetime.now().isoformat(),
        "agent_id": agent_id,
        "date": date_str,
        "tasks": tasks,
        "pending_tasks": [t for t in tasks if t.get("status") == "pending"],
        "total_tasks": len(tasks),
        "pending_count": len([t for t in tasks if t.get("status") == "pending"])
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(task_data, f, indent=2, ensure_ascii=False)
    
    return filepath


def main():
    parser = argparse.ArgumentParser(description="Create cycle planner tasks")
    parser.add_argument("--agent", help="Agent ID (default: all agents)")
    parser.add_argument("--priority", choices=["high", "medium", "low", "all"], 
                       default="all", help="Filter by priority")
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    agent_workspaces = project_root / "agent_workspaces"
    
    print("=" * 70)
    print("Cycle Planner Task Creator")
    print("=" * 70)
    print()
    
    agents_to_process = [args.agent] if args.agent else PRIORITY_TASKS.keys()
    
    for agent_id in agents_to_process:
        if agent_id not in PRIORITY_TASKS:
            print(f"⚠️  No tasks defined for {agent_id}")
            continue
        
        tasks = PRIORITY_TASKS[agent_id]
        
        # Filter by priority if specified
        if args.priority != "all":
            tasks = [t for t in tasks if t.get("priority") == args.priority]
        
        if not tasks:
            print(f"⚠️  No {args.priority} priority tasks for {agent_id}")
            continue
        
        print(f"📋 Creating tasks for {agent_id}...")
        print(f"   Found {len(tasks)} tasks")
        
        filepath = create_cycle_planner_file(agent_id, tasks, agent_workspaces)
        
        print(f"✅ Created: {filepath.relative_to(project_root)}")
        print()
        
        # Print task summary
        for task in tasks:
            print(f"   • {task['task_id']}: {task['title']} ({task['priority']} priority)")
    
    print("=" * 70)
    print("✅ Cycle planner tasks created!")
    print()
    print("Agents can now claim these tasks using:")
    print("  python -m src.services.messaging_cli --agent Agent-X --get-next-task")
    print()


if __name__ == "__main__":
    main()


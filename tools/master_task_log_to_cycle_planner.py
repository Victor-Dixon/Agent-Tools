#!/usr/bin/env python3
"""
Wire MASTER_TASK_LOG.md to Cycle Planner
========================================

Converts tasks from MASTER_TASK_LOG.md into per-agent cycle planner JSON
files that are consumed by the contract / cycle planner system.

Usage examples:

    # Create cycle planner tasks for Agent-2 from THIS WEEK section
    python tools/master_task_log_to_cycle_planner.py --agent Agent-2 --section THIS_WEEK

    # Create tasks for Agent-3 from INBOX, limited to 5 items
    python tools/master_task_log_to_cycle_planner.py --agent Agent-3 --section INBOX --max-tasks 5

This does NOT modify MASTER_TASK_LOG.md; it only reads from it and writes
cycle planner JSON files under agent_workspaces/<agent_id>/.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional


PROJECT_ROOT = Path(__file__).parent.parent
MASTER_TASK_LOG_PATH = PROJECT_ROOT / "MASTER_TASK_LOG.md"
AGENT_WORKSPACES_DIR = PROJECT_ROOT / "agent_workspaces"

SectionName = Literal["INBOX", "THIS_WEEK", "WAITING_ON", "PARKED"]


@dataclass
class ParsedTask:
    """Represents a single parsed task from MASTER_TASK_LOG.md."""

    raw_line: str
    section: SectionName
    text: str


def detect_section(line: str) -> Optional[SectionName]:
    """Detect logical section from a Markdown heading line."""
    if line.startswith("##") and "INBOX" in line.upper():
        return "INBOX"
    if line.startswith("##") and "THIS WEEK" in line.upper():
        return "THIS_WEEK"
    if line.startswith("##") and "WAITING ON" in line.upper():
        return "WAITING_ON"
    if line.startswith("##") and "PARKED" in line.upper():
        return "PARKED"
    return None


def parse_master_task_log(path: Path) -> List[ParsedTask]:
    """
    Parse MASTER_TASK_LOG.md and return a flat list of tasks with section labels.

    We treat any Markdown checkbox line under a recognized section as a task:
      - [ ] Task text
      - [x] Completed task
    """
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    current_section: Optional[SectionName] = None
    tasks: List[ParsedTask] = []

    for line in lines:
        section = detect_section(line.strip())
        if section:
            current_section = section
            continue

        if not current_section:
            continue

        stripped = line.strip()
        if stripped.startswith("- [") or stripped.startswith("* ["):
            # remove "- [ ]" or "- [x]" prefix
            # formats:
            #   - [ ] Task text
            #   - [x] Task text
            try:
                checkbox_end = stripped.index("]")
                text_part = stripped[checkbox_end + 1 :].strip()
            except ValueError:
                text_part = stripped

            if text_part:
                tasks.append(
                    ParsedTask(
                        raw_line=stripped,
                        section=current_section,
                        text=text_part,
                    )
                )

    return tasks


def build_cycle_planner_payload(
    agent_id: str,
    tasks: List[ParsedTask],
    priority: str = "medium",
) -> Dict[str, Any]:
    """Build a cycle planner JSON payload from parsed tasks."""
    date_str = date.today().isoformat()
    created_at = datetime.now().isoformat()

    cp_tasks: List[Dict[str, Any]] = []

    for idx, task in enumerate(tasks, start=1):
        task_id = f"MTL-{task.section}-{idx}"
        title = task.text
        # Truncate ultra-long titles for safety
        if len(title) > 200:
            title = title[:197] + "..."

        cp_tasks.append(
            {
                "task_id": task_id,
                "title": title,
                "description": f"Imported from MASTER_TASK_LOG.md [{task.section}] on {date_str}",
                "priority": priority.lower(),
                "status": "pending",
                "assigned_to": agent_id,
                "category": "technical_debt",
                "estimated_points": 50,
                "created_from": "MASTER_TASK_LOG",
                "section": task.section,
            }
        )

    return {
        "created": created_at,
        "agent_id": agent_id,
        "date": date_str,
        "tasks": cp_tasks,
        "pending_tasks": [t for t in cp_tasks if t.get("status") == "pending"],
        "total_tasks": len(cp_tasks),
        "pending_count": len([t for t in cp_tasks if t.get("status") == "pending"]),
        "source": "master_task_log_to_cycle_planner",
    }


def write_cycle_planner_file(agent_id: str, payload: Dict[str, Any]) -> Path:
    """Write payload to agent_workspaces/<agent>/cycle_planner_tasks_<date>.json."""
    agent_dir = AGENT_WORKSPACES_DIR / agent_id
    agent_dir.mkdir(parents=True, exist_ok=True)

    date_str = payload.get("date") or date.today().isoformat()
    filename = f"cycle_planner_tasks_{date_str}.json"
    out_path = agent_dir / filename

    out_path.write_text(
        __import__("json").dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return out_path


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert MASTER_TASK_LOG.md tasks into Cycle Planner JSON for an agent."
    )
    parser.add_argument(
        "--agent",
        required=True,
        help="Agent ID (e.g., Agent-2, Agent-3, Agent-4)",
    )
    parser.add_argument(
        "--section",
        choices=["INBOX", "THIS_WEEK", "WAITING_ON", "PARKED"],
        default="THIS_WEEK",
        help="Which section of MASTER_TASK_LOG.md to export tasks from (default: THIS_WEEK)",
    )
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=0,
        help="Maximum number of tasks to export (0 = no limit)",
    )
    parser.add_argument(
        "--priority",
        choices=["high", "medium", "low"],
        default="medium",
        help="Priority to assign to exported tasks (default: medium)",
    )

    args = parser.parse_args(argv)

    if not MASTER_TASK_LOG_PATH.exists():
        print(f"❌ MASTER_TASK_LOG not found at {MASTER_TASK_LOG_PATH}")
        return 1

    parsed_tasks = parse_master_task_log(MASTER_TASK_LOG_PATH)
    section_tasks = [t for t in parsed_tasks if t.section == args.section]

    if args.max_tasks and args.max_tasks > 0:
        section_tasks = section_tasks[: args.max_tasks]

    if not section_tasks:
        print(f"⚠️ No tasks found in section {args.section} of MASTER_TASK_LOG.md")
        return 0

    payload = build_cycle_planner_payload(agent_id=args.agent, tasks=section_tasks, priority=args.priority)
    out_path = write_cycle_planner_file(args.agent, payload)

    print("======================================================")
    print("MASTER TASK LOG → CYCLE PLANNER")
    print("======================================================")
    print(f"Agent: {args.agent}")
    print(f"Section: {args.section}")
    print(f"Tasks exported: {payload['total_tasks']}")
    print(f"Output file: {out_path.relative_to(PROJECT_ROOT)}")
    print("======================================================")
    print("Agents can now claim these tasks using:")
    print("  python -m src.services.messaging_cli --agent", args.agent, "--get-next-task")
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())





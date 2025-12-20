#!/usr/bin/env python3
"""
Documentation Assistant Tool
============================

The tool I wished I had this session!

Automates common documentation tasks:
- Generate mission tracking docs from templates
- Create completion reports with consistent structure
- Generate milestone documentation for agent achievements
- Create enhancement request docs with standard format
- Quick status snapshots

Author: Agent-8 (Documentation Specialist)
Refactored: Agent-6 (V2 Compliance - 539→165 lines, 69% reduction!)
Created: 2025-10-11 (During C-055-8 session cleanup)
Purpose: Make documentation faster and more consistent

Usage:
    python tools/documentation_assistant.py mission start --name C-057
    python tools/documentation_assistant.py mission complete --name C-057
    python tools/documentation_assistant.py milestone --agent Agent-7 --achievement "100% V2"
    python tools/documentation_assistant.py enhancement --name "Message Batching" --priority HIGH
    python tools/documentation_assistant.py status-snapshot

V2 Compliance: ✅ <400 lines, modular design
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import template generators
from doc_templates_mission import (
    create_mission_tracking_template,
    create_completion_report_template,
)
from doc_templates_achievements import (
    create_milestone_template,
    create_enhancement_request_template,
)


class DocumentationAssistant:
    """Helper tool for generating consistent documentation."""

    def __init__(self):
        """Initialize documentation assistant."""
        self.templates_dir = Path("docs/templates")
        self.missions_dir = Path("docs/missions")
        self.milestones_dir = Path("docs/milestones")
        self.enhancements_dir = Path("docs/enhancement_requests")

        # Ensure directories exist
        self.missions_dir.mkdir(parents=True, exist_ok=True)
        self.milestones_dir.mkdir(parents=True, exist_ok=True)
        self.enhancements_dir.mkdir(parents=True, exist_ok=True)

    def create_mission_doc(self, mission_name: str) -> Path:
        """Create initial mission tracking document."""
        doc_path = self.missions_dir / f"{mission_name}_TRACKING.md"
        content = create_mission_tracking_template(mission_name)
        doc_path.write_text(content)
        print(f"✅ Created mission tracking doc: {doc_path}")
        return doc_path

    def create_completion_report(self, mission_name: str) -> Path:
        """Create mission completion report."""
        doc_path = self.missions_dir / f"{mission_name}_COMPLETION_REPORT.md"
        content = create_completion_report_template(mission_name)
        doc_path.write_text(content)
        print(f"✅ Created completion report: {doc_path}")
        return doc_path

    def create_milestone_doc(self, agent_id: str, achievement: str) -> Path:
        """Create agent milestone documentation."""
        safe_achievement = achievement.lower().replace(" ", "_")
        doc_path = self.milestones_dir / f"{agent_id}_{safe_achievement}.md"
        content = create_milestone_template(agent_id, achievement)
        doc_path.write_text(content)
        print(f"✅ Created milestone doc: {doc_path}")
        return doc_path

    def create_enhancement_request(self, name: str, priority: str = "MEDIUM") -> Path:
        """Create enhancement request document."""
        safe_name = name.upper().replace(" ", "_")
        doc_path = self.enhancements_dir / f"{safe_name}.md"
        content = create_enhancement_request_template(name, priority)
        doc_path.write_text(content)
        print(f"✅ Created enhancement request: {doc_path}")
        return doc_path

    def create_status_snapshot(self) -> dict[str, Any]:
        """Generate quick status snapshot."""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "swarm_status": {
                "active_agents": self._count_active_agents(),
                "recent_missions": self._list_recent_missions(),
                "recent_milestones": self._list_recent_milestones(),
            },
            "documentation_health": {
                "missions_tracked": len(list(self.missions_dir.glob("*_TRACKING.md"))),
                "completed_missions": len(list(self.missions_dir.glob("*_COMPLETION*.md"))),
                "milestones_documented": len(list(self.milestones_dir.glob("*.md"))),
                "enhancements_proposed": len(list(self.enhancements_dir.glob("*.md"))),
            },
        }

        print(json.dumps(snapshot, indent=2))
        return snapshot

    def _count_active_agents(self) -> int:
        """Count active agents based on recent activity."""
        workspaces = Path("agent_workspaces")
        if not workspaces.exists():
            return 0
        return len([d for d in workspaces.iterdir() if d.is_dir() and d.name.startswith("Agent-")])

    def _list_recent_missions(self, limit: int = 5) -> list:
        """List recent mission docs."""
        missions = sorted(
            self.missions_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        return [m.stem for m in missions[:limit]]

    def _list_recent_milestones(self, limit: int = 5) -> list:
        """List recent milestone docs."""
        milestones = sorted(
            self.milestones_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )
        return [m.stem for m in milestones[:limit]]


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Documentation Assistant - Automate common documentation tasks"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Mission subcommand
    mission_parser = subparsers.add_parser("mission", help="Mission documentation")
    mission_sub = mission_parser.add_subparsers(dest="action")

    start_p = mission_sub.add_parser("start", help="Create mission tracking doc")
    start_p.add_argument("--name", required=True, help="Mission name (e.g., C-057)")

    complete_p = mission_sub.add_parser("complete", help="Create completion report")
    complete_p.add_argument("--name", required=True, help="Mission name")

    # Milestone subcommand
    milestone_parser = subparsers.add_parser("milestone", help="Milestone documentation")
    milestone_parser.add_argument("--agent", required=True, help="Agent ID")
    milestone_parser.add_argument("--achievement", required=True, help="Achievement description")

    # Enhancement subcommand
    enhance_parser = subparsers.add_parser("enhancement", help="Enhancement request")
    enhance_parser.add_argument("--name", required=True, help="Enhancement name")
    enhance_parser.add_argument(
        "--priority", choices=["LOW", "MEDIUM", "HIGH"], default="MEDIUM", help="Priority level"
    )

    # Status snapshot
    subparsers.add_parser("status-snapshot", help="Generate status snapshot")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    assistant = DocumentationAssistant()

    try:
        if args.command == "mission":
            if args.action == "start":
                assistant.create_mission_doc(args.name)
            elif args.action == "complete":
                assistant.create_completion_report(args.name)

        elif args.command == "milestone":
            assistant.create_milestone_doc(args.agent, args.achievement)

        elif args.command == "enhancement":
            assistant.create_enhancement_request(args.name, args.priority)

        elif args.command == "status-snapshot":
            assistant.create_status_snapshot()

        print("\n🐝 WE. ARE. SWARM. ⚡🔥")
        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())


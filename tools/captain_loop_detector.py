#!/usr/bin/env python3
"""
Captain Loop Detector - Automated Open Loop Detection

Scans all agent status.json files to identify incomplete tasks,
pending work, and open loops that need captain assignment.

Author: Agent-2 (Acting Captain)
Date: 2025-12-02
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CaptainLoopDetector:
    """Detect open loops and incomplete tasks across all agents."""

    def __init__(self, workspace_root: Path = Path("agent_workspaces")):
        """Initialize loop detector."""
        self.workspace_root = workspace_root
        self.agents = {}
        self.open_loops = []

    def scan_all_agents(self) -> Dict[str, dict]:
        """Scan all agent status files."""
        agents = {}
        for agent_dir in self.workspace_root.glob("Agent-*"):
            if not agent_dir.is_dir():
                continue

            agent_id = agent_dir.name
            status_file = agent_dir / "status.json"

            if not status_file.exists():
                logger.warning(f"⚠️ No status.json found for {agent_id}")
                continue

            try:
                with open(status_file, "r", encoding="utf-8") as f:
                    status = json.load(f)
                    agents[agent_id] = status
            except Exception as e:
                logger.error(f"❌ Error reading {status_file}: {e}")

        self.agents = agents
        return agents

    def detect_open_loops(self) -> List[dict]:
        """Detect open loops from agent status files."""
        open_loops = []

        for agent_id, status in self.agents.items():
            # Check current_tasks for incomplete items
            current_tasks = status.get("current_tasks", [])
            for task in current_tasks:
                if self._is_incomplete(task):
                    loop = self._extract_loop_info(agent_id, task, status)
                    if loop:
                        open_loops.append(loop)

            # Check next_actions for pending items
            next_actions = status.get("next_actions", [])
            for action in next_actions:
                if self._is_pending(action):
                    loop = self._extract_action_info(agent_id, action, status)
                    if loop:
                        open_loops.append(loop)

        self.open_loops = open_loops
        return open_loops

    def _is_incomplete(self, task: str) -> bool:
        """Check if task is incomplete."""
        incomplete_markers = ["⏳", "ACTIVE", "PENDING", "IN PROGRESS", "BLOCKED"]
        complete_markers = ["✅", "COMPLETE", "DONE", "FINISHED"]

        task_upper = task.upper()
        has_incomplete = any(marker in task_upper for marker in incomplete_markers)
        has_complete = any(marker in task_upper for marker in complete_markers)

        return has_incomplete and not has_complete

    def _is_pending(self, action: str) -> bool:
        """Check if action is pending."""
        pending_markers = ["⏳", "PENDING", "TODO", "NEXT"]
        complete_markers = ["✅", "COMPLETE", "DONE"]

        action_upper = action.upper()
        has_pending = any(marker in action_upper for marker in pending_markers)
        has_complete = any(marker in action_upper for marker in complete_markers)

        return has_pending and not has_complete

    def _extract_loop_info(self, agent_id: str, task: str, status: dict) -> dict:
        """Extract loop information from task."""
        # Determine priority
        priority = self._determine_priority(task, status)

        # Extract task details
        task_clean = task.replace("⏳", "").replace("ACTIVE:", "").strip()

        return {
            "agent_id": agent_id,
            "agent_name": status.get("agent_name", "Unknown"),
            "type": "task",
            "description": task_clean,
            "priority": priority,
            "status": status.get("status", "UNKNOWN"),
            "last_updated": status.get("last_updated", "Unknown"),
            "mission": status.get("current_mission", "No mission"),
        }

    def _extract_action_info(self, agent_id: str, action: str, status: dict) -> dict:
        """Extract loop information from action."""
        priority = self._determine_priority(action, status)

        action_clean = action.replace("⏳", "").replace("PENDING:", "").strip()

        return {
            "agent_id": agent_id,
            "agent_name": status.get("agent_name", "Unknown"),
            "type": "action",
            "description": action_clean,
            "priority": priority,
            "status": status.get("status", "UNKNOWN"),
            "last_updated": status.get("last_updated", "Unknown"),
            "mission": status.get("current_mission", "No mission"),
        }

    def _determine_priority(self, text: str, status: dict) -> str:
        """Determine priority from text and status."""
        text_upper = text.upper()

        # Critical markers
        if any(marker in text_upper for marker in ["🚨", "CRITICAL", "BLOCKER", "URGENT", "MUST FIX"]):
            return "CRITICAL"

        # High markers
        if any(marker in text_upper for marker in ["⚠️", "HIGH", "IMPORTANT", "USER-FACING"]):
            return "HIGH"

        # Medium markers
        if any(marker in text_upper for marker in ["⏳", "MEDIUM", "QUALITY", "MAINTENANCE"]):
            return "MEDIUM"

        # Check mission priority
        mission_priority = status.get("mission_priority", "").upper()
        if mission_priority == "CRITICAL":
            return "CRITICAL"
        elif mission_priority == "HIGH":
            return "HIGH"

        return "MEDIUM"

    def categorize_loops(self) -> Dict[str, List[dict]]:
        """Categorize loops by priority."""
        categorized = {
            "CRITICAL": [],
            "HIGH": [],
            "MEDIUM": [],
            "LOW": [],
        }

        for loop in self.open_loops:
            priority = loop.get("priority", "MEDIUM")
            categorized[priority].append(loop)

        return categorized

    def generate_report(self) -> str:
        """Generate loop detection report."""
        report_lines = [
            "# 🚨 Captain Loop Detection Report",
            "",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Agent**: Agent-2 (Acting Captain)",
            f"**Status**: ✅ **LOOP DETECTION COMPLETE**",
            "",
            "---",
            "",
            f"## 📊 **SUMMARY**",
            "",
            f"**Total Agents Scanned**: {len(self.agents)}",
            f"**Open Loops Detected**: {len(self.open_loops)}",
            "",
        ]

        categorized = self.categorize_loops()

        for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            loops = categorized[priority]
            if not loops:
                continue

            report_lines.extend([
                f"## {priority} Priority Loops ({len(loops)})",
                "",
            ])

            for i, loop in enumerate(loops, 1):
                report_lines.extend([
                    f"### {i}. {loop['agent_id']}: {loop['description'][:80]}",
                    "",
                    f"- **Agent**: {loop['agent_name']}",
                    f"- **Type**: {loop['type']}",
                    f"- **Status**: {loop['status']}",
                    f"- **Last Updated**: {loop['last_updated']}",
                    f"- **Mission**: {loop['mission'][:100]}",
                    "",
                ])

        report_lines.extend([
            "---",
            "",
            "**Generated By**: Captain Loop Detector",
            "**Next Action**: Review loops and assign tasks to agents",
            "",
            "🐝 **WE. ARE. SWARM. ⚡🔥**",
        ])

        return "\n".join(report_lines)

    def save_report(self, output_path: Path = Path("agent_workspaces/Agent-2/LOOP_DETECTION_REPORT.md")):
        """Save loop detection report."""
        report = self.generate_report()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        logger.info(f"✅ Report saved to {output_path}")


def main():
    """Main execution."""
    detector = CaptainLoopDetector()
    
    logger.info("🔍 Scanning all agents...")
    agents = detector.scan_all_agents()
    logger.info(f"✅ Scanned {len(agents)} agents")

    logger.info("🔍 Detecting open loops...")
    loops = detector.detect_open_loops()
    logger.info(f"✅ Detected {len(loops)} open loops")

    logger.info("📊 Categorizing loops...")
    categorized = detector.categorize_loops()
    for priority, loops_list in categorized.items():
        if loops_list:
            logger.info(f"   {priority}: {len(loops_list)} loops")

    logger.info("📝 Generating report...")
    detector.save_report()
    logger.info("✅ Report generated")

    # Print summary
    print("\n" + "=" * 60)
    print("🚨 LOOP DETECTION SUMMARY")
    print("=" * 60)
    print(f"Total Agents: {len(agents)}")
    print(f"Open Loops: {len(loops)}")
    print(f"  CRITICAL: {len(categorized['CRITICAL'])}")
    print(f"  HIGH: {len(categorized['HIGH'])}")
    print(f"  MEDIUM: {len(categorized['MEDIUM'])}")
    print(f"  LOW: {len(categorized['LOW'])}")
    print("=" * 60)


if __name__ == "__main__":
    main()


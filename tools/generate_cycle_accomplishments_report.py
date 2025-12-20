#!/usr/bin/env python3
"""
Cycle Accomplishments Report Generator
=======================================

Generates a comprehensive cycle report by reading all agents' status.json files
and compiling their accomplishments, completed tasks, and achievements.

Part of soft onboarding protocol - automatically generates report during onboarding.

Usage:
    python tools/generate_cycle_accomplishments_report.py
    python tools/generate_cycle_accomplishments_report.py --cycle C-XXX
    python tools/generate_cycle_accomplishments_report.py --output docs/archive/cycles/

Author: Agent-7 (Web Development Specialist)
Date: 2025-01-27
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_agent_status(agent_id: str) -> dict[str, Any] | None:
    """Load agent status.json file."""
    status_file = Path(f"agent_workspaces/{agent_id}/status.json")
    if not status_file.exists():
        logger.warning(f"⚠️  Status file not found for {agent_id}: {status_file}")
        return None
    
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to load status for {agent_id}: {e}")
        return None


def extract_accomplishments(status: dict[str, Any]) -> dict[str, Any]:
    """Extract accomplishments data from status.json."""
    return {
        "agent_id": status.get("agent_id", "Unknown"),
        "agent_name": status.get("agent_name", "Unknown"),
        "status": status.get("status", "Unknown"),
        "current_mission": status.get("current_mission", "No mission"),
        "mission_priority": status.get("mission_priority", "N/A"),
        "last_updated": status.get("last_updated", "Unknown"),
        "completed_tasks": status.get("completed_tasks", []),
        "achievements": status.get("achievements", []),
        "progress": status.get("progress", ""),
        "current_tasks": status.get("current_tasks", []),
        "next_actions": status.get("next_actions", []),
        "points_earned": status.get("points_earned", 0),
        "last_milestone": status.get("last_milestone", ""),
        "next_milestone": status.get("next_milestone", ""),
    }


def generate_cycle_report(
    cycle_id: str | None = None,
    output_dir: Path | None = None
) -> Path:
    """
    Generate comprehensive cycle accomplishments report.
    
    Args:
        cycle_id: Optional cycle identifier (e.g., "C-XXX")
        output_dir: Optional output directory (default: docs/archive/cycles/)
    
    Returns:
        Path to generated report file
    """
    # Determine output directory
    if output_dir is None:
        output_dir = Path("docs/archive/cycles")
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if cycle_id:
        filename = f"CYCLE_ACCOMPLISHMENTS_{cycle_id}_{timestamp}.md"
    else:
        filename = f"CYCLE_ACCOMPLISHMENTS_{timestamp}.md"
    
    report_path = output_dir / filename
    
    logger.info("📊 Generating cycle accomplishments report...")
    logger.info(f"   Output: {report_path}")
    
    # Load active agent statuses (mode-aware)
    try:
        from src.core.agent_mode_manager import get_active_agents
        agents = get_active_agents()
        logger.info(f"Mode-aware: Loading status for {len(agents)} active agents")
    except Exception as e:
        logger.warning(f"Failed to load mode-aware agents, using fallback: {e}")
        agents = [f"Agent-{i}" for i in range(1, 9)]
    
    agent_data = {}
    total_completed_tasks = 0
    total_achievements = 0
    total_points = 0
    
    for agent_id in agents:
        status = load_agent_status(agent_id)
        if status:
            agent_data[agent_id] = extract_accomplishments(status)
            total_completed_tasks += len(agent_data[agent_id]["completed_tasks"])
            total_achievements += len(agent_data[agent_id]["achievements"])
            total_points += agent_data[agent_id].get("points_earned", 0)
        else:
            logger.warning(f"⚠️  Skipping {agent_id} - no status file")
    
    # Generate report content
    report_lines = []
    report_lines.append("# 🎉 CYCLE ACCOMPLISHMENTS REPORT")
    report_lines.append("")
    report_lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if cycle_id:
        report_lines.append(f"**Cycle**: {cycle_id}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Summary statistics
    report_lines.append("## 📊 SWARM SUMMARY")
    report_lines.append("")
    report_lines.append(f"- **Agents Active**: {len(agent_data)}/{len(agents)}")
    report_lines.append(f"- **Total Completed Tasks**: {total_completed_tasks}")
    report_lines.append(f"- **Total Achievements**: {total_achievements}")
    report_lines.append(f"- **Total Points Earned**: {total_points:,}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    
    # Per-agent accomplishments
    report_lines.append("## 🤖 AGENT ACCOMPLISHMENTS")
    report_lines.append("")
    
    for agent_id in sorted(agent_data.keys()):
        data = agent_data[agent_id]
        report_lines.append(f"### {agent_id} - {data['agent_name']}")
        report_lines.append("")
        report_lines.append(f"**Status**: {data['status']}")
        report_lines.append(f"**Mission**: {data['current_mission']}")
        report_lines.append(f"**Priority**: {data['mission_priority']}")
        report_lines.append(f"**Last Updated**: {data['last_updated']}")
        if data.get('points_earned', 0) > 0:
            report_lines.append(f"**Points Earned**: {data['points_earned']:,}")
        report_lines.append("")
        
        # Completed Tasks
        if data['completed_tasks']:
            report_lines.append("#### ✅ Completed Tasks")
            report_lines.append("")
            for task in data['completed_tasks']:
                report_lines.append(f"- {task}")
            report_lines.append("")
        
        # Achievements
        if data['achievements']:
            report_lines.append("#### 🏆 Achievements")
            report_lines.append("")
            for achievement in data['achievements']:
                report_lines.append(f"- {achievement}")
            report_lines.append("")
        
        # Progress Summary
        if data['progress']:
            report_lines.append("#### 📈 Progress Summary")
            report_lines.append("")
            report_lines.append(data['progress'])
            report_lines.append("")
        
        # Current Tasks (if any)
        if data['current_tasks']:
            report_lines.append("#### 🔄 Current Tasks")
            report_lines.append("")
            for task in data['current_tasks'][:5]:  # Limit to 5 most recent
                report_lines.append(f"- {task}")
            if len(data['current_tasks']) > 5:
                report_lines.append(f"- *... and {len(data['current_tasks']) - 5} more*")
            report_lines.append("")
        
        # Milestones
        if data.get('last_milestone'):
            report_lines.append(f"**Last Milestone**: {data['last_milestone']}")
        if data.get('next_milestone'):
            report_lines.append(f"**Next Milestone**: {data['next_milestone']}")
        
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")
    
    # Footer
    report_lines.append("## 📝 NOTES")
    report_lines.append("")
    report_lines.append("This report was automatically generated from agent status.json files.")
    report_lines.append("All accomplishments, tasks, and achievements are extracted from")
    report_lines.append("each agent's status tracking.")
    report_lines.append("")
    report_lines.append("**🐝 WE. ARE. SWARM. ⚡🔥**")
    
    # Write report
    report_content = "\n".join(report_lines)
    report_path.write_text(report_content, encoding="utf-8")
    
    logger.info(f"✅ Cycle report generated: {report_path}")
    logger.info(f"   Agents: {len(agent_data)}")
    logger.info(f"   Tasks: {total_completed_tasks}")
    logger.info(f"   Achievements: {total_achievements}")
    logger.info(f"   Points: {total_points:,}")
    
    return report_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate cycle accomplishments report from agent status.json files",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--cycle",
        type=str,
        help="Cycle identifier (e.g., C-XXX)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output directory (default: docs/archive/cycles/)"
    )
    
    args = parser.parse_args()
    
    try:
        output_dir = Path(args.output) if args.output else None
        report_path = generate_cycle_report(
            cycle_id=args.cycle,
            output_dir=output_dir
        )
        
        print(f"\n✅ Report generated: {report_path}")
        print(f"   Location: {report_path.absolute()}")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Failed to generate report: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())


#!/usr/bin/env python3
"""
Captain Progress Dashboard - Real-time Progress Monitoring

Tracks agent progress, identifies blockers, and provides visual
progress indicators for captain coordination.

Author: Agent-2 (Acting Captain)
Date: 2025-12-02
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CaptainProgressDashboard:
    """Real-time progress monitoring dashboard for captain coordination."""

    def __init__(self, workspace_root: Path = Path("agent_workspaces")):
        """Initialize progress dashboard."""
        self.workspace_root = workspace_root
        self.agents = {}
        self.progress_data = {}

    def scan_agent_progress(self) -> Dict[str, dict]:
        """Scan all agent status files for progress."""
        agents = {}
        for agent_dir in self.workspace_root.glob("Agent-*"):
            if not agent_dir.is_dir():
                continue

            agent_id = agent_dir.name
            status_file = agent_dir / "status.json"

            if not status_file.exists():
                continue

            try:
                with open(status_file, "r", encoding="utf-8") as f:
                    status = json.load(f)
                    
                    # Calculate progress metrics
                    progress = self._calculate_progress(status)
                    agents[agent_id] = {
                        "status": status,
                        "progress": progress,
                    }
            except Exception as e:
                logger.error(f"❌ Error reading {status_file}: {e}")

        self.agents = agents
        return agents

    def _calculate_progress(self, status: dict) -> dict:
        """Calculate progress metrics for agent."""
        current_tasks = status.get("current_tasks", [])
        completed_tasks = status.get("completed_tasks", [])
        
        # Count tasks by status
        total_tasks = len(current_tasks) + len(completed_tasks)
        completed_count = len([t for t in current_tasks if "✅" in t or "COMPLETE" in t.upper()])
        active_count = len([t for t in current_tasks if "⏳" in t or "ACTIVE" in t.upper()])
        blocked_count = len([t for t in current_tasks if "🚨" in t or "BLOCKER" in t.upper() or "BLOCKED" in t.upper()])
        
        # Calculate completion percentage
        if total_tasks > 0:
            completion_pct = (completed_count + len(completed_tasks)) / total_tasks * 100
        else:
            completion_pct = 100.0
        
        # Determine status
        if blocked_count > 0:
            status_indicator = "🔴 BLOCKED"
        elif active_count > 0:
            status_indicator = "🟡 ACTIVE"
        elif completion_pct == 100:
            status_indicator = "🟢 COMPLETE"
        else:
            status_indicator = "⚪ IDLE"
        
        # Last update age
        last_updated_str = status.get("last_updated", "")
        age_hours = self._calculate_age_hours(last_updated_str)
        
        return {
            "total_tasks": total_tasks,
            "completed": completed_count + len(completed_tasks),
            "active": active_count,
            "blocked": blocked_count,
            "completion_pct": round(completion_pct, 1),
            "status_indicator": status_indicator,
            "last_updated": last_updated_str,
            "age_hours": age_hours,
        }

    def _calculate_age_hours(self, timestamp_str: str) -> float:
        """Calculate age of timestamp in hours."""
        if not timestamp_str:
            return 999.0
        
        try:
            # Parse timestamp (format: "2025-12-02 08:00:00")
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            age = datetime.now() - dt
            return age.total_seconds() / 3600
        except Exception:
            return 999.0

    def identify_blockers(self) -> List[dict]:
        """Identify blockers across all agents."""
        blockers = []
        
        for agent_id, data in self.agents.items():
            status = data["status"]
            current_tasks = status.get("current_tasks", [])
            
            for task in current_tasks:
                if "🚨" in task or "BLOCKER" in task.upper() or "BLOCKED" in task.upper():
                    blockers.append({
                        "agent_id": agent_id,
                        "agent_name": status.get("agent_name", "Unknown"),
                        "blocker": task,
                        "priority": self._determine_priority(task),
                        "last_updated": status.get("last_updated", "Unknown"),
                    })
        
        return sorted(blockers, key=lambda x: x["priority"] == "CRITICAL", reverse=True)

    def _determine_priority(self, text: str) -> str:
        """Determine priority from text."""
        text_upper = text.upper()
        
        if "🚨" in text or "CRITICAL" in text_upper:
            return "CRITICAL"
        elif "⚠️" in text or "HIGH" in text_upper:
            return "HIGH"
        else:
            return "MEDIUM"

    def generate_dashboard(self) -> str:
        """Generate progress dashboard report."""
        lines = [
            "# 📊 Captain Progress Dashboard",
            "",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Agent**: Agent-2 (Acting Captain)",
            "",
            "---",
            "",
            "## 📈 **AGENT PROGRESS SUMMARY**",
            "",
            "| Agent | Status | Completion | Active | Blocked | Last Updated |",
            "|-------|--------|------------|--------|---------|--------------|",
        ]
        
        # Sort agents by completion percentage
        sorted_agents = sorted(
            self.agents.items(),
            key=lambda x: x[1]["progress"]["completion_pct"],
            reverse=True
        )
        
        for agent_id, data in sorted_agents:
            progress = data["progress"]
            lines.append(
                f"| {agent_id} | {progress['status_indicator']} | "
                f"{progress['completion_pct']}% | {progress['active']} | "
                f"{progress['blocked']} | {progress['last_updated']} |"
            )
        
        # Blockers section
        blockers = self.identify_blockers()
        if blockers:
            lines.extend([
                "",
                "## 🚨 **BLOCKERS**",
                "",
            ])
            
            for blocker in blockers:
                lines.extend([
                    f"### {blocker['agent_id']}: {blocker['blocker'][:80]}",
                    f"- **Priority**: {blocker['priority']}",
                    f"- **Last Updated**: {blocker['last_updated']}",
                    "",
                ])
        
        lines.extend([
            "---",
            "",
            "**Generated By**: Captain Progress Dashboard",
            "**Next Action**: Review blockers and assign tasks",
            "",
            "🐝 **WE. ARE. SWARM. ⚡🔥**",
        ])
        
        return "\n".join(lines)

    def save_dashboard(self, output_path: Path = Path("agent_workspaces/Agent-2/PROGRESS_DASHBOARD.md")):
        """Save progress dashboard."""
        dashboard = self.generate_dashboard()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(dashboard, encoding="utf-8")
        logger.info(f"✅ Dashboard saved to {output_path}")


def main():
    """Main execution."""
    dashboard = CaptainProgressDashboard()
    
    logger.info("📊 Scanning agent progress...")
    agents = dashboard.scan_agent_progress()
    logger.info(f"✅ Scanned {len(agents)} agents")
    
    logger.info("🚨 Identifying blockers...")
    blockers = dashboard.identify_blockers()
    logger.info(f"✅ Found {len(blockers)} blockers")
    
    logger.info("📝 Generating dashboard...")
    dashboard.save_dashboard()
    logger.info("✅ Dashboard generated")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 PROGRESS DASHBOARD SUMMARY")
    print("=" * 60)
    for agent_id, data in sorted(agents.items()):
        progress = data["progress"]
        print(f"{agent_id}: {progress['status_indicator']} - {progress['completion_pct']}% complete")
    print("=" * 60)
    if blockers:
        print(f"\n🚨 BLOCKERS: {len(blockers)}")
        for blocker in blockers[:5]:  # Show top 5
            print(f"  - {blocker['agent_id']}: {blocker['blocker'][:60]}")


if __name__ == "__main__":
    main()


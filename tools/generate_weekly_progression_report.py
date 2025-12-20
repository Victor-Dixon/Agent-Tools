#!/usr/bin/env python3
"""
Weekly State of Progression Report Generator
============================================

Generates comprehensive weekly report based on:
- Daily state of project reports from all agents
- Agent status.json files
- Agent Discord updates
- Swarm Organizer data
- Metrics tracking

Author: Agent-4 (Captain)
Date: 2025-12-05
"""

import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


class WeeklyProgressionReportGenerator:
    """Generate weekly state of progression report from multiple sources."""

    def __init__(self):
        self.workspace_path = Path("agent_workspaces")
        self.reports_dir = self.workspace_path / "Agent-4" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.swarm_organizer_dir = self.workspace_path / "swarm_cycle_planner"
        self.devlogs_dir = Path("devlogs")
        self.swarm_brain_dir = Path("swarm_brain/devlogs")

    def generate_report(self, week_start_date: Optional[str] = None) -> Path:
        """
        Generate weekly progression report.

        Args:
            week_start_date: Week start date (YYYY-MM-DD). Defaults to Monday of current week.

        Returns:
            Path to generated report file
        """
        # Determine week dates
        if week_start_date:
            week_start = datetime.strptime(week_start_date, "%Y-%m-%d")
        else:
            # Find most recent Monday
            today = datetime.now()
            days_since_monday = today.weekday()
            week_start = today - timedelta(days=days_since_monday)
            week_start = week_start.replace(
                hour=0, minute=0, second=0, microsecond=0)

        week_end = week_start + timedelta(days=6)

        # Collect data from all sources
        agent_statuses = self._collect_agent_statuses()
        swarm_organizer = self._collect_swarm_organizer()
        daily_reports = self._collect_daily_reports(week_start, week_end)
        discord_updates = self._collect_discord_updates(week_start, week_end)
        metrics = self._collect_metrics()
        project_scanner_outputs = self._collect_project_scanner_outputs(
            week_start, week_end)

        # Generate report
        report_content = self._generate_report_content(
            week_start, week_end, agent_statuses, swarm_organizer,
            daily_reports, discord_updates, metrics, project_scanner_outputs
        )

        # Save report
        report_filename = f"WEEKLY_STATE_OF_PROGRESSION_{week_start.strftime('%Y-%m-%d')}.md"
        report_path = self.reports_dir / report_filename
        report_path.write_text(report_content, encoding='utf-8')

        logger.info(f"✅ Weekly progression report generated: {report_path}")
        return report_path

    def _collect_agent_statuses(self) -> Dict[str, Dict]:
        """Collect status.json from all agents."""
        statuses = {}
        for agent_id in [f"Agent-{i}" for i in [1, 2, 3, 5, 6, 7, 8, 4]]:
            status_file = self.workspace_path / agent_id / "status.json"
            if status_file.exists():
                try:
                    with open(status_file, 'r', encoding='utf-8') as f:
                        statuses[agent_id] = json.load(f)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to read {agent_id} status: {e}")
        return statuses

    def _collect_swarm_organizer(self) -> Optional[Dict]:
        """Collect latest Swarm Organizer data."""
        # Find latest organizer file
        organizer_files = list(
            self.swarm_organizer_dir.glob("SWARM_ORGANIZER_*.json"))
        if not organizer_files:
            return None

        latest = max(organizer_files, key=lambda p: p.stat().st_mtime)
        try:
            with open(latest, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️ Failed to read swarm organizer: {e}")
            return None

    def _collect_daily_reports(self, week_start: datetime, week_end: datetime) -> List[Dict]:
        """Collect daily state of project reports from agents."""
        reports = []

        # Search in agent workspaces and swarm_brain
        for search_dir in [self.workspace_path, self.swarm_brain_dir]:
            if not search_dir.exists():
                continue

            for agent_dir in search_dir.iterdir():
                if not agent_dir.is_dir():
                    continue

                # Look for daily report files
                report_files = list(agent_dir.rglob(
                    "*daily*state*project*.md"))
                report_files.extend(agent_dir.rglob(
                    "*DAILY*STATE*PROJECT*.md"))

                for report_file in report_files:
                    try:
                        # Check if file is within week
                        file_time = datetime.fromtimestamp(
                            report_file.stat().st_mtime)
                        if week_start <= file_time <= week_end:
                            reports.append({
                                "agent": agent_dir.name,
                                "file": report_file,
                                "date": file_time,
                                # Preview
                                "content": report_file.read_text(encoding='utf-8')[:500]
                            })
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to read {report_file}: {e}")

        return reports

    def _collect_discord_updates(self, week_start: datetime, week_end: datetime) -> List[Dict]:
        """Collect Discord updates from logs."""
        updates = []

        # Check devlog posts log
        devlog_posts_file = Path("logs/devlog_posts.json")
        if devlog_posts_file.exists():
            try:
                with open(devlog_posts_file, 'r', encoding='utf-8') as f:
                    posts = json.load(f)

                for post in posts:
                    try:
                        post_time = datetime.fromisoformat(
                            post.get('timestamp', '').replace('Z', '+00:00'))
                        if week_start <= post_time.replace(tzinfo=None) <= week_end:
                            updates.append({
                                "agent": post.get('agent', 'Unknown'),
                                "channel": post.get('channel', 'Unknown'),
                                "timestamp": post_time,
                                "filename": post.get('filename', '')
                            })
                    except Exception:
                        pass
            except Exception as e:
                logger.warning(f"⚠️ Failed to read Discord updates log: {e}")

        return updates

    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect metrics from tracking files."""
        metrics = {}

        # Check for metrics file
        metrics_file = self.workspace_path / "Agent-4" / "metrics" / "cycle_metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    metrics = json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Failed to read metrics: {e}")

        return metrics

    def _collect_project_scanner_outputs(self, week_start: datetime, week_end: datetime) -> List[Dict]:
        """Collect project scanner outputs as proof of work."""
        outputs = []
        project_root = Path(".")

        # Scanner output files to check
        scanner_files = [
            "project_analysis.json",
            "test_analysis.json",
            "chatgpt_project_context.json"
        ]

        # Analysis directory files
        analysis_dir = project_root / "analysis"
        if analysis_dir.exists():
            scanner_files.extend([
                "analysis/agent_analysis.json",
                "analysis/module_analysis.json",
                "analysis/file_type_analysis.json",
                "analysis/complexity_analysis.json",
                "analysis/dependency_analysis.json",
                "analysis/architecture_overview.json"
            ])

        for file_path_str in scanner_files:
            file_path = project_root / file_path_str
            if file_path.exists():
                try:
                    file_time = datetime.fromtimestamp(
                        file_path.stat().st_mtime)
                    file_size = file_path.stat().st_size

                    # Always include project_analysis.json as proof of work, others if within week
                    if file_path_str == "project_analysis.json" or (week_start <= file_time <= week_end):
                        # Try to get file count or summary from JSON
                        file_count = "N/A"
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                                if isinstance(data, dict):
                                    file_count = len(data)
                                elif isinstance(data, list):
                                    file_count = len(data)
                        except Exception:
                            pass

                        outputs.append({
                            "file": file_path,
                            "date": file_time,
                            "size": file_size,
                            "file_count": file_count,
                            "name": file_path.name
                        })
                except Exception as e:
                    logger.warning(
                        f"⚠️ Failed to read scanner output {file_path}: {e}")

        return outputs

    def _generate_report_content(
        self,
        week_start: datetime,
        week_end: datetime,
        agent_statuses: Dict[str, Dict],
        swarm_organizer: Optional[Dict],
        daily_reports: List[Dict],
        discord_updates: List[Dict],
        metrics: Dict[str, Any],
        project_scanner_outputs: List[Dict]
    ) -> str:
        """Generate report markdown content."""

        week_str = f"{week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}"

        report = f"""# Weekly State of Progression Report
**Week**: {week_str}  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Report Period**: {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}

---

## 📊 **EXECUTIVE SUMMARY**

### **Swarm Status Overview**
- **Total Agents**: 8
- **Active Agents**: {sum(1 for s in agent_statuses.values() if s.get('status', '').upper() in ['ACTIVE', 'ACTIVE_AGENT_MODE'])}
- **Stale Agents**: {sum(1 for s in agent_statuses.values() if self._is_stale(s))}
- **Tasks Completed**: {self._count_completed_tasks(agent_statuses)}
- **Discord Updates Posted**: {len(discord_updates)}

---

## 🤖 **AGENT STATUS BREAKDOWN**

"""

        # Add agent-by-agent breakdown
        for agent_id in [f"Agent-{i}" for i in [1, 2, 3, 5, 6, 7, 8, 4]]:
            if agent_id not in agent_statuses:
                continue

            status = agent_statuses[agent_id]
            is_stale = self._is_stale(status)
            stale_marker = " ⚠️ STALE" if is_stale else ""

            report += f"""### **{agent_id}**{stale_marker}
- **Status**: {status.get('status', 'UNKNOWN')}
- **Mission**: {status.get('current_mission', 'N/A')[:80]}
- **Priority**: {status.get('mission_priority', 'N/A')}
- **Last Updated**: {status.get('last_updated', 'N/A')}
- **Active Tasks**: {len(status.get('current_tasks', []))}
- **Completed Tasks**: {len(status.get('completed_tasks', []))}
- **Achievements**: {len(status.get('achievements', []))}

"""

        # Add task completions
        report += """## ✅ **TASK COMPLETIONS BY AGENT**

"""
        for agent_id in [f"Agent-{i}" for i in [1, 2, 3, 5, 6, 7, 8, 4]]:
            if agent_id not in agent_statuses:
                continue

            status = agent_statuses[agent_id]
            completed = status.get('completed_tasks', [])

            if completed:
                report += f"""### **{agent_id}**
"""
                for task in completed[-10:]:  # Last 10 tasks
                    report += f"- ✅ {task[:100]}\n"
                if len(completed) > 10:
                    report += f"- ... and {len(completed) - 10} more\n"
                report += "\n"

        # Add Discord updates summary
        if discord_updates:
            report += """## 📢 **DISCORD UPDATES SUMMARY**

"""
            updates_by_agent = {}
            for update in discord_updates:
                agent = update.get('agent', 'Unknown')
                if agent not in updates_by_agent:
                    updates_by_agent[agent] = []
                updates_by_agent[agent].append(update)

            for agent, agent_updates in sorted(updates_by_agent.items()):
                report += f"""### **{agent}**
- **Updates Posted**: {len(agent_updates)}
- **Last Update**: {max(u['timestamp'] for u in agent_updates).strftime('%Y-%m-%d %H:%M:%S')}

"""

        # Add project scanner outputs section
        if project_scanner_outputs:
            report += """## 🔍 **PROJECT SCANNER OUTPUTS (PROOF OF WORK)**

"""
            for output in sorted(project_scanner_outputs, key=lambda x: x['date'], reverse=True):
                file_path = output['file']
                file_date = output['date']
                file_size = output['size']
                file_count = output['file_count']
                file_name = output['name']

                # Format size
                if file_size > 1024 * 1024:
                    size_str = f"{file_size / (1024 * 1024):.2f} MB"
                elif file_size > 1024:
                    size_str = f"{file_size / 1024:.2f} KB"
                else:
                    size_str = f"{file_size} bytes"

                report += f"""### **{file_name}**
- **Date**: {file_date.strftime('%Y-%m-%d %H:%M:%S')}
- **Size**: {size_str}
- **Files Analyzed**: {file_count if file_count != 'N/A' else 'N/A'}
- **Path**: `{file_path}`

"""
        else:
            report += """## 🔍 **PROJECT SCANNER OUTPUTS (PROOF OF WORK)**

*No project scanner outputs found for this week period.*

"""

        # Add daily reports section
        if daily_reports:
            report += """## 📅 **DAILY STATE OF PROJECT REPORTS**

"""
            # Group by agent
            reports_by_agent = {}
            for report_data in daily_reports:
                agent = report_data.get('agent', 'Unknown')
                if agent not in reports_by_agent:
                    reports_by_agent[agent] = []
                reports_by_agent[agent].append(report_data)

            for agent, agent_reports in sorted(reports_by_agent.items()):
                report += f"""### **{agent}**
- **Reports Found**: {len(agent_reports)}

"""
                for report_data in agent_reports:
                    report_date = report_data.get('date', datetime.now())
                    report_file = report_data.get('file', Path())
                    report += f"""- **{report_date.strftime('%Y-%m-%d')}**: [{report_file.name}]({report_file})
"""
                report += "\n"
        else:
            report += """## 📅 **DAILY STATE OF PROJECT REPORTS**

*No daily state of project reports found for this week period.*

"""

        # Add swarm organizer data
        if swarm_organizer:
            report += """## 📋 **SWARM ORGANIZER SUMMARY**

"""
            overview = swarm_organizer.get('swarm_overview', {})
            report += f"""- **Total Agents**: {overview.get('total_agents', 8)}
- **Active Agents**: {overview.get('active_agents', 0)}
- **Blocked Agents**: {overview.get('blocked_agents', 0)}
- **Total Points Assigned**: {overview.get('total_points_assigned', 0)}
- **Cycle Focus**: {overview.get('cycle_focus', 'N/A')}

"""

        # Add metrics
        if metrics:
            report += """## 📈 **METRICS SUMMARY**

"""
            report += f"""- **Agent Utilization**: {metrics.get('agent_utilization', 'N/A')}
- **Staleness Incidents**: {metrics.get('staleness_incidents', 0)}
- **Resume Prompts Sent**: {metrics.get('resume_prompts_sent', 0)}
- **Tasks Completed**: {metrics.get('tasks_completed', 0)}

"""

        # Add blockers
        blockers = self._collect_blockers(agent_statuses)
        if blockers:
            report += """## 🚨 **BLOCKERS & RESOLUTIONS**

"""
            for blocker in blockers:
                report += f"""### **{blocker['agent']}**
- **Blocker**: {blocker['description']}
- **Status**: {blocker['status']}

"""

        # Add achievements
        achievements = self._collect_achievements(agent_statuses)
        if achievements:
            report += """## 🎯 **KEY ACHIEVEMENTS & MILESTONES**

"""
            for achievement in achievements[:20]:  # Top 20
                report += f"""- ✅ **{achievement['agent']}**: {achievement['achievement']}

"""

        # Add next week priorities
        report += """## 🔮 **NEXT WEEK PRIORITIES**

"""
        priorities = self._extract_next_priorities(
            agent_statuses, swarm_organizer)
        for priority in priorities:
            report += f"""- **{priority['agent']}**: {priority['priority']}

"""

        report += f"""
---

**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Generated By**: Agent-4 (Captain)  
**Pattern**: Captain Restart Pattern V2.0

🐝 **WE. ARE. SWARM. ⚡🔥**
"""

        return report

    def _is_stale(self, status: Dict) -> bool:
        """Check if agent status is stale (>2 hours)."""
        last_updated_str = status.get('last_updated', '')
        if not last_updated_str:
            return True

        try:
            last_updated = datetime.strptime(
                last_updated_str, '%Y-%m-%d %H:%M:%S')
            hours_since_update = (
                datetime.now() - last_updated).total_seconds() / 3600
            return hours_since_update > 2
        except Exception:
            return True

    def _count_completed_tasks(self, agent_statuses: Dict[str, Dict]) -> int:
        """Count total completed tasks across all agents."""
        total = 0
        for status in agent_statuses.values():
            total += len(status.get('completed_tasks', []))
        return total

    def _collect_blockers(self, agent_statuses: Dict[str, Dict]) -> List[Dict]:
        """Collect blockers from agent statuses."""
        blockers = []
        for agent_id, status in agent_statuses.items():
            blocker_list = status.get('blockers', [])
            for blocker in blocker_list:
                blockers.append({
                    'agent': agent_id,
                    'description': blocker if isinstance(blocker, str) else blocker.get('description', str(blocker)),
                    'status': 'Active'
                })
        return blockers

    def _collect_achievements(self, agent_statuses: Dict[str, Dict]) -> List[Dict]:
        """Collect achievements from agent statuses."""
        achievements = []
        for agent_id, status in agent_statuses.items():
            achievement_list = status.get('achievements', [])
            for achievement in achievement_list:
                achievements.append({
                    'agent': agent_id,
                    'achievement': achievement if isinstance(achievement, str) else achievement.get('description', str(achievement))
                })
        return achievements

    def _extract_next_priorities(self, agent_statuses: Dict[str, Dict], swarm_organizer: Optional[Dict]) -> List[Dict]:
        """Extract next priorities from statuses and organizer."""
        priorities = []

        # From agent statuses
        for agent_id, status in agent_statuses.items():
            next_actions = status.get('next_actions', [])
            if next_actions:
                priorities.append({
                    'agent': agent_id,
                    'priority': next_actions[0][:100] if isinstance(next_actions[0], str) else str(next_actions[0])
                })

        # From swarm organizer
        if swarm_organizer:
            agents = swarm_organizer.get('agents', {})
            for agent_id, agent_data in agents.items():
                if agent_data.get('next_actions'):
                    priorities.append({
                        'agent': agent_id,
                        'priority': agent_data['next_actions'][0][:100] if isinstance(agent_data['next_actions'][0], str) else str(agent_data['next_actions'][0])
                    })

        return priorities


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate weekly state of progression report')
    parser.add_argument(
        '--week-start', help='Week start date (YYYY-MM-DD). Defaults to Monday of current week.')
    parser.add_argument(
        '--output', help='Output file path. Defaults to Agent-4/reports/WEEKLY_STATE_OF_PROGRESSION_YYYY-MM-DD.md')

    args = parser.parse_args()

    generator = WeeklyProgressionReportGenerator()
    report_path = generator.generate_report(args.week_start)

    print(f"✅ Weekly progression report generated: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

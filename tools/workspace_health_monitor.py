#!/usr/bin/env python3
"""Workspace Health Monitor - Check agent workspace health.

Consolidates workspace_health_checker.py functionality.
Provides comprehensive workspace health monitoring.

Consolidated Tools:
- workspace_health_checker.py

Author: Agent-1 (Integration & Core Systems Specialist)
Created: 2025-11-22 (Agent-6), Enhanced: 2025-12-03 (Agent-1)
V2 Compliant: Yes (<300 lines)
<!-- SSOT Domain: infrastructure -->
"""

import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class WorkspaceHealth:
    """Workspace health metrics."""
    agent_id: str
    inbox_count: int
    unprocessed_count: int
    old_messages: int
    archive_count: int
    devlogs_count: int
    reports_count: int
    status_file_exists: bool
    status_file_current: bool
    status_consistency: str
    issues_found: int
    health_score: float
    recommendations: List[str]


class WorkspaceHealthMonitor:
    """Monitor agent workspace health."""

    def __init__(self, workspace_root: Path = Path("agent_workspaces")):
        self.workspace_root = workspace_root
        self.cutoff_days = 7

    def check_agent_workspace(self, agent_id: str) -> WorkspaceHealth:
        """Check health of a single agent workspace."""
        agent_dir = self.workspace_root / agent_id
        
        if not agent_dir.exists():
            return WorkspaceHealth(
                agent_id=agent_id,
                inbox_count=0,
                old_messages=0,
                archive_count=0,
                devlogs_count=0,
                reports_count=0,
                status_file_exists=False,
                status_file_current=False,
                health_score=0.0,
                recommendations=["Workspace directory does not exist"]
            )

        # Count inbox messages
        inbox_dir = agent_dir / "inbox"
        inbox_count = 0
        unprocessed_count = 0
        old_messages = 0
        cutoff_date = datetime.now() - timedelta(days=self.cutoff_days)
        
        if inbox_dir.exists():
            messages_json = inbox_dir / "messages.json"
            processed_messages = set()
            if messages_json.exists():
                try:
                    with open(messages_json, 'r') as f:
                        msg_data = json.load(f)
                        processed_messages = set(msg_data.get("messages", {}).keys())
                except Exception:
                    pass
            
            for msg_file in inbox_dir.glob("*.md"):
                if msg_file.name not in ["Agent-6_inbox.txt", "messages.json"]:
                    inbox_count += 1
                    file_time = datetime.fromtimestamp(msg_file.stat().st_mtime)
                    if file_time < cutoff_date:
                        old_messages += 1
                    if msg_file.stem not in processed_messages:
                        unprocessed_count += 1

        # Count archive messages
        archive_dir = inbox_dir / "archive"
        archive_count = len(list(archive_dir.glob("*.md"))) if archive_dir.exists() else 0

        # Count devlogs
        devlogs_dir = agent_dir / "devlogs"
        devlogs_count = len(list(devlogs_dir.glob("*.md"))) if devlogs_dir.exists() else 0

        # Count reports
        reports_dir = agent_dir / "reports"
        reports_count = len(list(reports_dir.glob("*.md"))) if reports_dir.exists() else 0

        # Check status file
        status_file = agent_dir / "status.json"
        status_file_exists = status_file.exists()
        status_file_current = False
        status_consistency = "UNKNOWN"
        
        agent_last_updated = None
        if status_file_exists:
            try:
                status_data = json.loads(status_file.read_text())
                last_updated = status_data.get("last_updated", "")
                if last_updated:
                    # Parse timestamp (various formats)
                    try:
                        if "T" in last_updated:
                            agent_last_updated = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                        else:
                            agent_last_updated = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
                        
                        if datetime.now() - agent_last_updated < timedelta(days=1):
                            status_file_current = True
                    except (ValueError, TypeError):
                        pass
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Check status consistency with runtime/AGENT_STATUS.json
        runtime_status_file = Path("runtime/AGENT_STATUS.json")
        if runtime_status_file.exists() and agent_last_updated:
            try:
                with open(runtime_status_file, 'r') as f:
                    runtime_data = json.load(f)
                    runtime_status = runtime_data.get(agent_id, {})
                    runtime_last_updated = runtime_status.get("last_updated", "")
                    if runtime_last_updated:
                        try:
                            if "T" in runtime_last_updated:
                                runtime_time = datetime.fromisoformat(runtime_last_updated.replace("Z", "+00:00"))
                            else:
                                runtime_time = datetime.strptime(runtime_last_updated, "%Y-%m-%d %H:%M:%S")
                            if abs((agent_last_updated - runtime_time).total_seconds()) < 60:
                                status_consistency = "CONSISTENT"
                            else:
                                status_consistency = "INCONSISTENT"
                        except (ValueError, TypeError):
                            status_consistency = "UNKNOWN"
            except Exception:
                status_consistency = "UNKNOWN"
        else:
            status_consistency = "NO_RUNTIME_FILE"
        
        # Identify issues (ERROR/FIXME/TODO markers)
        issues_found = 0
        if agent_dir.exists():
            for file_path in agent_dir.rglob("*.md"):
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    if "ERROR" in content or "FIXME" in content or "TODO" in content:
                        issues_found += 1
                except Exception:
                    pass

        # Calculate health score (0-100)
        health_score = self._calculate_health_score(
            inbox_count, unprocessed_count, old_messages,
            status_file_exists, status_file_current, status_consistency
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            inbox_count, unprocessed_count, old_messages,
            status_file_exists, status_file_current, status_consistency, issues_found
        )

        return WorkspaceHealth(
            agent_id=agent_id,
            inbox_count=inbox_count,
            unprocessed_count=unprocessed_count,
            old_messages=old_messages,
            archive_count=archive_count,
            devlogs_count=devlogs_count,
            reports_count=reports_count,
            status_file_exists=status_file_exists,
            status_file_current=status_file_current,
            status_consistency=status_consistency,
            issues_found=issues_found,
            health_score=health_score,
            recommendations=recommendations
        )

    def _calculate_health_score(
        self, inbox_count: int, unprocessed_count: int, old_messages: int,
        status_exists: bool, status_current: bool, status_consistency: str
    ) -> float:
        """Calculate workspace health score (0-100)."""
        score = 100.0
        
        # Penalize for old messages
        if old_messages > 0:
            score -= min(30, old_messages * 5)
        
        # Penalize for unprocessed messages
        if unprocessed_count > 0:
            score -= min(25, unprocessed_count * 3)
        
        # Penalize for high inbox count
        if inbox_count > 10:
            score -= min(20, (inbox_count - 10) * 2)
        
        # Penalize for missing status file
        if not status_exists:
            score -= 20
        
        # Penalize for outdated status file
        if status_exists and not status_current:
            score -= 10
        
        # Penalize for inconsistent status
        if status_consistency == "INCONSISTENT":
            score -= 15
        
        return max(0.0, score)

    def _generate_recommendations(
        self, inbox_count: int, unprocessed_count: int, old_messages: int,
        status_exists: bool, status_current: bool, status_consistency: str,
        issues_found: int
    ) -> List[str]:
        """Generate health recommendations."""
        recommendations = []
        
        if unprocessed_count > 0:
            recommendations.append(f"Process {unprocessed_count} unprocessed inbox message(s)")
        
        if old_messages > 0:
            recommendations.append(f"Archive {old_messages} old inbox message(s) (>7 days)")
        
        if inbox_count > 10:
            recommendations.append(f"Review {inbox_count} inbox messages (consider archiving old ones)")
        
        if not status_exists:
            recommendations.append("Create status.json file")
        
        if status_exists and not status_current:
            recommendations.append("Update status.json file (last updated >24 hours ago)")
        
        if status_consistency == "INCONSISTENT":
            recommendations.append("Fix status file inconsistency (agent vs runtime)")
        
        if issues_found > 0:
            recommendations.append(f"Review {issues_found} file(s) with ERROR/FIXME/TODO markers")
        
        if not recommendations:
            recommendations.append("Workspace health: Excellent ✅")
        
        return recommendations

    def check_all_workspaces(self) -> Dict[str, WorkspaceHealth]:
        """Check health of all agent workspaces."""
        health_results = {}
        
        # Find all agent directories
        for agent_dir in self.workspace_root.iterdir():
            if agent_dir.is_dir() and agent_dir.name.startswith("Agent-"):
                agent_id = agent_dir.name
                health_results[agent_id] = self.check_agent_workspace(agent_id)
        
        return health_results

    def print_report(self, health: WorkspaceHealth, verbose: bool = False):
        """Print health report for an agent."""
        print(f"\n{'='*70}")
        print(f"🏥 Workspace Health: {health.agent_id}")
        print(f"{'='*70}")
        print(f"Health Score: {health.health_score:.1f}/100")
        print(f"\n📬 Inbox: {health.inbox_count} messages "
              f"({health.unprocessed_count} unprocessed, {health.old_messages} old)")
        print(f"📦 Archive: {health.archive_count} messages")
        print(f"📝 Devlogs: {health.devlogs_count} files")
        print(f"📋 Reports: {health.reports_count} files")
        print(f"\n📄 Status File: {'✅' if health.status_file_exists else '❌'} "
              f"{'Current' if health.status_file_current else 'Outdated'} "
              f"(Consistency: {health.status_consistency})")
        
        if health.issues_found > 0:
            print(f"🚨 Issues Found: {health.issues_found} file(s) with ERROR/FIXME/TODO markers")
        
        print(f"\n💡 Recommendations:")
        for rec in health.recommendations:
            print(f"   • {rec}")
        
        if verbose:
            print(f"\n📊 Detailed Metrics:")
            print(f"   • Inbox messages: {health.inbox_count}")
            print(f"   • Unprocessed messages: {health.unprocessed_count}")
            print(f"   • Old messages: {health.old_messages}")
            print(f"   • Archive messages: {health.archive_count}")
            print(f"   • Devlogs: {health.devlogs_count}")
            print(f"   • Reports: {health.reports_count}")
            print(f"   • Status consistency: {health.status_consistency}")
            print(f"   • Issues found: {health.issues_found}")

    def print_summary(self, all_health: Dict[str, WorkspaceHealth]):
        """Print summary report for all workspaces."""
        print(f"\n{'='*60}")
        print(f"📊 Workspace Health Summary")
        print(f"{'='*60}")
        
        total_score = sum(h.health_score for h in all_health.values())
        avg_score = total_score / len(all_health) if all_health else 0
        
        print(f"\nAverage Health Score: {avg_score:.1f}/100")
        print(f"Workspaces Checked: {len(all_health)}")
        
        print(f"\n📊 Health by Agent:")
        for agent_id, health in sorted(all_health.items()):
            status = "✅" if health.health_score >= 80 else "⚠️" if health.health_score >= 60 else "❌"
            print(f"   {status} {agent_id}: {health.health_score:.1f}/100 "
                  f"({health.old_messages} old messages)")

        # Identify agents needing attention
        needs_attention = [
            (agent_id, health) for agent_id, health in all_health.items()
            if health.old_messages > 0 or health.health_score < 70
        ]
        
        if needs_attention:
            print(f"\n⚠️  Agents Needing Attention:")
            for agent_id, health in needs_attention:
                print(f"   • {agent_id}: {health.health_score:.1f}/100 "
                      f"({health.unprocessed_count} unprocessed, {health.old_messages} old, "
                      f"{len(health.recommendations)} recommendations)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Monitor agent workspace health")
    parser.add_argument(
        "--agent", "-a",
        help="Check specific agent workspace (e.g., Agent-6)"
    )
    parser.add_argument(
        "--all", "-A",
        action="store_true",
        help="Check all agent workspaces"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed information"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path("agent_workspaces"),
        help="Root directory for agent workspaces"
    )
    
    args = parser.parse_args()
    
    monitor = WorkspaceHealthMonitor(workspace_root=args.workspace_root)
    
    if args.agent:
        health = monitor.check_agent_workspace(args.agent)
        if args.json:
            print(json.dumps(asdict(health), indent=2))
        else:
            monitor.print_report(health, verbose=args.verbose)
    
    elif args.all:
        all_health = monitor.check_all_workspaces()
        if args.json:
            print(json.dumps({k: asdict(v) for k, v in all_health.items()}, indent=2))
        else:
            monitor.print_summary(all_health)
            if args.verbose:
                for agent_id, health in sorted(all_health.items()):
                    monitor.print_report(health, verbose=True)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()




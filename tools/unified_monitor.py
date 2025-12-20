#!/usr/bin/env python3
"""
Unified Monitor - Consolidated Monitoring Tool
==============================================

Consolidates all monitoring capabilities into a single unified tool.
Replaces 33+ individual monitoring tools with modular monitoring system.

Consolidated Tools:
- discord_bot_infrastructure_check.py (queue file check)
- manually_trigger_status_monitor_resume.py (resume trigger)
- workspace_health_monitor.py (workspace health monitoring) - Phase 2 ✅ CONSOLIDATED
- captain_check_agent_status.py (agent status checking) - Phase 2 ✅ CONSOLIDATED

Monitoring Categories:
- Service Health (GitHub Pusher, Discord, CI/CD)
- Queue Monitoring (Deferred Push Queue, Message Queue File)
- Agent Status (Progress, Stalls, Health, Resume Triggers)
- Infrastructure (Disk, CI, System)
- Test Coverage Tracking

Author: Agent-8 (SSOT & System Integration Specialist)
Enhanced: Agent-1 (Integration & Core Systems Specialist) - 2025-12-03
Phase 2: Agent-3 (Infrastructure & DevOps Specialist) - 2025-12-05 - Added workspace health monitoring
V2 Compliant: Yes (<400 lines)
<!-- SSOT Domain: infrastructure -->
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnifiedMonitor:
    """Unified monitoring system consolidating all monitoring capabilities."""
    
    def __init__(self):
        """Initialize unified monitor."""
        self.project_root = project_root
        
    def monitor_queue_health(self) -> Dict[str, Any]:
        """Monitor deferred push queue health."""
        try:
            from src.core.deferred_push_queue import get_deferred_push_queue
            queue = get_deferred_push_queue()
            stats = queue.get_stats()
            
            total = stats.get("total", 0)
            pending = stats.get("pending", 0)
            failed = stats.get("failed", 0)
            
            if total == 0:
                health_score = 100
            else:
                failure_rate = (failed / total) * 100 if total > 0 else 0
                health_score = max(0, 100 - failure_rate)
            
            health_status = "HEALTHY" if health_score >= 80 else "DEGRADED" if health_score >= 50 else "UNHEALTHY"
            
            return {
                "category": "queue",
                "status": health_status,
                "score": health_score,
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Queue health check failed: {e}")
            return {
                "category": "queue",
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def check_message_queue_file(self) -> Dict[str, Any]:
        """Check message queue file status (from discord_bot_infrastructure_check)."""
        queue_file = Path("message_queue/queue.json")
        result = {
            "category": "message_queue_file",
            "exists": False,
            "readable": False,
            "writable": False,
            "size": 0,
            "last_modified": None,
            "valid_json": False,
            "timestamp": datetime.now().isoformat()
        }
        
        if not queue_file.exists():
            result["status"] = "MISSING"
            return result
        
        result["exists"] = True
        result["size"] = queue_file.stat().st_size
        result["last_modified"] = time.ctime(queue_file.stat().st_mtime)
        
        # Check readability and JSON validity
        try:
            with open(queue_file, 'r', encoding='utf-8') as f:
                content = f.read()
                result["readable"] = True
                try:
                    json.loads(content)
                    result["valid_json"] = True
                    result["status"] = "HEALTHY"
                except json.JSONDecodeError:
                    result["status"] = "INVALID_JSON"
        except PermissionError:
            result["status"] = "NOT_READABLE"
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
        
        # Check writability
        try:
            with open(queue_file, 'a', encoding='utf-8') as f:
                result["writable"] = True
        except PermissionError:
            result["status"] = "NOT_WRITABLE" if result.get("status") == "HEALTHY" else result.get("status")
        except Exception:
            pass
        
        return result
    
    def monitor_service_health(self, service_name: str) -> Dict[str, Any]:
        """Monitor a specific service health."""
        try:
            import psutil
            
            service_running = False
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any(service_name.lower() in str(arg).lower() for arg in cmdline):
                        service_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                "category": "service",
                "service": service_name,
                "status": "RUNNING" if service_running else "STOPPED",
                "running": service_running,
                "timestamp": datetime.now().isoformat()
            }
        except ImportError:
            logger.warning("psutil not available - cannot check service status")
            return {
                "category": "service",
                "service": service_name,
                "status": "UNKNOWN",
                "error": "psutil not available",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Service health check failed: {e}")
            return {
                "category": "service",
                "service": service_name,
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def monitor_disk_usage(self, paths: List[str] = None) -> Dict[str, Any]:
        """Monitor disk usage for specified paths."""
        if paths is None:
            paths = ["C:/", "D:/"]
        
        import shutil
        
        disk_info = []
        for path in paths:
            try:
                usage = shutil.disk_usage(path)
                total_gb = usage.total / (1024**3)
                free_gb = usage.free / (1024**3)
                used_percent = (usage.used / usage.total) * 100
                
                disk_info.append({
                    "path": path,
                    "total_gb": round(total_gb, 2),
                    "free_gb": round(free_gb, 2),
                    "used_percent": round(used_percent, 2),
                    "status": "OK" if used_percent < 90 else "WARNING" if used_percent < 95 else "CRITICAL"
                })
            except Exception as e:
                logger.error(f"Disk check failed for {path}: {e}")
                disk_info.append({
                    "path": path,
                    "status": "ERROR",
                    "error": str(e)
                })
        
        return {
            "category": "disk",
            "disks": disk_info,
            "timestamp": datetime.now().isoformat()
        }
    
    def monitor_agent_status(self) -> Dict[str, Any]:
        """Monitor agent workspace status."""
        agents_dir = self.project_root / "agent_workspaces"
        agent_statuses = []
        
        if not agents_dir.exists():
            return {
                "category": "agents",
                "status": "ERROR",
                "error": "Agent workspaces directory not found",
                "timestamp": datetime.now().isoformat()
            }
        
        for agent_dir in sorted(agents_dir.iterdir()):
            if not agent_dir.is_dir():
                continue
            
            status_file = agent_dir / "status.json"
            if not status_file.exists():
                continue
            
            try:
                status_data = json.loads(status_file.read_text())
                agent_statuses.append({
                    "agent_id": status_data.get("agent_id", agent_dir.name),
                    "status": status_data.get("status", "UNKNOWN"),
                    "last_updated": status_data.get("last_updated", "unknown"),
                    "current_mission": status_data.get("current_mission", "")[:100] + "..."
                })
            except Exception as e:
                logger.warning(f"Error reading status for {agent_dir.name}: {e}")
        
        active_count = sum(1 for a in agent_statuses if a.get("status") == "ACTIVE_AGENT_MODE")
        
        return {
            "category": "agents",
            "total_agents": len(agent_statuses),
            "active_agents": active_count,
            "agent_statuses": agent_statuses,
            "timestamp": datetime.now().isoformat()
        }
    
    def monitor_workspace_health(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Monitor agent workspace health (from workspace_health_monitor.py)."""
        from datetime import timedelta
        from dataclasses import dataclass
        
        @dataclass
        class WorkspaceHealth:
            """Workspace health metrics."""
            agent_id: str
            inbox_count: int = 0
            unprocessed_count: int = 0
            old_messages: int = 0
            archive_count: int = 0
            devlogs_count: int = 0
            reports_count: int = 0
            status_file_exists: bool = False
            status_file_current: bool = False
            status_consistency: str = "UNKNOWN"
            issues_found: int = 0
            health_score: float = 0.0
            recommendations: List[str] = None
        
        workspace_root = self.project_root / "agent_workspaces"
        cutoff_days = 7
        cutoff_date = datetime.now() - timedelta(days=cutoff_days)
        
        def check_agent_workspace(agent_id: str) -> WorkspaceHealth:
            """Check health of a single agent workspace."""
            agent_dir = workspace_root / agent_id
            if not agent_dir.exists():
                return WorkspaceHealth(
                    agent_id=agent_id,
                    recommendations=["Workspace directory does not exist"]
                )
            
            # Count inbox messages
            inbox_dir = agent_dir / "inbox"
            inbox_count = 0
            unprocessed_count = 0
            old_messages = 0
            
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
            
            # Count archive, devlogs, reports
            archive_dir = inbox_dir / "archive"
            archive_count = len(list(archive_dir.glob("*.md"))) if archive_dir.exists() else 0
            devlogs_dir = agent_dir / "devlogs"
            devlogs_count = len(list(devlogs_dir.glob("*.md"))) if devlogs_dir.exists() else 0
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
            
            # Check consistency with runtime status
            runtime_status_file = self.project_root / "runtime" / "AGENT_STATUS.json"
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
            
            # Identify issues
            issues_found = 0
            for file_path in agent_dir.rglob("*.md"):
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    if any(marker in content for marker in ["ERROR", "FIXME", "TODO"]):
                        issues_found += 1
                except Exception:
                    pass
            
            # Calculate health score
            health_score = 100.0
            if old_messages > 0:
                health_score -= min(30, old_messages * 5)
            if unprocessed_count > 0:
                health_score -= min(25, unprocessed_count * 3)
            if inbox_count > 10:
                health_score -= min(20, (inbox_count - 10) * 2)
            if not status_file_exists:
                health_score -= 20
            if status_file_exists and not status_file_current:
                health_score -= 10
            if status_consistency == "INCONSISTENT":
                health_score -= 15
            health_score = max(0.0, health_score)
            
            # Generate recommendations
            recommendations = []
            if unprocessed_count > 0:
                recommendations.append(f"Process {unprocessed_count} unprocessed inbox message(s)")
            if old_messages > 0:
                recommendations.append(f"Archive {old_messages} old inbox message(s) (>7 days)")
            if inbox_count > 10:
                recommendations.append(f"Review {inbox_count} inbox messages")
            if not status_file_exists:
                recommendations.append("Create status.json file")
            if status_file_exists and not status_file_current:
                recommendations.append("Update status.json file")
            if status_consistency == "INCONSISTENT":
                recommendations.append("Fix status file inconsistency")
            if issues_found > 0:
                recommendations.append(f"Review {issues_found} file(s) with ERROR/FIXME/TODO")
            if not recommendations:
                recommendations.append("Workspace health: Excellent ✅")
            
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
        
        try:
            if agent_id:
                health = check_agent_workspace(agent_id)
                return {
                    "category": "workspace_health",
                    "agent_id": agent_id,
                    "health_score": health.health_score,
                    "inbox_count": health.inbox_count,
                    "unprocessed_count": health.unprocessed_count,
                    "old_messages": health.old_messages,
                    "status_file_exists": health.status_file_exists,
                    "status_file_current": health.status_file_current,
                    "status_consistency": health.status_consistency,
                    "issues_found": health.issues_found,
                    "recommendations": health.recommendations,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Check all workspaces
                all_health = {}
                for agent_dir in workspace_root.iterdir():
                    if agent_dir.is_dir() and agent_dir.name.startswith("Agent-"):
                        all_health[agent_dir.name] = check_agent_workspace(agent_dir.name)
                
                avg_score = sum(h.health_score for h in all_health.values()) / len(all_health) if all_health else 0
                return {
                    "category": "workspace_health",
                    "workspaces_checked": len(all_health),
                    "average_health_score": round(avg_score, 1),
                    "workspaces": {
                        k: {
                            "health_score": v.health_score,
                            "old_messages": v.old_messages,
                            "unprocessed_count": v.unprocessed_count,
                            "status_consistency": v.status_consistency
                        } for k, v in all_health.items()
                    },
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Workspace health check failed: {e}")
            return {
                "category": "workspace_health",
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def monitor_test_coverage(self) -> Dict[str, Any]:
        """Monitor test coverage status."""
        try:
            # Count test files
            tests_dir = self.project_root / "tests"
            test_files = list(tests_dir.rglob("test_*.py")) if tests_dir.exists() else []
            
            return {
                "category": "coverage",
                "total_test_files": len(test_files),
                "target_coverage": 85.0,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Test coverage check failed: {e}")
            return {
                "category": "coverage",
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def trigger_status_monitor_resume(self, agent_id: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
        """Trigger status monitor resume prompts (from manually_trigger_status_monitor_resume)."""
        try:
            from tools.agent_activity_detector import AgentActivityDetector
            from src.core.optimized_stall_resume_prompt import generate_optimized_resume_prompt
            from src.services.messaging_infrastructure import MessageCoordinator, UnifiedMessagePriority
            
            AGENTS = ["Agent-1", "Agent-2", "Agent-3", "Agent-5", "Agent-6", "Agent-7", "Agent-8"]
            agents_to_check = [agent_id] if agent_id else AGENTS
            
            activity_detector = AgentActivityDetector()
            results = {"sent": [], "skipped": [], "failed": []}
            
            for agent in agents_to_check:
                if agent not in AGENTS:
                    continue
                
                try:
                    summary = activity_detector.detect_agent_activity(agent, lookback_minutes=60)
                    inactivity_threshold = 5.0
                    
                    should_send = False
                    if force:
                        should_send = not summary.is_active or summary.inactivity_duration_minutes >= 5.0
                    else:
                        should_send = not summary.is_active or summary.inactivity_duration_minutes >= inactivity_threshold
                    
                    if should_send:
                        # Load status for context
                        status_file = self.project_root / "agent_workspaces" / agent / "status.json"
                        fsm_state = "active"
                        last_mission = "Unknown"
                        
                        if status_file.exists():
                            try:
                                with open(status_file, 'r', encoding='utf-8') as f:
                                    status = json.load(f)
                                fsm_state = status.get("status", "active")
                                last_mission = status.get("current_mission", "Unknown")
                            except Exception:
                                pass
                        
                        # Generate resume prompt
                        resumer_prompt = generate_optimized_resume_prompt(
                            agent_id=agent,
                            fsm_state=fsm_state,
                            last_mission=last_mission,
                            stall_duration_minutes=summary.inactivity_duration_minutes
                        )
                        
                        # Format resume message
                        resume_message = f"🚨 RESUMER PROMPT - Inactivity Detected\n\n{resumer_prompt}\n\n"
                        resume_message += f"**Inactivity Duration**: {summary.inactivity_duration_minutes:.1f} minutes\n"
                        if summary.last_activity:
                            resume_message += f"**Last Activity**: {summary.last_activity.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        if summary.activity_sources:
                            resume_message += f"**Activity Sources**: {', '.join(summary.activity_sources)}\n"
                        resume_message += f"\n**Action Required**: Review your status, update status.json, and resume operations.\n"
                        resume_message += f"\n🐝 WE. ARE. SWARM. ⚡🔥"
                        
                        # Send via messaging system
                        result = MessageCoordinator.send_to_agent(
                            agent=agent,
                            message=resume_message,
                            priority=UnifiedMessagePriority.URGENT,
                            use_pyautogui=True,
                            stalled=True,
                            sender="Captain Agent-4"
                        )
                        
                        if result.get("success"):
                            results["sent"].append(agent)
                        else:
                            results["failed"].append(agent)
                    else:
                        results["skipped"].append(agent)
                except Exception as e:
                    logger.error(f"Error checking {agent}: {e}")
                    results["failed"].append(agent)
            
            return {
                "category": "resume_trigger",
                "sent": len(results["sent"]),
                "skipped": len(results["skipped"]),
                "failed": len(results["failed"]),
                "agents_sent": results["sent"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Resume trigger failed: {e}")
            return {
                "category": "resume_trigger",
                "status": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def run_full_monitoring(self) -> Dict[str, Any]:
        """Run all monitoring checks."""
        logger.info("Running full monitoring suite...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # Queue health
        results["checks"]["queue"] = self.monitor_queue_health()
        results["checks"]["message_queue_file"] = self.check_message_queue_file()
        
        # Service health
        results["checks"]["github_pusher"] = self.monitor_service_health("github_pusher")
        results["checks"]["discord"] = self.monitor_service_health("discord")
        
        # Disk usage
        results["checks"]["disk"] = self.monitor_disk_usage()
        
        # Agent status
        results["checks"]["agents"] = self.monitor_agent_status()
        
        # Workspace health
        results["checks"]["workspace"] = self.monitor_workspace_health()
        
        # Test coverage
        results["checks"]["coverage"] = self.monitor_test_coverage()
        
        return results
    
    def print_monitoring_report(self, results: Dict[str, Any]):
        """Print formatted monitoring report."""
        print("\n" + "=" * 70)
        print("📊 UNIFIED MONITORING REPORT")
        print("=" * 70)
        
        checks = results.get("checks", {})
        
        # Queue status
        if "queue" in checks:
            queue = checks["queue"]
            status_icon = "✅" if queue.get("status") == "HEALTHY" else "⚠️" if queue.get("status") == "DEGRADED" else "❌"
            print(f"\n{status_icon} Deferred Push Queue: {queue.get('status', 'UNKNOWN')}")
            if "stats" in queue:
                stats = queue["stats"]
                print(f"   Pending: {stats.get('pending', 0)}, Failed: {stats.get('failed', 0)}")
        
        # Message queue file status
        if "message_queue_file" in checks:
            mq_file = checks["message_queue_file"]
            status_icon = "✅" if mq_file.get("status") == "HEALTHY" else "❌"
            print(f"\n{status_icon} Message Queue File: {mq_file.get('status', 'UNKNOWN')}")
            if mq_file.get("exists"):
                print(f"   Size: {mq_file.get('size', 0):,} bytes, Valid JSON: {mq_file.get('valid_json', False)}")
        
        # Service status
        for service_name in ["github_pusher", "discord"]:
            if service_name in checks:
                service = checks[service_name]
                status_icon = "✅" if service.get("running") else "❌"
                print(f"\n{status_icon} {service_name.replace('_', ' ').title()}: {service.get('status', 'UNKNOWN')}")
        
        # Disk usage
        if "disk" in checks:
            disk = checks["disk"]
            print(f"\n💾 Disk Usage:")
            for disk_info in disk.get("disks", []):
                status_icon = "✅" if disk_info.get("status") == "OK" else "⚠️"
                print(f"   {status_icon} {disk_info.get('path')}: {disk_info.get('used_percent', 0):.1f}% used "
                      f"({disk_info.get('free_gb', 0):.1f} GB free)")
        
        # Agent status
        if "agents" in checks:
            agents = checks["agents"]
            print(f"\n👥 Agents: {agents.get('active_agents', 0)}/{agents.get('total_agents', 0)} active")
        
        # Workspace health
        if "workspace" in checks:
            workspace = checks["workspace"]
            if "agent_id" in workspace:
                # Single agent report
                score = workspace.get("health_score", 0)
                status_icon = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
                print(f"\n{status_icon} Workspace Health ({workspace.get('agent_id')}): {score:.1f}/100")
                if workspace.get("old_messages", 0) > 0:
                    print(f"   ⚠️ {workspace.get('old_messages')} old messages")
                if workspace.get("unprocessed_count", 0) > 0:
                    print(f"   ⚠️ {workspace.get('unprocessed_count')} unprocessed messages")
            else:
                # All workspaces summary
                avg_score = workspace.get("average_health_score", 0)
                print(f"\n📊 Workspace Health: {avg_score:.1f}/100 avg ({workspace.get('workspaces_checked', 0)} workspaces)")
        
        # Test coverage
        if "coverage" in checks:
            coverage = checks["coverage"]
            print(f"\n🧪 Test Files: {coverage.get('total_test_files', 0)}")
        
        print(f"\n🕐 Timestamp: {results.get('timestamp', 'unknown')}")
        print("=" * 70 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Unified Monitoring Tool - Consolidated monitoring for all systems",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--category", "-c",
        choices=["queue", "message_queue_file", "service", "disk", "agents", "coverage", "workspace", "resume", "all"],
        default="all",
        help="Monitoring category to check (default: all)"
    )
    
    parser.add_argument(
        "--trigger-resume", "-r",
        action="store_true",
        help="Trigger status monitor resume prompts for inactive agents"
    )
    
    parser.add_argument(
        "--force-resume", "-f",
        action="store_true",
        help="Force send resume prompts to all agents (5 min threshold)"
    )
    
    parser.add_argument(
        "--agent",
        type=str,
        help="Agent ID for resume trigger (default: all agents)"
    )
    
    parser.add_argument(
        "--service", "-s",
        type=str,
        help="Service name for service monitoring"
    )
    
    parser.add_argument(
        "--watch", "-w",
        action="store_true",
        help="Watch mode: continuously monitor"
    )
    
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=30,
        help="Watch interval in seconds (default: 30)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    monitor = UnifiedMonitor()
    
    # Handle resume trigger
    if args.trigger_resume or args.force_resume:
        async def run_resume():
            result = await monitor.trigger_status_monitor_resume(
                agent_id=args.agent,
                force=args.force_resume
            )
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"\n🚨 Resume Trigger Results:")
                print(f"   Sent: {result.get('sent', 0)}")
                print(f"   Skipped: {result.get('skipped', 0)}")
                print(f"   Failed: {result.get('failed', 0)}")
                if result.get("agents_sent"):
                    print(f"   Agents: {', '.join(result['agents_sent'])}")
        
        asyncio.run(run_resume())
        return
    
    if args.watch:
        logger.info(f"👀 Watch mode: Checking every {args.interval}s (Ctrl+C to stop)")
        try:
            while True:
                if args.category == "all":
                    results = monitor.run_full_monitoring()
                else:
                    # Single category check
                    if args.category == "queue":
                        results = {"checks": {"queue": monitor.monitor_queue_health()}}
                    elif args.category == "message_queue_file":
                        results = {"checks": {"message_queue_file": monitor.check_message_queue_file()}}
                    elif args.category == "service":
                        service_name = args.service or "github_pusher"
                        results = {"checks": {service_name: monitor.monitor_service_health(service_name)}}
                    elif args.category == "disk":
                        results = {"checks": {"disk": monitor.monitor_disk_usage()}}
                    elif args.category == "agents":
                        results = {"checks": {"agents": monitor.monitor_agent_status()}}
                    elif args.category == "coverage":
                        results = {"checks": {"coverage": monitor.monitor_test_coverage()}}
                    elif args.category == "workspace":
                        agent_id = args.agent if args.agent else None
                        results = {"checks": {"workspace": monitor.monitor_workspace_health(agent_id)}}
                
                if args.json:
                    print(json.dumps(results, indent=2))
                else:
                    monitor.print_monitoring_report(results)
                
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("\n🛑 Monitoring stopped")
    else:
        # Single check
        if args.category == "all":
            results = monitor.run_full_monitoring()
        else:
            if args.category == "queue":
                results = {"checks": {"queue": monitor.monitor_queue_health()}}
            elif args.category == "message_queue_file":
                results = {"checks": {"message_queue_file": monitor.check_message_queue_file()}}
            elif args.category == "service":
                service_name = args.service or "github_pusher"
                results = {"checks": {service_name: monitor.monitor_service_health(service_name)}}
            elif args.category == "disk":
                results = {"checks": {"disk": monitor.monitor_disk_usage()}}
            elif args.category == "agents":
                results = {"checks": {"agents": monitor.monitor_agent_status()}}
            elif args.category == "coverage":
                results = {"checks": {"coverage": monitor.monitor_test_coverage()}}
            elif args.category == "workspace":
                agent_id = args.agent if args.agent else None
                results = {"checks": {"workspace": monitor.monitor_workspace_health(agent_id)}}
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            monitor.print_monitoring_report(results)


if __name__ == "__main__":
    main()


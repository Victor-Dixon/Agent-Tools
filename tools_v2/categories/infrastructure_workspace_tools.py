#!/usr/bin/env python3
"""
Infrastructure Workspace Tools - Agent Toolbelt V2
===================================================

Workspace management and agent status tools for infrastructure operations.

V2 Compliance: <400 lines
Author: Agent-2 (Architecture & Design) - Split from infrastructure_tools.py
Date: 2025-01-27
"""

import logging
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec

logger = logging.getLogger(__name__)


class WorkspaceHealthMonitorTool(IToolAdapter):
    """Monitor workspace health for agent workspaces."""
    def get_name(self) -> str:
        return "workspace_health_monitor"
    def get_description(self) -> str:
        return "Monitor agent workspace health (inbox, status, recommendations)"
    def get_spec(self) -> ToolSpec:
        return ToolSpec(name="workspace_health_monitor", version="1.0.0", category="infrastructure",
            summary="Monitor agent workspace health", required_params=[],
            optional_params={"agent_id": None, "check_all": False})
    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])
    def execute(self, params: dict[str, Any] = None, context: dict[str, Any] | None = None) -> ToolResult:
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))
            from workspace_health_monitor import WorkspaceHealthMonitor
            params = params or {}
            monitor = WorkspaceHealthMonitor()
            if params.get("check_all"):
                results = monitor.check_all_workspaces()
                output = {"mode": "all", "results": {k: {"score": v.health_score, "inbox": v.inbox_count,
                    "old": v.old_messages, "status_ok": v.status_file_current, "recs": v.recommendations}
                    for k, v in results.items()}}
            elif params.get("agent_id"):
                h = monitor.check_agent_workspace(params["agent_id"])
                output = {"agent_id": params["agent_id"], "score": h.health_score,
                    "inbox": h.inbox_count, "old": h.old_messages, "recs": h.recommendations}
            else:
                return ToolResult(success=False, output=None,
                    error_message="Must specify agent_id or check_all=True", exit_code=1)
            return ToolResult(success=True, output=output)
        except Exception as e:
            logger.error(f"Workspace health monitor failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class WorkspaceAutoCleanerTool(IToolAdapter):
    """Automated workspace cleanup tool."""
    def get_name(self) -> str:
        return "workspace_auto_cleaner"
    def get_description(self) -> str:
        return "Automated workspace cleanup (archive old messages, clean temp files)"
    def get_spec(self) -> ToolSpec:
        return ToolSpec(name="workspace_auto_cleaner", version="1.0.0", category="infrastructure",
            summary="Automated workspace cleanup", required_params=["agent_id"],
            optional_params={"archive": False, "clean_temp": False, "full": False, "dry_run": True})
    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return self.get_spec().validate_params(params)
    def execute(self, params: dict[str, Any] = None, context: dict[str, Any] | None = None) -> ToolResult:
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))
            from workspace_auto_cleaner import archive_old_messages, clean_temp_files, organize_workspace
            params = params or {}
            agent_id = params.get("agent_id")
            if not agent_id:
                return ToolResult(success=False, output=None, error_message="agent_id required", exit_code=1)
            dry_run = params.get("dry_run", True)
            full = params.get("full", False)
            results = {}
            if params.get("archive") or full:
                results["archived"] = archive_old_messages(agent_id, dry_run=dry_run)
            if params.get("clean_temp") or full:
                results["cleaned"] = clean_temp_files(agent_id, dry_run=dry_run)
            if full:
                results["organized"] = organize_workspace(agent_id, dry_run=dry_run)
            return ToolResult(success=True, output={"agent_id": agent_id, "dry_run": dry_run, "results": results})
        except Exception as e:
            logger.error(f"Workspace auto cleaner failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class AgentStatusQuickCheckTool(IToolAdapter):
    """Quick check agent status.json for current missions and progress."""
    def get_name(self) -> str:
        return "agent_status_check"
    def get_description(self) -> str:
        return "Quick check agent status.json for missions, points, and progress"
    def get_spec(self) -> ToolSpec:
        return ToolSpec(name="agent_status_check", version="1.0.0", category="infrastructure",
            summary="Quick agent status check", required_params=[],
            optional_params={"agent_id": None, "check_all": False, "detail": False})
    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])
    def execute(self, params: dict[str, Any] = None, context: dict[str, Any] | None = None) -> ToolResult:
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))
            # NOTE: agent_status_quick_check consolidated into unified_agent_status_monitor
            from unified_agent_status_monitor import UnifiedAgentStatusMonitor
            params = params or {}
            monitor = UnifiedAgentStatusMonitor(Path("agent_workspaces").parent)
            if params.get("check_all"):
                output = {"mode": "all", "agents": {}}
                for agent_dir in (Path("agent_workspaces")).iterdir():
                    if agent_dir.is_dir() and agent_dir.name.startswith("Agent-"):
                        status = monitor.get_quick_status(agent_dir.name)
                        if status:
                            output["agents"][agent_dir.name] = {
                                "mission": status.get("mission", "None"),
                                "status": status.get("status", "Unknown"),
                                "points": status.get("points", 0)
                            }
            elif params.get("agent_id"):
                status = monitor.get_quick_status(params["agent_id"])
                if not status:
                    return ToolResult(success=False, output=None, error_message=f"Status not found for {params['agent_id']}", exit_code=1)
                output = {"agent_id": params["agent_id"], "mission": status.get("mission"), "status": status.get("status"),
                    "points": status.get("points", 0), "phase": status.get("phase")}
            else:
                return ToolResult(success=False, output=None, error_message="Must specify agent_id or check_all=True", exit_code=1)
            return ToolResult(success=True, output=output)
        except Exception as e:
            logger.error(f"Agent status check failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class AutoStatusUpdaterTool(IToolAdapter):
    """Automatically update agent status.json based on activity."""
    def get_name(self) -> str:
        return "auto_status_updater"
    def get_description(self) -> str:
        return "Automatically update agent status.json based on activity detection"
    def get_spec(self) -> ToolSpec:
        return ToolSpec(name="auto_status_updater", version="1.0.0", category="infrastructure",
            summary="Auto-update agent status", required_params=["agent_id"],
            optional_params={"activity": None, "milestone": None, "points": None, "task_complete": None, "auto_commit": True})
    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return self.get_spec().validate_params(params)
    def execute(self, params: dict[str, Any] = None, context: dict[str, Any] | None = None) -> ToolResult:
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))
            from auto_status_updater import AutoStatusUpdater
            params = params or {}
            agent_id = params.get("agent_id")
            if not agent_id:
                return ToolResult(success=False, output=None, error_message="agent_id required", exit_code=1)
            updater = AutoStatusUpdater(auto_commit=params.get("auto_commit", True))
            success = updater.update_status(agent_id=agent_id, activity=params.get("activity"),
                milestone=params.get("milestone"), points=params.get("points"), task_complete=params.get("task_complete"))
            return ToolResult(success=success, output={"agent_id": agent_id, "updated": success})
        except Exception as e:
            logger.error(f"Auto status updater failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class SessionTransitionAutomatorTool(IToolAdapter):
    """Automate session transition deliverables and handoff."""
    def get_name(self) -> str:
        return "session_transition_automator"
    def get_description(self) -> str:
        return "Automate session transition deliverables (passdown, devlog, handoff)"
    def get_spec(self) -> ToolSpec:
        return ToolSpec(name="session_transition_automator", version="1.0.0", category="infrastructure",
            summary="Automate session transition", required_params=["agent_id"],
            optional_params={"generate_all": True, "send_handoff": True})
    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return self.get_spec().validate_params(params)
    def execute(self, params: dict[str, Any] = None, context: dict[str, Any] | None = None) -> ToolResult:
        try:
            import json
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))
            from session_transition_automator import SessionTransitionAutomator
            params = params or {}
            agent_id = params.get("agent_id")
            if not agent_id:
                return ToolResult(success=False, output=None, error_message="agent_id required", exit_code=1)
            automator = SessionTransitionAutomator(agent_id, Path("agent_workspaces"))
            if params.get("generate_all", True):
                status_file = Path(f"agent_workspaces/{agent_id}/status.json")
                status_data = json.loads(status_file.read_text()) if status_file.exists() else {}
                automator.generate_passdown(status_data)
                automator.create_devlog_template()
            return ToolResult(success=True, output={"agent_id": agent_id, "transition_complete": True})
        except Exception as e:
            logger.error(f"Session transition automator failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


class SwarmStatusBroadcasterTool(IToolAdapter):
    """Broadcast status messages to multiple agents."""
    def get_name(self) -> str:
        return "swarm_status_broadcaster"
    def get_description(self) -> str:
        return "Broadcast status messages to multiple agents for coordination"
    def get_spec(self) -> ToolSpec:
        return ToolSpec(name="swarm_status_broadcaster", version="1.0.0", category="infrastructure",
            summary="Broadcast to swarm", required_params=["message"],
            optional_params={"priority": "regular", "exclude_agents": None, "include_only": None})
    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return self.get_spec().validate_params(params)
    def execute(self, params: dict[str, Any] = None, context: dict[str, Any] | None = None) -> ToolResult:
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))
            from swarm_status_broadcaster import SwarmStatusBroadcaster
            params = params or {}
            broadcaster = SwarmStatusBroadcaster()
            results = broadcaster.broadcast(params["message"], priority=params.get("priority", "regular"),
                exclude_agents=params.get("exclude_agents"), include_only=params.get("include_only"))
            return ToolResult(success=True, output={"broadcast_results": results, "success_count": sum(1 for v in results.values() if v)})
        except Exception as e:
            logger.error(f"Swarm status broadcaster failed: {e}")
            return ToolResult(success=False, output=None, error_message=str(e), exit_code=1)


__all__ = [
    "WorkspaceHealthMonitorTool",
    "WorkspaceAutoCleanerTool",
    "AgentStatusQuickCheckTool",
    "AutoStatusUpdaterTool",
    "SessionTransitionAutomatorTool",
    "SwarmStatusBroadcasterTool",
]





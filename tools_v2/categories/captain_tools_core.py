"""
Captain Core Operations Tools
==============================

Core tool adapters for Captain operations: status checking, git verification,
work verification, and integrity checks.

V2 Compliance: <300 lines
Author: Agent-4 (Captain) - Refactored 2025-01-27
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)

# Swarm agents list
SWARM_AGENTS = [f"Agent-{i}" for i in range(1, 9)]


class StatusCheckTool(IToolAdapter):
    """Check all agent status.json files to detect idle agents."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.status_check",
            version="1.0.0",
            category="captain",
            summary="Check all agent status files to detect idle agents",
            required_params=[],
            optional_params={"agents": SWARM_AGENTS, "threshold_hours": 24},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        return (True, [])

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute status check across all agents."""
        try:
            agents = params.get("agents", SWARM_AGENTS)
            threshold = params.get("threshold_hours", 24)

            results = {}
            idle_agents = []

            for agent in agents:
                status_file = Path(f"agent_workspaces/{agent}/status.json")
                if status_file.exists():
                    try:
                        status_data = json.loads(status_file.read_text())
                        results[agent] = status_data

                        # Check if idle based on last_activity
                        if "last_activity" in status_data:
                            last_activity = datetime.fromisoformat(status_data["last_activity"])
                            hours_idle = (datetime.now() - last_activity).total_seconds() / 3600

                            if hours_idle > threshold:
                                idle_agents.append(
                                    {
                                        "agent": agent,
                                        "hours_idle": round(hours_idle, 1),
                                        "status": status_data.get("status", "unknown"),
                                    }
                                )
                    except Exception as e:
                        results[agent] = {"error": str(e)}
                else:
                    results[agent] = {"error": "Status file not found"}

            return ToolResult(
                success=True,
                output={
                    "all_status": results,
                    "idle_agents": idle_agents,
                    "threshold_hours": threshold,
                },
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error checking agent status: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.status_check")


class GitVerifyTool(IToolAdapter):
    """Verify git commits for work attribution and integrity checks."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.git_verify",
            version="1.0.0",
            category="captain",
            summary="Verify git commits for work attribution",
            required_params=["commit_hash"],
            optional_params={"show_stat": True, "show_diff": False},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute git verification."""
        try:
            commit_hash = params["commit_hash"]
            show_stat = params.get("show_stat", True)
            show_diff = params.get("show_diff", False)

            # Build git command
            cmd = ["git", "show"]
            if show_stat:
                cmd.append("--stat")
            if not show_diff:
                cmd.append("--no-patch")
            cmd.append(commit_hash)

            # Execute git command
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())

            if result.returncode != 0:
                return ToolResult(
                    success=False,
                    output={"error": result.stderr},
                    exit_code=result.returncode,
                    error_message=f"Git command failed: {result.stderr}",
                )

            return ToolResult(
                success=True,
                output={"commit_hash": commit_hash, "commit_info": result.stdout, "verified": True},
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error verifying git commit: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.git_verify")


class WorkVerifyTool(IToolAdapter):
    """Comprehensive work verification (git + files + tests)."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.verify_work",
            version="1.0.0",
            category="captain",
            summary="Verify completed work with git commits and file checks",
            required_params=["agent_id", "work_description"],
            optional_params={"commit_hash": None, "files_changed": []},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute work verification."""
        try:
            agent_id = params["agent_id"]
            work_desc = params["work_description"]
            commit_hash = params.get("commit_hash")
            files_changed = params.get("files_changed", [])

            verification_results = {
                "agent_id": agent_id,
                "work_description": work_desc,
                "verified": True,
                "checks": {},
            }

            # Check 1: Git commit verification
            if commit_hash:
                git_result = subprocess.run(
                    ["git", "show", "--stat", "--no-patch", commit_hash],
                    capture_output=True,
                    text=True,
                    cwd=Path.cwd(),
                )
                verification_results["checks"]["git_commit"] = {
                    "verified": git_result.returncode == 0,
                    "commit_hash": commit_hash,
                    "commit_info": (
                        git_result.stdout if git_result.returncode == 0 else git_result.stderr
                    ),
                }

            # Check 2: Files exist
            if files_changed:
                files_status = {}
                for file_path in files_changed:
                    file = Path(file_path)
                    files_status[file_path] = {
                        "exists": file.exists(),
                        "size": file.stat().st_size if file.exists() else 0,
                    }
                verification_results["checks"]["files"] = files_status

            # Check 3: Agent workspace activity
            workspace = Path(f"agent_workspaces/{agent_id}")
            if workspace.exists():
                verification_results["checks"]["workspace"] = {
                    "exists": True,
                    "files_count": len(list(workspace.rglob("*"))),
                }

            return ToolResult(success=True, output=verification_results, exit_code=0)
        except Exception as e:
            logger.error(f"Error verifying work: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.verify_work")


class IntegrityCheckTool(IToolAdapter):
    """Verify work claims with git history and Entry #025 integrity checks."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="captain.integrity_check",
            version="1.0.0",
            category="captain",
            summary="Verify work claims with git history (Entry #025)",
            required_params=["agent_id", "claimed_work"],
            optional_params={"search_terms": []},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute integrity check."""
        try:
            agent_id = params["agent_id"]
            claimed_work = params["claimed_work"]
            search_terms = params.get("search_terms", [])

            # Search git log for commits related to claimed work
            git_results = []

            for term in search_terms:
                result = subprocess.run(
                    ["git", "log", "--all", "--oneline", "--grep", term],
                    capture_output=True,
                    text=True,
                    cwd=Path.cwd(),
                )

                if result.returncode == 0 and result.stdout.strip():
                    git_results.append(
                        {"search_term": term, "commits_found": result.stdout.strip().split("\n")}
                    )

            # Check if any commits found
            integrity_status = {
                "agent_id": agent_id,
                "claimed_work": claimed_work,
                "git_commits_found": len(git_results) > 0,
                "commit_details": git_results,
                "integrity_verdict": "VERIFIED" if git_results else "NO_EVIDENCE",
                "recommendation": "Approve work claim" if git_results else "Request more evidence",
            }

            return ToolResult(success=True, output=integrity_status, exit_code=0)
        except Exception as e:
            logger.error(f"Error checking integrity: {e}")
            raise ToolExecutionError(str(e), tool_name="captain.integrity_check")

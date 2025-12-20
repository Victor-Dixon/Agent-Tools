#!/usr/bin/env python3
"""
Open Source Contribution Tools
===============================

Tools for OSS project management and contributions.

Author: Agent-7 - Repository Cloning Specialist
Created: 2025-10-13
"""

import logging
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec

logger = logging.getLogger(__name__)


class OSSCloneTool(IToolAdapter):
    """Clone external OSS project."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="oss.clone",
            version="1.0.0",
            category="oss",
            summary="Clone external OSS project",
            required_params=["github_url"],
            optional_params={"project_name": None}
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        if "github_url" not in params:
            return False, ["github_url"]
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Execute project clone."""
        try:
            from src.opensource.project_manager import OpenSourceProjectManager

            github_url = params.get("github_url")
            project_name = params.get("project_name")

            if not github_url:
                return ToolResult(success=False, output=None, exit_code=1, error_message="github_url required")

            pm = OpenSourceProjectManager()
            project_id = pm.clone_project(github_url, project_name)

            if project_id:
                project = pm.get_project(project_id)
                return ToolResult(
                    success=True,
                    output={
                        "project_id": project_id,
                        "name": project["name"],
                        "path": project["clone_path"],
                    },
                    exit_code=0
                )
            else:
                return ToolResult(success=False, output=None, exit_code=1, error_message="Clone failed")

        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class OSSFetchIssuesTool(IToolAdapter):
    """Fetch GitHub issues from OSS project."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="oss.issues",
            version="1.0.0",
            category="oss",
            summary="Fetch GitHub issues from OSS project",
            required_params=["project_id"],
            optional_params={"labels": []}
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        if "project_id" not in params:
            return False, ["project_id"]
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Execute issue fetching."""
        try:
            from src.opensource.github_integration import GitHubIntegration
            from src.opensource.project_manager import OpenSourceProjectManager

            project_id = params.get("project_id")
            labels = params.get("labels", [])

            if not project_id:
                return ToolResult(success=False, output=None, exit_code=1, error_message="project_id required")

            pm = OpenSourceProjectManager()
            github = GitHubIntegration()

            project = pm.get_project(project_id)
            if not project:
                return ToolResult(success=False, output=None, exit_code=1, error_message=f"Project not found: {project_id}")

            issues = github.fetch_issues(project["github_url"], labels)

            return ToolResult(success=True, output={"issues": issues, "count": len(issues)}, exit_code=0)

        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class OSSImportIssuesTool(IToolAdapter):
    """Import GitHub issues as tasks."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="oss.import",
            version="1.0.0",
            category="oss",
            summary="Import GitHub issues as tasks",
            required_params=["project_id"],
            optional_params={"labels": ["good first issue"], "max_tasks": 10}
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        if "project_id" not in params:
            return False, ["project_id"]
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Execute issue import."""
        try:
            from src.infrastructure.persistence.sqlite_task_repo import SqliteTaskRepository
            from src.opensource.github_integration import GitHubIntegration
            from src.opensource.project_manager import OpenSourceProjectManager
            from src.opensource.task_integration import OSSTaskIntegration

            project_id = params.get("project_id")
            labels = params.get("labels", ["good first issue"])
            max_tasks = params.get("max_tasks", 10)

            if not project_id:
                return ToolResult(success=False, output=None, exit_code=1, error_message="project_id required")

            pm = OpenSourceProjectManager()
            github = GitHubIntegration()
            repo = SqliteTaskRepository()
            integration = OSSTaskIntegration(pm, repo)

            project = pm.get_project(project_id)
            if not project:
                return ToolResult(success=False, output=None, exit_code=1, error_message=f"Project not found: {project_id}")

            issues = github.fetch_issues(project["github_url"], labels)
            task_ids = integration.bulk_import_issues(project_id, issues, max_tasks)

            return ToolResult(
                success=True,
                output={
                    "tasks_created": len(task_ids),
                    "task_ids": task_ids,
                },
                exit_code=0
            )

        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class OSSPortfolioTool(IToolAdapter):
    """Generate OSS contribution portfolio."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="oss.portfolio",
            version="1.0.0",
            category="oss",
            summary="Generate OSS contribution portfolio",
            required_params=[],
            optional_params={"format": "markdown"}
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Execute portfolio generation."""
        try:
            from src.opensource.contribution_tracker import ContributionTracker
            from src.opensource.portfolio_builder import PortfolioBuilder

            format_type = params.get("format", "markdown")

            tracker = ContributionTracker()
            builder = PortfolioBuilder(tracker)

            if format_type == "markdown":
                builder.generate_readme()
                return ToolResult(success=True, output={"format": "markdown", "file": "README.md"}, exit_code=0)
            elif format_type == "html":
                builder.generate_dashboard_html()
                return ToolResult(success=True, output={"format": "html", "file": "portfolio.html"}, exit_code=0)
            elif format_type == "json":
                builder.export_portfolio_json()
                return ToolResult(success=True, output={"format": "json", "file": "portfolio_export.json"}, exit_code=0)
            else:
                return ToolResult(success=False, output=None, exit_code=1, error_message=f"Unknown format: {format_type}")

        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))


class OSSStatusTool(IToolAdapter):
    """Get OSS contribution status."""

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="oss.status",
            version="1.0.0",
            category="oss",
            summary="Get OSS contribution status",
            required_params=[],
            optional_params={}
        )

    def validate(self, params: dict) -> tuple[bool, list[str]]:
        return True, []

    def execute(self, params: dict, context: dict | None = None) -> ToolResult:
        """Execute status check."""
        try:
            from src.opensource.contribution_tracker import ContributionTracker

            tracker = ContributionTracker()
            metrics = tracker.get_metrics()

            return ToolResult(
                success=True,
                output={
                    "total_projects": metrics.total_projects,
                    "total_prs": metrics.total_prs,
                    "merged_prs": metrics.merged_prs,
                    "merge_rate": (
                        (metrics.merged_prs / metrics.total_prs * 100) if metrics.total_prs > 0 else 0
                    ),
                    "reputation_score": metrics.reputation_score,
                },
                exit_code=0
            )

        except Exception as e:
            return ToolResult(success=False, output=None, exit_code=1, error_message=str(e))

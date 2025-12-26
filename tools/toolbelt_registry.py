"""
CLI Toolbelt Registry - Unified Tool Discovery
==============================================

Central registry for the consolidated Swarm Toolbelt.
Maps command-line flags to unified and specialized tools.

Architecture: WE ARE SWARM
Status: Consolidated (Phase 4 Complete)
"""

from typing import Any

TOOLS_REGISTRY: dict[str, dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # 🟢 UNIFIED TOOLS (The Big Three + Domain Unifieds)
    # -------------------------------------------------------------------------
    "monitor": {
        "name": "Unified Monitor",
        "module": "tools.monitoring.unified_monitor",
        "main_function": "main",
        "description": "System-wide monitoring (Queue, Service, Disk, Agents, Workspace)",
        "flags": ["--monitor", "-m"],
        "args_passthrough": True,
    },
    "validator": {
        "name": "Unified Validator",
        "module": "tools.validation.unified_validator",
        "main_function": "main",
        "description": "System-wide validation (SSOT, Imports, Config, Tracker)",
        "flags": ["--validate", "-V"],
        "args_passthrough": True,
    },
    "analyzer": {
        "name": "Unified Analyzer",
        "module": "tools.analysis.unified_analyzer",
        "main_function": "main",
        "description": "System-wide analysis (Repository, Structure, Complexity, Overlap)",
        "flags": ["--analyze", "-a"],
        "args_passthrough": True,
    },
    "agent": {
        "name": "Unified Agent Tools",
        "module": "tools.agent.unified_agent",
        "main_function": "main",
        "description": "Agent operations (Status, Tasks, Orientation, Onboarding)",
        "flags": ["--agent", "-A"],
        "args_passthrough": True,
    },
    "captain": {
        "name": "Unified Captain Tools",
        "module": "tools.captain.unified_captain",
        "main_function": "main",
        "description": "Captain operations (Inbox, Coordination, Mission Control)",
        "flags": ["--captain", "-C"],
        "args_passthrough": True,
    },
    "cleanup": {
        "name": "Unified Cleanup",
        "module": "tools.cleanup.unified_cleanup",
        "main_function": "main",
        "description": "System cleanup (Workspace, Archives, Logs)",
        "flags": ["--cleanup", "--clean"],
        "args_passthrough": True,
    },
    "discord": {
        "name": "Unified Discord",
        "module": "tools.discord.unified_discord",
        "main_function": "main",
        "description": "Discord operations (Bot, Webhooks, Verification)",
        "flags": ["--discord"],
        "args_passthrough": True,
    },
    "github": {
        "name": "Unified GitHub",
        "module": "tools.github.unified_github",
        "main_function": "main",
        "description": "GitHub operations (PRs, Issues, Repo Audit)",
        "flags": ["--github", "--gh"],
        "args_passthrough": True,
    },
    "verifier": {
        "name": "Unified Verifier",
        "module": "tools.verification.unified_verifier",
        "main_function": "main",
        "description": "Deep verification (CI/CD, Merge, Credentials, Test Health)",
        "flags": ["--verify"],
        "args_passthrough": True,
    },
    "wordpress": {
        "name": "Unified WordPress",
        "module": "tools.wordpress.unified_wordpress",
        "main_function": "main",
        "description": "WordPress operations (Deploy, Theme, Admin)",
        "flags": ["--wordpress", "--wp"],
        "args_passthrough": True,
    },

    # -------------------------------------------------------------------------
    # 🟡 GOLD TOOLS (Critical/Security/Recovery)
    # -------------------------------------------------------------------------
    "check-sensitive": {
        "name": "Sensitive File Checker",
        "module": "tools.security.check_sensitive_files",
        "main_function": "main",
        "description": "Scan for sensitive files and credentials",
        "flags": ["--check-sensitive", "--sec-check"],
        "args_passthrough": True,
    },
    "audit-imports": {
        "name": "Import Auditor",
        "module": "tools.validation.audit_imports",
        "main_function": "main",
        "description": "Audit Python imports and dependencies",
        "flags": ["--audit-imports"],
        "args_passthrough": True,
    },
    "diagnose-auth": {
        "name": "GitHub Auth Diagnoser",
        "module": "tools.debug.diagnose_github_cli_auth",
        "main_function": "main",
        "description": "Diagnose and fix GitHub CLI authentication",
        "flags": ["--diagnose-auth"],
        "args_passthrough": True,
    },
    "debug-queue": {
        "name": "Queue Debugger",
        "module": "tools.debug.debug_message_queue",
        "main_function": "main",
        "description": "Debug message queue contents and state",
        "flags": ["--debug-queue"],
        "args_passthrough": True,
    },
    "fix-queue": {
        "name": "Queue Fixer",
        "module": "tools.debug.fix_message_queue",
        "main_function": "main",
        "description": "Attempt to fix message queue issues",
        "flags": ["--fix-queue"],
        "args_passthrough": True,
    },
    "check-stuck": {
        "name": "Stuck Message Checker",
        "module": "tools.debug.check_stuck_messages",
        "main_function": "main",
        "description": "Identify stuck messages in the system",
        "flags": ["--check-stuck"],
        "args_passthrough": True,
    },
    "ci-debt": {
        "name": "CI Technical Debt Summary",
        "module": "tools.analysis.tech_debt_ci_summary",
        "main_function": "main",
        "description": "Summarize technical debt in CI pipelines",
        "flags": ["--ci-debt"],
        "args_passthrough": True,
    },
    "swarm-patterns": {
        "name": "Swarm Pattern Analyzer",
        "module": "tools.analysis.analyze_swarm_coordination_patterns",
        "main_function": "main",
        "description": "Analyze coordination patterns in the swarm",
        "flags": ["--swarm-patterns"],
        "args_passthrough": True,
    },
    "create-session": {
        "name": "Session Creator",
        "module": "tools.captain.create_work_session",
        "main_function": "main",
        "description": "Create a new work session structure",
        "flags": ["--create-session", "--session"],
        "args_passthrough": True,
    },
    "security-scan": {
        "name": "Unified Security Scanner",
        "module": "tools.security.unified_security_scanner",
        "main_function": "main",
        "description": "Comprehensive security scanner (Secrets, Deps, SAST)",
        "flags": ["--security-scan", "--scan-security"],
        "args_passthrough": True,
    },
    "debugger": {
        "name": "Unified Debugger",
        "module": "tools.debug.unified_debugger",
        "main_function": "main",
        "description": "System-wide debugging (Logs, Queue, Processes)",
        "flags": ["--debugger", "--debug"],
        "args_passthrough": True,
    },
    "environment": {
        "name": "Unified Environment",
        "module": "tools.devops.unified_environment",
        "main_function": "main",
        "description": "Environment verification and setup",
        "flags": ["--environment", "--env"],
        "args_passthrough": True,
    },

    # -------------------------------------------------------------------------
    # 🔵 DIAMOND TOOLS (High Value Specialists)
    # -------------------------------------------------------------------------
    "fix-types": {
        "name": "Type Annotation Fixer",
        "module": "tools.devops.type_annotation_fixer",
        "main_function": "main",
        "description": "Add and fix type annotations",
        "flags": ["--fix-types"],
        "args_passthrough": True,
    },
    "suggest-refactor": {
        "name": "Refactoring Suggester",
        "module": "tools.analysis.refactoring_suggestion_engine",
        "main_function": "main",
        "description": "Generate refactoring suggestions",
        "flags": ["--suggest-refactor"],
        "args_passthrough": True,
    },
    "analyze-consolidation": {
        "name": "Consolidation Analyzer",
        "module": "tools.analysis.consolidation_analyzer",
        "main_function": "main",
        "description": "Analyze opportunities for tool consolidation",
        "flags": ["--analyze-consolidation"],
        "args_passthrough": True,
    },
    "analyze-debt": {
        "name": "Technical Debt Analyzer",
        "module": "tools.analysis.technical_debt_analyzer",
        "main_function": "main",
        "description": "Deep scan for technical debt",
        "flags": ["--analyze-debt"],
        "args_passthrough": True,
    },
    "analyze-source": {
        "name": "Source Analyzer",
        "module": "tools.analysis.source_analyzer",
        "main_function": "main",
        "description": "Analyze source code statistics",
        "flags": ["--analyze-source"],
        "args_passthrough": True,
    },
    "analyze-tools": {
        "name": "Tool Analyzer",
        "module": "tools.analysis.comprehensive_tool_analyzer",
        "main_function": "main",
        "description": "Analyze the tool ecosystem itself",
        "flags": ["--analyze-tools"],
        "args_passthrough": True,
    },
    "auto-cleanup": {
        "name": "Auto Workspace Cleaner",
        "module": "tools.cleanup.workspace_auto_cleaner",
        "main_function": "main",
        "description": "Automated workspace maintenance",
        "flags": ["--auto-cleanup"],
        "args_passthrough": True,
    },
    "session-cleanup": {
        "name": "Session Cleanup",
        "module": "tools.cleanup.session_cleanup_automation",
        "main_function": "main",
        "description": "Cleanup old sessions",
        "flags": ["--session-cleanup"],
        "args_passthrough": True,
    },
    "generate-docs": {
        "name": "Documentation Generator",
        "module": "tools.devops.documentation_assistant",
        "main_function": "main",
        "description": "Assist in generating documentation",
        "flags": ["--generate-docs"],
        "args_passthrough": True,
    },
    "seo-extract": {
        "name": "SEO Meta Extractor",
        "module": "tools.analysis.seo_meta_tag_extractor",
        "main_function": "main",
        "description": "Extract SEO meta tags from files",
        "flags": ["--seo-extract"],
        "args_passthrough": True,
    },
    "schema-validate": {
        "name": "Schema Validator",
        "module": "tools.validation.schema_org_validator",
        "main_function": "main",
        "description": "Validate Schema.org JSON-LD",
        "flags": ["--schema-validate"],
        "args_passthrough": True,
    },
    "master-task": {
        "name": "Master Task Claimer",
        "module": "tools.captain.claim_and_fix_master_task",
        "main_function": "main",
        "description": "Workflow for claiming and fixing tasks",
        "flags": ["--master-task"],
        "args_passthrough": True,
    },
    "test-coordinator": {
        "name": "Integration Test Coordinator",
        "module": "tools.verification.integration_test_coordinator",
        "main_function": "main",
        "description": "Coordinate integration tests",
        "flags": ["--test-coordinator"],
        "args_passthrough": True,
    },
    "session-transition": {
        "name": "Session Transition",
        "module": "tools.captain.session_transition_automator",
        "main_function": "main",
        "description": "Automate session transitions",
        "flags": ["--session-transition"],
        "args_passthrough": True,
    },
    "task-cli": {
        "name": "Task CLI",
        "module": "tools.captain.task_cli",
        "main_function": "main",
        "description": "Task management CLI",
        "flags": ["--task", "-t"],
        "args_passthrough": True,
    },
}


class ToolRegistry:
    """Tool registry for CLI Toolbelt."""

    def __init__(self):
        """Initialize tool registry."""
        self.tools = TOOLS_REGISTRY
        self._flag_map = self._build_flag_map()

    def _build_flag_map(self) -> dict[str, str]:
        """Build mapping from flags to tool IDs."""
        flag_map = {}
        for tool_id, config in self.tools.items():
            for flag in config["flags"]:
                flag_map[flag] = tool_id
        return flag_map

    def get_tool_for_flag(self, flag: str) -> dict[str, Any] | None:
        """
        Get tool configuration by flag.

        Args:
            flag: Tool flag (e.g., "--scan", "-s")

        Returns:
            Tool configuration or None if not found
        """
        tool_id = self._flag_map.get(flag)
        if tool_id:
            return self.tools[tool_id]
        return None

    def get_tool_by_name(self, name: str) -> dict[str, Any] | None:
        """
        Get tool configuration by tool ID.

        Args:
            name: Tool ID (e.g., "scan", "v2-check")

        Returns:
            Tool configuration or None if not found
        """
        return self.tools.get(name)

    def list_tools(self) -> list[dict[str, Any]]:
        """
        List all available tools.

        Returns:
            List of tool configurations
        """
        return [{"id": tool_id, **config} for tool_id, config in self.tools.items()]

    def get_all_flags(self) -> list[str]:
        """Get list of all registered flags."""
        return list(self._flag_map.keys())

"""
CLI Toolbelt Registry - Tool Discovery and Registration
========================================================

Tool registry and discovery system for CLI Toolbelt.
Maps flags to tool modules with metadata.

Architecture: Agent-2 (C-058-2)
Implementation: Agent-1 (C-058-1)
V2 Compliance: ~120 lines

Author: Agent-1 - Code Integration & Testing Specialist
Date: 2025-10-11
License: MIT
"""

from typing import Any

# Tool Registry - Maps tool IDs to configuration
TOOLS_REGISTRY: dict[str, dict[str, Any]] = {
    "scan": {
        "name": "Project Scanner",
        "module": "tools.project_scan",
        "main_function": "main",
        "description": "Scan project structure and generate analysis",
        "flags": ["--scan", "-s"],
        "args_passthrough": True,
    },
    "v2-check": {
        "name": "V2 Compliance Checker",
        "module": "tools.v2_compliance_checker",
        "main_function": "main",
        "description": "Check V2 compliance violations",
        "flags": ["--v2-check", "--v2", "-v"],
        "args_passthrough": True,
    },
    "dashboard": {
        "name": "Compliance Dashboard",
        "module": "tools.compliance_dashboard",
        "main_function": "main",
        "description": "Open compliance tracking dashboard",
        "flags": ["--dashboard", "-d"],
        "args_passthrough": False,
    },
    "complexity": {
        "name": "Complexity Analyzer",
        "module": "tools.unified_analyzer",
        "main_function": "main",
        "description": "Analyze code complexity metrics",
        "flags": ["--complexity", "-c"],
        "args_passthrough": True,
    },
    "refactor": {
        "name": "Refactoring Suggestions",
        "module": "tools.refactoring_suggestion_engine",
        "main_function": "main",
        "description": "Get intelligent refactoring suggestions",
        "flags": ["--refactor", "-r"],
        "args_passthrough": True,
    },
    "duplication": {
        "name": "Duplication Analyzer",
        "module": "tools.duplication_analyzer",
        "main_function": "main",
        "description": "Find duplicate code across project",
        "flags": ["--duplication", "--dup"],
        "args_passthrough": True,
    },
    "technical-debt": {
        "name": "Technical Debt Analyzer",
        "module": "tools.technical_debt_analyzer",
        "main_function": "main",
        "description": "Analyze technical debt markers and consolidation opportunities",
        "flags": ["--technical-debt", "--debt"],
        "args_passthrough": True,
    },
    "coverage": {
        "name": "Coverage Analyzer",
        "module": "tools.coverage_analyzer",
        "main_function": "main",
        "description": "Analyze test coverage gaps and usage patterns",
        "flags": ["--coverage", "--test-coverage"],
        "args_passthrough": True,
    },
    "functionality": {
        "name": "Functionality Verification",
        "module": "tools.functionality_verification",
        "main_function": "main",
        "description": "Verify functionality preservation",
        "flags": ["--functionality", "--verify"],
        "args_passthrough": True,
    },
    "leaderboard": {
        "name": "Autonomous Leaderboard",
        "module": "tools.autonomous_leaderboard",
        "main_function": "main",
        "description": "Show agent performance leaderboard",
        "flags": ["--leaderboard", "-l"],
        "args_passthrough": True,
    },
    "history": {
        "name": "Compliance History",
        "module": "tools.compliance_history_tracker",
        "main_function": "main",
        "description": "Track compliance history over time",
        "flags": ["--history"],
        "args_passthrough": True,
    },
    "soft-onboard": {
        "name": "Soft Onboarding",
        "module": "tools.soft_onboard_cli",
        "main_function": "main",
        "description": "Soft onboard agents (6-step session cleanup protocol)",
        "flags": ["--soft-onboard", "--soft"],
        "args_passthrough": True,
    },
    "test-usage-analyzer": {
        "name": "Test Usage Analyzer",
        "module": "tools.test_usage_analyzer",
        "main_function": "main",
        "description": "Identify unused functionality via test coverage analysis - finds methods only tested but never used in production",
        "flags": ["--test-usage-analyzer", "--test-usage", "--unused-via-tests"],
        "args_passthrough": True,
    },
    "swarm-brain": {
        "name": "Swarm Brain Update",
        "module": "tools.update_swarm_brain",
        "main_function": "main",
        "description": "Update swarm brain with insights/lessons/patterns",
        "flags": ["--swarm-brain", "--brain"],
        "args_passthrough": True,
    },
    "message": {
        "name": "Send Message",
        "module": "src.services.messaging_cli",
        "main_function": "main",
        "description": "Send messages to agents via messaging system",
        "flags": ["--message-cli", "--msg"],
        "args_passthrough": True,
    },
    "pattern-validator": {
        "name": "Architecture Pattern Validator",
        "module": "tools.architecture_review",
        "main_function": "main",
        "description": "Validate architectural patterns (Agent-2's tool)",
        "flags": ["--validate-patterns", "--patterns"],
        "args_passthrough": True,
    },
    "linecount": {
        "name": "Quick Line Count",
        "module": "tools.quick_linecount",
        "main_function": "main",
        "description": "Quick line count for files/directories",
        "flags": ["--linecount", "--lines"],
        "args_passthrough": True,
    },
    "validate-imports": {
        "name": "Import Validator",
        "module": "tools.validate_imports",
        "main_function": "main",
        "description": "Validate import statements and dependencies",
        "flags": ["--validate-imports", "--imports"],
        "args_passthrough": True,
    },
    "get-task": {
        "name": "Get Next Task",
        "module": "src.services.messaging_cli",
        "main_function": "main",
        "description": "Claim next task from centralized task system (Step 1 of workflow)",
        "flags": ["--get-task", "--next-task"],
        "args_passthrough": False,
        "override_args": ["--get-next-task"],
    },
    "list-tasks": {
        "name": "List Tasks",
        "module": "src.services.messaging_cli",
        "main_function": "main",
        "description": "List all available tasks in queue",
        "flags": ["--tasks", "--task-list"],
        "args_passthrough": False,
        "override_args": ["--list-tasks"],
    },
    # QA & Validation Tools (Agent-8)
    "line-count": {
        "name": "Quick Line Counter",
        "module": "tools.quick_linecount",
        "main_function": "main",
        "description": "Quickly count lines in files for V2 compliance",
        "flags": ["--line-count", "--count-lines", "--lc"],
        "args_passthrough": True,
    },
    "ssot-validate": {
        "name": "SSOT Validator",
        "module": "tools.ssot_validator",
        "main_function": "main",
        "description": "Check documentation-code alignment (prevent SSOT violations)",
        "flags": ["--ssot-validate", "--ssot-check"],
        "args_passthrough": True,
    },
    "extract-module": {
        "name": "Module Extractor",
        "module": "tools.module_extractor",
        "main_function": "main",
        "description": "Extract functions/classes into focused modules",
        "flags": ["--extract-module", "--extract"],
        "args_passthrough": True,
    },
    "check-imports": {
        "name": "Import Chain Validator",
        "module": "tools.import_chain_validator",
        "main_function": "main",
        "description": "Validate import chains and find missing modules",
        "flags": ["--check-imports", "--import-check"],
        "args_passthrough": True,
    },
    "task": {
        "name": "Task CLI",
        "module": "tools.task_cli",
        "main_function": "main",
        "description": "Quick task management (get/list/status/complete)",
        "flags": ["--task", "-t"],
        "args_passthrough": True,
    },
    "refactor-analyze": {
        "name": "Refactor Analyzer",
        "module": "tools.unified_validator",
        "main_function": "main",
        "description": "Smart refactoring suggestions based on file analysis",
        "flags": ["--refactor-analyze", "--analyze-refactor"],
        "args_passthrough": True,
    },
    "memory-scan": {
        "name": "Memory Leak Scanner",
        "module": "tools.memory_leak_scanner",
        "main_function": "main",
        "description": "Detect unbounded caches, lists, and memory leaks",
        "flags": ["--memory-scan", "--memleak"],
        "args_passthrough": True,
    },
    "devlog-post": {
        "name": "Devlog Auto-Poster",
        "module": "tools.devlog_poster",
        "main_function": "main",
        "description": "Auto-post devlogs to Discord (10min → 30sec!)",
        "flags": ["--devlog-post", "--post-devlog"],
        "args_passthrough": True,
    },
    "swarm-brain": {
        "name": "Swarm Brain CLI",
        "module": "tools.swarm_brain_cli",
        "main_function": "main",
        "description": "Easy Swarm Brain contributions (10min → 1min!)",
        "flags": ["--swarm-brain", "--brain"],
        "args_passthrough": True,
    },
    "auto-track": {
        "name": "Progress Auto-Tracker",
        "module": "tools.progress_auto_tracker",
        "main_function": "main",
        "description": "Auto-update status.json from git commits",
        "flags": ["--auto-track", "--track-progress"],
        "args_passthrough": True,
    },
    "workspace-clean": {
        "name": "Workspace Auto-Cleaner",
        "module": "tools.workspace_auto_cleaner",
        "main_function": "main",
        "description": "Automated workspace cleanup (15min → 2min!)",
        "flags": ["--workspace-clean", "--clean"],
        "args_passthrough": True,
    },
    "pattern-extract": {
        "name": "Pattern Extractor",
        "module": "tools.extraction_roadmap_generator",
        "main_function": "main",
        "description": "Semi-automated code pattern extraction (30min → 5min!)",
        "flags": ["--pattern-extract", "--extract"],
        "args_passthrough": True,
    },
    "repo-batch": {
        "name": "Repository Analyzer",
        "module": "tools.repository_analyzer",
        "main_function": "main",
        "description": "Unified repository and project analysis (consolidates repo_batch_analyzer and 7 other tools)",
        "flags": ["--repo-batch", "--batch-analyze", "--repository-analyzer"],
        "args_passthrough": True,
    },
    "unified-validator": {
        "name": "Unified Validator",
        "module": "tools.unified_validator",
        "main_function": "main",
        "description": "Consolidated validation tool - SSOT config, imports, refactor status, session transition, tracker status (consolidates 19+ validation tools)",
        "flags": ["--unified-validator", "--validate", "--validator"],
        "args_passthrough": True,
    },
    "unified-analyzer": {
        "name": "Unified Analyzer",
        "module": "tools.unified_analyzer",
        "main_function": "main",
        "description": "Consolidated analysis tool - repository, project structure, file analysis, consolidation detection, overlaps (consolidates multiple analysis tools)",
        "flags": ["--unified-analyzer", "--analyze", "--analyzer"],
        "args_passthrough": True,
    },
    "unified-captain": {
        "name": "Unified Captain Tools",
        "module": "tools.unified_captain",
        "main_function": "main",
        "description": "Consolidated captain operations - inbox, coordination, monitoring, tasks, cleanup (consolidates 23+ captain tools)",
        "flags": ["--unified-captain", "--captain"],
        "args_passthrough": True,
    },
    "unified-verifier": {
        "name": "Unified Verifier",
        "module": "tools.unified_verifier",
        "main_function": "main",
        "description": "Consolidated verification tool - repo, merge, file, cicd, credentials (consolidates 25+ verification tools)",
        "flags": ["--unified-verifier", "--verify"],
        "args_passthrough": True,
    },
    "unified-cleanup": {
        "name": "Unified Cleanup Tools",
        "module": "tools.unified_cleanup",
        "main_function": "main",
        "description": "Consolidated cleanup operations - archive, delete, cleanup, disk (consolidates 15+ cleanup/archive tools)",
        "flags": ["--unified-cleanup", "--cleanup"],
        "args_passthrough": True,
    },
    "unified-agent": {
        "name": "Unified Agent Tools",
        "module": "tools.unified_agent",
        "main_function": "main",
        "description": "Consolidated agent operations - orient, tasks, status, lifecycle, onboard (consolidates 12+ agent tools)",
        "flags": ["--unified-agent", "--agent"],
        "args_passthrough": True,
    },
    "unified-wordpress": {
        "name": "Unified WordPress Tools",
        "module": "tools.unified_wordpress",
        "main_function": "main",
        "description": "Consolidated WordPress operations - deploy, theme, debug, admin (consolidates 16+ WordPress tools)",
        "flags": ["--unified-wordpress", "--wordpress", "--wp"],
        "args_passthrough": True,
    },
    "unified-discord": {
        "name": "Unified Discord Tools",
        "module": "tools.unified_discord",
        "main_function": "main",
        "description": "Consolidated Discord operations - system, test, verify, upload (consolidates 14+ Discord tools)",
        "flags": ["--unified-discord", "--discord"],
        "args_passthrough": True,
    },
    "unified-github": {
        "name": "Unified GitHub Tools",
        "module": "tools.unified_github",
        "main_function": "main",
        "description": "Consolidated GitHub operations - pr, repo, merge, audit (consolidates 28+ GitHub tools)",
        "flags": ["--unified-github", "--github", "--gh"],
        "args_passthrough": True,
    },
    "spreadsheet-github": {
        "name": "Spreadsheet GitHub Adapter",
        "module": "tools.spreadsheet_github_adapter",
        "main_function": "main",
        "description": "Spreadsheet-driven GitHub automation (create_issue, update_file, open_pr) using unified GitHub tools",
        "flags": ["--spreadsheet-github", "--sheet-github", "--spreadsheet"],
        "args_passthrough": True,
    },
    "extraction-roadmap": {
        "name": "Extraction Roadmap Generator",
        "module": "tools.extraction_roadmap_generator",
        "main_function": "main",
        "description": "Auto-generate extraction plans (30min → 5min!)",
        "flags": ["--extraction-roadmap", "--roadmap"],
        "args_passthrough": True,
    },
    "git-verify": {
        "name": "Git Commit Verifier",
        "module": "tools.git_commit_verifier",
        "main_function": "main",
        "description": "Verify claimed work exists in git history",
        "flags": ["--git-verify", "--verify-commits"],
        "args_passthrough": True,
    },
    "test-pyramid": {
        "name": "Test Pyramid Analyzer",
        "module": "tools.test_pyramid_analyzer",
        "main_function": "main",
        "description": "Analyze test distribution vs 60/30/10 target",
        "flags": ["--test-pyramid", "--pyramid"],
        "args_passthrough": True,
    },
    "v2-batch": {
        "name": "V2 Batch Checker",
        "module": "tools.v2_compliance_checker",
        "main_function": "main",
        "description": "Quick V2 compliance check for multiple files (uses modular v2_checker_cli)",
        "flags": ["--v2-batch", "--batch"],
        "args_passthrough": True,
    },
    "coverage-check": {
        "name": "Coverage Validator",
        "module": "tools.coverage_analyzer",
        "main_function": "main",
        "description": "Validate test coverage meets thresholds (uses coverage analyzer)",
        "flags": ["--coverage-check", "--cov"],
        "args_passthrough": True,
    },
    "qa-checklist": {
        "name": "QA Validation Checklist",
        "module": "tools.qa_validation_checklist",
        "main_function": "main",
        "description": "Automated QA validation checklist",
        "flags": ["--qa-checklist", "--qa"],
        "args_passthrough": True,
    },
    # Agent Coordination & Communication Tools (Agent-6)
    # NOTE: agent_status_quick_check.py consolidated into unified_agent_status_monitor.py
    "agent-status": {
        "name": "Unified Agent Status Monitor",
        "module": "tools.communication.agent_status_validator",
        "main_function": "main",
        "description": "Unified agent status monitoring (consolidates 15+ tools including quick check, snapshot, staleness)",
        "flags": ["--agent-status", "--status-check"],
        "args_passthrough": True,
    },
    "extension-test": {
        "name": "Extension Test Runner",
        "module": "tools.extension_test_runner",
        "main_function": "main",
        "description": "VSCode extension testing with coverage",
        "flags": ["--extension-test", "--ext-test"],
        "args_passthrough": True,
    },
    "message-history": {
        "name": "Agent Message History",
        "module": "tools.agent_message_history",
        "main_function": "main",
        "description": "View recent agent message exchanges",
        "flags": ["--message-history", "--msg-history"],
        "args_passthrough": True,
    },
    "verify-complete": {
        "name": "Work Completion Verifier",
        "module": "tools.work_completion_verifier",
        "main_function": "main",
        "description": "Verify work completion before sending messages",
        "flags": ["--verify-complete", "--verify-work"],
        "args_passthrough": True,
    },
    # Architecture & Integration Tools (Agent-2)
    "arch-review": {
        "name": "Architecture Review",
        "module": "tools.architecture_review",
        "main_function": "main",
        "description": "Request/provide expert architecture reviews",
        "flags": ["--arch-review", "--review"],
        "args_passthrough": True,
    },
    # Stage 1 Integration Tools (Agent-2 & Agent-3)
    "analyze-duplicates": {
        "name": "Analyze Repository Duplicates",
        "module": "tools.unified_analyzer",
        "main_function": "main",
        "description": "General-purpose duplicate file analyzer for any repository (consolidated into unified_analyzer)",
        "flags": ["--analyze-duplicates", "--dup-analyze"],
        "args_passthrough": True,
    },
    "analyze-dreamvault": {
        "name": "Analyze DreamVault Duplicates",
        "module": "tools.unified_analyzer",
        "main_function": "main",
        "description": "DreamVault-specific duplicate detection (consolidated into unified_analyzer)",
        "flags": ["--analyze-dreamvault", "--dreamvault-dup"],
        "args_passthrough": True,
    },
    "resolve-duplicates": {
        "name": "Resolve DreamVault Duplicates",
        "module": "tools.resolve_dreamvault_duplicates",
        "main_function": "main",
        "description": "Detailed duplicate resolution analysis and planning (Agent-2's tool)",
        "flags": ["--resolve-duplicates", "--dup-resolve"],
        "args_passthrough": True,
    },
    "review-integration": {
        "name": "Review DreamVault Integration",
        "module": "tools.review_dreamvault_integration",
        "main_function": "main",
        "description": "Comprehensive integration review for merged repos (Agent-2's tool)",
        "flags": ["--review-integration", "--int-review"],
        "args_passthrough": True,
    },
    "execute-cleanup": {
        "name": "Execute DreamVault Cleanup",
        "module": "tools.execute_dreamvault_cleanup",
        "main_function": "main",
        "description": "Execute cleanup operations for DreamVault (Agent-2's tool)",
        "flags": ["--execute-cleanup", "--cleanup"],
        "args_passthrough": True,
    },
    "check-integration": {
        "name": "Integration Validator",
        "module": "tools.communication.integration_validator",
        "main_function": "main",
        "description": "Unified integration validator - checks integration issues, health, and readiness (consolidates check_integration_issues.py + integration_health_checker.py)",
        "flags": ["--check-integration", "--int-check"],
        "args_passthrough": True,
    },
    "merge-duplicates": {
        "name": "Merge Duplicate File Functionality",
        "module": "tools.merge_duplicate_file_functionality",
        "main_function": "main",
        "description": "Compare duplicate files and generate merge suggestions (Agent-3's tool)",
        "flags": ["--merge-duplicates", "--dup-merge"],
        "args_passthrough": True,
    },
    "verify-cicd": {
        "name": "Verify Merged Repo CI/CD",
        "module": "tools.unified_verifier",
        "main_function": "main",
        "description": "Verify CI/CD pipelines for merged repositories via unified verifier (category=cicd, action=merged)",
        "flags": ["--verify-cicd", "--cicd-verify"],
        "args_passthrough": False,
        "override_args": ["--category", "cicd", "--action", "merged"],
    },
    "real-violations": {
        "name": "Real Violation Scanner",
        "module": "tools.real_violation_scanner",
        "main_function": "main",
        "description": "Verify actual V2 violations (intelligent verification)",
        "flags": ["--real-violations", "--real-v2"],
        "args_passthrough": True,
    },
    "pattern-suggest": {
        "name": "Pattern Suggester",
        "module": "tools.refactoring_suggestion_engine",
        "main_function": "main",
        "description": "Suggest consolidation patterns for refactoring",
        "flags": ["--pattern-suggest", "--suggest-pattern"],
        "args_passthrough": True,
    },
    "integration-validate": {
        "name": "Integration Validator",
        "module": "tools.communication.integration_validator",
        "main_function": "main",
        "description": "Comprehensive system integration validation (C-048-5)",
        "flags": ["--integration-validate", "--int-val"],
        "args_passthrough": False,
    },
    # MASTERPIECE TOOL - Swarm Autonomous Orchestrator (Agent-8)
    "orchestrate": {
        "name": "Swarm Autonomous Orchestrator",
        "module": "tools.swarm_orchestrator",
        "main_function": "run_orchestrator",
        "description": "The Gas Station - Autonomous swarm coordination and gas delivery",
        "flags": ["--orchestrate", "--gas-station", "--swarm"],
        "args_passthrough": True,
    },
    # MASTERPIECE TOOL - Mission Control (Agent-2)
    "mission-control": {
        "name": "Mission Control - Autonomous Mission Generator",
        "module": "tools.mission_control",
        "main_function": "main",
        "description": "THE masterpiece - Runs all 5 workflow steps, generates conflict-free mission brief",
        "flags": ["--mission-control", "--mission", "--mc"],
        "args_passthrough": True,
    },
    # Agent & Captain Tools (Agent-6 Organization)
    "agent-orient": {
        "name": "Agent Orientation",
        "module": "tools.agent_orient",
        "main_function": "main",
        "description": "Agent orientation and onboarding",
        "flags": ["--agent-orient", "--orient"],
        "args_passthrough": True,
    },
    "agent-task-finder": {
        "name": "Agent Task Finder",
        "module": "tools.agent_task_finder",
        "main_function": "main",
        "description": "Find tasks assigned to agents",
        "flags": ["--agent-task-finder", "--find-tasks"],
        "args_passthrough": True,
    },
    "captain-find-idle": {
        "name": "Find Idle Agents",
        "module": "tools.captain_find_idle_agents",
        "main_function": "main",
        "description": "Find agents that are idle",
        "flags": ["--find-idle", "--idle-agents"],
        "args_passthrough": True,
    },
    "captain-next-task": {
        "name": "Captain Next Task Picker",
        "module": "tools.captain_next_task_picker",
        "main_function": "main",
        "description": "Pick next task for agents",
        "flags": ["--next-task", "--pick-task"],
        "args_passthrough": True,
    },
    "markov-optimize": {
        "name": "Markov Task Optimizer (Swarm Integration)",
        "module": "tools.markov_swarm_integration",
        "main_function": "main",
        "description": "Get optimal task assignments using Markov Chain analysis (integrated with swarm)",
        "flags": ["--markov-optimize", "--markov", "--optimize-task"],
        "args_passthrough": True,
    },
    "system-inventory": {
        "name": "Swarm System Inventory",
        "module": "tools.swarm_system_inventory",
        "main_function": "main",
        "description": "Complete catalog of all systems, tools, integrations, and connections",
        "flags": ["--system-inventory", "--inventory", "--what-do-we-have"],
        "args_passthrough": True,
    },
    "github-pr-debug": {
        "name": "GitHub PR Debugger",
        "module": "tools.github_pr_debugger",
        "main_function": "main",
        "description": "Diagnose and fix GitHub PR creation issues",
        "flags": ["--github-pr-debug", "--pr-debug", "--debug-pr"],
        "args_passthrough": True,
    },
    "fix-github-prs": {
        "name": "Fix GitHub PR Issues",
        "module": "tools.fix_github_prs",
        "main_function": "main",
        "description": "One-command fix for GitHub PR issues",
        "flags": ["--fix-github-prs", "--fix-prs"],
        "args_passthrough": False,
    },
    # Consolidation Tools (Agent-6 Organization)
    "repo-overlap": {
        "name": "Repo Overlap Analyzer",
        "module": "tools.repository_analyzer",
        "main_function": "main",
        "description": "Analyze repository overlaps for consolidation (consolidated into repository_analyzer)",
        "flags": ["--repo-overlap", "--overlap"],
        "args_passthrough": True,
    },
    "consolidation-exec": {
        "name": "Consolidation Executor",
        "module": "tools.consolidation_executor",
        "main_function": "main",
        "description": "Execute repository consolidations",
        "flags": ["--consolidation-exec", "--consolidate"],
    },
    "consolidation-status": {
        "name": "Consolidation Status Tracker",
        "module": "tools.consolidation_progress_tracker",
        "main_function": "main",
        "description": "Track GitHub consolidation progress and identify next opportunities",
        "flags": ["--consolidation-status", "--consolidation-track"],
        "args_passthrough": True,
    },
    "verify-phase1": {
        "name": "Verify Phase 1 Repos",
        "module": "tools.verify_phase1_repos",
        "main_function": "main",
        "description": "Verify Phase 1 consolidation repos",
        "flags": ["--verify-phase1", "--phase1-verify"],
        "args_passthrough": True,
    },
    # Discord Tools (Agent-6 Organization)
    "discord-start": {
        "name": "Start Discord System",
        "module": "tools.start_discord_system",
        "main_function": "main",
        "description": "Start Discord bot system",
        "flags": ["--discord-start", "--start-discord"],
        "args_passthrough": True,
    },
    "discord-verify": {
        "name": "Verify Discord Running",
        "module": "tools.check_service_status",
        "main_function": "main",
        "description": "Verify Discord bot is running",
        "flags": ["--discord-verify", "--verify-discord"],
        "args_passthrough": True,
    },
    # Queue Tools (Agent-6 Organization)
    "queue-diagnose": {
        "name": "Diagnose Queue",
        "module": "tools.diagnose_message_queue",
        "main_function": "main",
        "description": "Diagnose message queue issues",
        "flags": ["--queue-diagnose", "--diagnose-queue"],
        "args_passthrough": True,
    },
    "queue-status": {
        "name": "Messaging Infrastructure Validator",
        "module": "tools.communication.messaging_infrastructure_validator",
        "main_function": "main",
        "description": "Unified messaging infrastructure validator - checks queue status, persistence, and configuration (consolidates check_queue_status.py)",
        "flags": ["--queue-status", "--q-status"],
        "args_passthrough": True,
    },
    "fix-stuck": {
        "name": "Fix Stuck Message",
        "module": "tools.reset_stuck_messages",
        "main_function": "main",
        "description": "Fix stuck messages in queue",
        "flags": ["--fix-stuck", "--unstuck"],
        "args_passthrough": True,
    },
    # Workspace Tools (Agent-6 Organization)
    "workspace-health": {
        "name": "Workspace Health Monitor",
        "module": "tools.workspace_health_monitor",
        "main_function": "main",
        "description": "Check workspace health (consolidates workspace_health_checker.py)",
        "flags": ["--workspace-health", "--health"],
        "args_passthrough": True,
    },
    # Git Tools (Agent-6 Organization)
    "git-work-verify": {
        "name": "Git Work Verifier",
        "module": "tools.git_work_verifier",
        "main_function": "main",
        "description": "Verify work in git history",
        "flags": ["--git-work-verify", "--verify-work"],
        "args_passthrough": True,
    },
    "test-health": {
        "name": "Test Health Monitor",
        "module": "tools.unified_verifier",
        "main_function": "main",
        "description": "Monitor test suite health via unified verifier (category=file, action=comprehensive)",
        "flags": ["--test-health", "--health"],
        "args_passthrough": False,
        "override_args": ["--category", "file", "--action", "comprehensive"],
    },
    "infra-health": {
        "name": "Infrastructure Health Monitor",
        "module": "src.infrastructure.infrastructure_health_monitor",
        "main_function": "main",
        "description": "Monitor infrastructure health for automation reliability",
        "flags": ["--infra-health", "--infra"],
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

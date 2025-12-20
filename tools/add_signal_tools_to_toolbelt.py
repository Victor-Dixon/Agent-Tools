#!/usr/bin/env python3
"""
Add Signal Tools to Toolbelt Registry
=====================================

Adds high-priority Signal tools to the toolbelt registry.

Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-11-24
Priority: HIGH
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


# High-priority Signal tools to add to toolbelt
PRIORITY_TOOLS = [
    # Agent & Captain Tools
    {
        "id": "agent-orient",
        "name": "Agent Orientation",
        "module": "tools.agent_orient",
        "main_function": "main",
        "description": "Agent orientation and onboarding",
        "flags": ["--agent-orient", "--orient"],
        "args_passthrough": True,
    },
    {
        "id": "agent-task-finder",
        "name": "Agent Task Finder",
        "module": "tools.agent_task_finder",
        "main_function": "main",
        "description": "Find tasks assigned to agents",
        "flags": ["--agent-task-finder", "--find-tasks"],
        "args_passthrough": True,
    },
    {
        "id": "captain-status-check",
        "name": "Captain Status Check",
        "module": "tools.captain_check_agent_status",
        "main_function": "main",
        "description": "Captain check agent status",
        "flags": ["--captain-status", "--cap-status"],
        "args_passthrough": True,
    },
    {
        "id": "captain-find-idle",
        "name": "Find Idle Agents",
        "module": "tools.captain_find_idle_agents",
        "main_function": "main",
        "description": "Find agents that are idle",
        "flags": ["--find-idle", "--idle-agents"],
        "args_passthrough": True,
    },
    {
        "id": "captain-next-task",
        "name": "Captain Next Task Picker",
        "module": "tools.captain_next_task_picker",
        "main_function": "main",
        "description": "Pick next task for agents",
        "flags": ["--next-task", "--pick-task"],
        "args_passthrough": True,
    },
    {
        "id": "captain-roi-calc",
        "name": "Captain ROI Calculator",
        "module": "tools.captain_roi_quick_calc",
        "main_function": "main",
        "description": "Quick ROI calculation for tasks",
        "flags": ["--roi-calc", "--roi"],
        "args_passthrough": True,
    },
    # Consolidation Tools
    {
        "id": "repo-overlap",
        "name": "Repo Overlap Analyzer",
        "module": "tools.repo_overlap_analyzer",
        "main_function": "main",
        "description": "Analyze repository overlaps for consolidation",
        "flags": ["--repo-overlap", "--overlap"],
        "args_passthrough": True,
    },
    {
        "id": "consolidation-executor",
        "name": "Consolidation Executor",
        "module": "tools.consolidation_executor",
        "main_function": "main",
        "description": "Execute repository consolidations",
        "flags": ["--consolidation-exec", "--consolidate"],
        "args_passthrough": True,
    },
    {
        "id": "verify-phase1",
        "name": "Verify Phase 1 Repos",
        "module": "tools.verify_phase1_repos",
        "main_function": "main",
        "description": "Verify Phase 1 consolidation repos",
        "flags": ["--verify-phase1", "--phase1-verify"],
        "args_passthrough": True,
    },
    # Discord Tools
    {
        "id": "discord-start",
        "name": "Start Discord System",
        "module": "tools.start_discord_system",
        "main_function": "main",
        "description": "Start Discord bot system",
        "flags": ["--discord-start", "--start-discord"],
        "args_passthrough": True,
    },
    {
        "id": "discord-status",
        "name": "Discord Status Dashboard",
        "module": "tools.discord_status_dashboard",
        "main_function": "main",
        "description": "Discord status dashboard",
        "flags": ["--discord-status", "--discord-dash"],
        "args_passthrough": True,
    },
    {
        "id": "discord-verify",
        "name": "Verify Discord Running",
        "module": "tools.verify_discord_running",
        "main_function": "main",
        "description": "Verify Discord bot is running",
        "flags": ["--discord-verify", "--verify-discord"],
        "args_passthrough": True,
    },
    # Queue Tools - start_message_queue_processor removed (consolidated to unified_monitor.py)
    {
        "id": "queue-diagnose",
        "name": "Diagnose Queue",
        "module": "tools.diagnose_queue",
        "main_function": "main",
        "description": "Diagnose message queue issues",
        "flags": ["--queue-diagnose", "--diagnose-queue"],
        "args_passthrough": True,
    },
    {
        "id": "queue-status",
        "name": "Queue Status",
        "module": "tools.check_queue_status",
        "main_function": "main",
        "description": "Check message queue status",
        "flags": ["--queue-status", "--q-status"],
        "args_passthrough": True,
    },
    {
        "id": "fix-stuck-message",
        "name": "Fix Stuck Message",
        "module": "tools.fix_stuck_message",
        "main_function": "main",
        "description": "Fix stuck messages in queue",
        "flags": ["--fix-stuck", "--unstuck"],
        "args_passthrough": True,
    },
    # Workspace Tools
    {
        "id": "workspace-health",
        "name": "Workspace Health Checker",
        "module": "tools.workspace_health_checker",
        "main_function": "main",
        "description": "Check workspace health",
        "flags": ["--workspace-health", "--health"],
        "args_passthrough": True,
    },
    {
        "id": "workspace-monitor",
        "name": "Workspace Health Monitor",
        "module": "tools.workspace_health_monitor",
        "main_function": "main",
        "description": "Monitor workspace health",
        "flags": ["--workspace-monitor", "--monitor"],
        "args_passthrough": True,
    },
    # Git Tools
    {
        "id": "git-work-verify",
        "name": "Git Work Verifier",
        "module": "tools.git_work_verifier",
        "main_function": "main",
        "description": "Verify work in git history",
        "flags": ["--git-work-verify", "--verify-work"],
        "args_passthrough": True,
    },
    {
        "id": "github-create-repo",
        "name": "GitHub Create and Push Repo",
        "module": "tools.github_create_and_push_repo",
        "main_function": "main",
        "description": "Create and push GitHub repository",
        "flags": ["--github-create", "--create-repo"],
        "args_passthrough": True,
    },
    # Analysis Tools
    {
        "id": "arch-pattern-analyzer",
        "name": "Architectural Pattern Analyzer",
        "module": "tools.architectural_pattern_analyzer",
        "main_function": "main",
        "description": "Analyze architectural patterns",
        "flags": ["--arch-pattern", "--arch-analyze"],
        "args_passthrough": True,
    },
    {
        "id": "integration-pattern",
        "name": "Integration Pattern Analyzer",
        "module": "tools.integration_pattern_analyzer",
        "main_function": "main",
        "description": "Analyze integration patterns",
        "flags": ["--integration-pattern", "--int-pattern"],
        "args_passthrough": True,
    },
    {
        "id": "comprehensive-analyzer",
        "name": "Comprehensive Project Analyzer",
        "module": "tools.comprehensive_project_analyzer",
        "main_function": "main",
        "description": "Comprehensive project analysis",
        "flags": ["--comprehensive-analyze", "--full-analyze"],
        "args_passthrough": True,
    },
    # Refactoring Tools
    {
        "id": "refactor-cli",
        "name": "Refactoring CLI",
        "module": "tools.refactoring_cli",
        "main_function": "main",
        "description": "Refactoring command-line interface",
        "flags": ["--refactor-cli", "--refactor"],
        "args_passthrough": True,
    },
    {
        "id": "file-size-violations",
        "name": "Find File Size Violations",
        "module": "tools.find_file_size_violations",
        "main_function": "main",
        "description": "Find files violating size limits",
        "flags": ["--file-size-violations", "--size-violations"],
        "args_passthrough": True,
    },
    # Infrastructure Tools
    {
        "id": "infra-automation",
        "name": "Infrastructure Automation Suite",
        "module": "tools.infrastructure_automation_suite",
        "main_function": "main",
        "description": "Infrastructure automation suite",
        "flags": ["--infra-automation", "--infra-auto"],
        "args_passthrough": True,
    },
    {
        "id": "infra-health-dashboard",
        "name": "Infrastructure Health Dashboard",
        "module": "tools.infrastructure_health_dashboard",
        "main_function": "main",
        "description": "Infrastructure health dashboard",
        "flags": ["--infra-health", "--infra-dash"],
        "args_passthrough": True,
    },
]


def add_tools_to_registry(registry_path: Path, new_tools: List[Dict[str, Any]]) -> None:
    """Add new tools to toolbelt registry."""
    # Read current registry
    with open(registry_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find TOOLS_REGISTRY dict
    import ast
    tree = ast.parse(content)
    
    # Extract existing registry
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "TOOLS_REGISTRY":
                    # We'll need to manually add tools
                    break

    # Add new tools to registry file
    # Find the closing brace of TOOLS_REGISTRY
    lines = content.split('\n')
    new_lines = []
    in_registry = False
    registry_closed = False
    
    for i, line in enumerate(lines):
        if 'TOOLS_REGISTRY: dict[str, dict[str, Any]] = {' in line:
            in_registry = True
            new_lines.append(line)
        elif in_registry and not registry_closed:
            # Check if we're at the closing brace
            if line.strip() == '}':
                # Add new tools before closing
                for tool in new_tools:
                    tool_id = tool['id']
                    tool_config = {
                        "name": tool['name'],
                        "module": tool['module'],
                        "main_function": tool['main_function'],
                        "description": tool['description'],
                        "flags": tool['flags'],
                        "args_passthrough": tool.get('args_passthrough', True),
                    }
                    # Format as Python dict entry
                    new_lines.append(f'    "{tool_id}": {{')
                    new_lines.append(f'        "name": "{tool_config["name"]}",')
                    new_lines.append(f'        "module": "{tool_config["module"]}",')
                    new_lines.append(f'        "main_function": "{tool_config["main_function"]}",')
                    new_lines.append(f'        "description": "{tool_config["description"]}",')
                    new_lines.append(f'        "flags": {tool_config["flags"]},')
                    new_lines.append(f'        "args_passthrough": {tool_config["args_passthrough"]},')
                    new_lines.append('    },')
                registry_closed = True
                new_lines.append(line)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    # Write updated registry
    with open(registry_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))


def main():
    """Main entry point."""
    registry_path = Path(__file__).parent / "toolbelt_registry.py"
    
    print(f"📝 Adding {len(PRIORITY_TOOLS)} priority tools to toolbelt registry...")
    print(f"📁 Registry: {registry_path}")
    
    # For now, create a separate file with new tools to add
    # Manual integration is safer
    additions_file = Path(__file__).parent / "TOOLBELT_ADDITIONS.md"
    with open(additions_file, 'w', encoding='utf-8') as f:
        f.write("# Toolbelt Registry Additions\n\n")
        f.write("## Priority Signal Tools to Add\n\n")
        for tool in PRIORITY_TOOLS:
            f.write(f"### {tool['name']}\n\n")
            f.write(f"**ID**: `{tool['id']}`\n\n")
            f.write(f"**Module**: `{tool['module']}`\n\n")
            f.write(f"**Flags**: {', '.join(tool['flags'])}\n\n")
            f.write(f"**Description**: {tool['description']}\n\n")
            f.write("```python\n")
            f.write(f'"{tool["id"]}": {{\n')
            f.write(f'    "name": "{tool["name"]}",\n')
            f.write(f'    "module": "{tool["module"]}",\n')
            f.write(f'    "main_function": "{tool["main_function"]}",\n')
            f.write(f'    "description": "{tool["description"]}",\n')
            f.write(f'    "flags": {tool["flags"]},\n')
            f.write(f'    "args_passthrough": {tool.get("args_passthrough", True)},\n')
            f.write('},\n')
            f.write("```\n\n")
    
    print(f"✅ Created additions file: {additions_file}")
    print(f"📋 {len(PRIORITY_TOOLS)} tools ready to add to registry")


if __name__ == "__main__":
    main()



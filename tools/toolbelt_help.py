"""
CLI Toolbelt Help System - Auto-Generated Help
==============================================

Generates formatted help text from tool registry.

Architecture: Agent-2 (C-058-2)
Implementation: Agent-1 (C-058-1)
V2 Compliance: ~100 lines

Author: Agent-1 - Code Integration & Testing Specialist
Date: 2025-10-11
License: MIT
"""

from typing import Any


class HelpGenerator:
    """Help system generator for CLI Toolbelt."""

    def __init__(self, registry):
        """
        Initialize help generator.

        Args:
            registry: ToolRegistry instance
        """
        self.registry = registry

    def generate_help(self) -> str:
        """
        Generate formatted help text.

        Returns:
            Formatted help text
        """
        help_lines = []

        # Header
        help_lines.append("🛠️  CLI Toolbelt - Unified Tool Access")
        help_lines.append("=" * 50)
        help_lines.append("")
        help_lines.append("Usage: python -m tools.toolbelt <TOOL_FLAG> [TOOL_ARGS...]")
        help_lines.append("")

        # Available tools
        help_lines.append("Available Tools:")
        help_lines.append("-" * 50)
        help_lines.append("")

        tools = self.registry.list_tools()
        for tool in tools:
            # Tool name and flags
            flags_str = ", ".join(tool["flags"])
            help_lines.append(f"📊 {tool['name']} ({flags_str})")
            help_lines.append(f"   {tool['description']}")
            help_lines.append(f"   Example: python -m tools.toolbelt {tool['flags'][0]}")
            help_lines.append("")

        # General options
        help_lines.append("General Options:")
        help_lines.append("-" * 50)
        help_lines.append("  --help          Show this help message")
        help_lines.append("  --version       Show toolbelt version")
        help_lines.append("  --list          List all available tools")
        help_lines.append("")

        # Tool-specific help
        help_lines.append("For tool-specific help:")
        help_lines.append("  python -m tools.toolbelt <TOOL_FLAG> --help")
        help_lines.append("")

        # Examples
        help_lines.append("Examples:")
        help_lines.append("-" * 50)
        help_lines.append("# Run project scan")
        help_lines.append("python -m tools.toolbelt --scan")
        help_lines.append("")
        help_lines.append("# Check V2 compliance with suggestions")
        help_lines.append("python -m tools.toolbelt --v2-check --suggest")
        help_lines.append("")
        help_lines.append("# Show leaderboard")
        help_lines.append("python -m tools.toolbelt --leaderboard --top 10")
        help_lines.append("")

        return "\n".join(help_lines)

    def show_tool_help(self, tool_config: dict[str, Any]) -> str:
        """
        Show help for specific tool.

        Args:
            tool_config: Tool configuration

        Returns:
            Tool-specific help text
        """
        help_lines = []

        help_lines.append(f"🛠️  {tool_config['name']}")
        help_lines.append("=" * 50)
        help_lines.append("")
        help_lines.append(f"Description: {tool_config['description']}")
        help_lines.append("")
        help_lines.append(f"Flags: {', '.join(tool_config['flags'])}")
        help_lines.append("")
        help_lines.append(f"Usage: python -m tools.toolbelt {tool_config['flags'][0]} [OPTIONS]")
        help_lines.append("")
        help_lines.append("For detailed tool options, run:")
        help_lines.append(f"  python -m {tool_config['module']} --help")
        help_lines.append("")

        return "\n".join(help_lines)

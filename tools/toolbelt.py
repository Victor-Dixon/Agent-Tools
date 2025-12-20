"""
CLI Toolbelt - Unified Tool Launcher
=====================================

Main entry point for unified CLI tool access.
Provides flag-based tool selection and execution.

Architecture: Agent-2 (C-058-2)
Implementation: Agent-1 (C-058-1)
V2 Compliance: ~80 lines

Usage:
    python -m tools.toolbelt --scan
    python -m tools.toolbelt --v2-check --fail-on-major
    python -m tools.toolbelt --help

Author: Agent-1 - Code Integration & Testing Specialist
Date: 2025-10-11
License: MIT
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.toolbelt_help import HelpGenerator
from tools.toolbelt_registry import ToolRegistry
from tools.toolbelt_runner import ToolRunner

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Version
VERSION = "1.0.0"


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for toolbelt."""
    parser = argparse.ArgumentParser(
        description="CLI Toolbelt - Unified Tool Access",
        add_help=False,  # Custom help handling
    )

    # General options
    parser.add_argument("--help", action="store_true", help="Show help message")
    parser.add_argument("--version", action="store_true", help="Show version")
    parser.add_argument("--list", action="store_true", help="List all tools")

    # Tool flags (these will be detected dynamically)
    # We use parse_known_args() to handle tool-specific flags

    return parser


def main() -> int:
    """Main CLI entry point."""
    try:
        # Initialize components
        registry = ToolRegistry()
        runner = ToolRunner()
        help_gen = HelpGenerator(registry)

        # Parse arguments (known and unknown)
        parser = create_parser()
        args, remaining = parser.parse_known_args()

        # Handle version
        if args.version:
            print(f"CLI Toolbelt v{VERSION}")
            return 0

        # Handle list
        if args.list:
            print("Available tools:")
            for tool in registry.list_tools():
                print(f"  {', '.join(tool['flags'])} - {tool['name']}")
            return 0

        # Detect tool flag from remaining args
        tool_config = None
        tool_flag = None

        for arg in sys.argv[1:]:
            if arg.startswith("-"):
                tool_config = registry.get_tool_for_flag(arg)
                if tool_config:
                    tool_flag = arg
                    break

        # Handle help or no tool flag
        if args.help or not tool_config:
            print(help_gen.generate_help())
            return 0

        # Remove tool flag from remaining args
        if tool_flag in remaining:
            remaining.remove(tool_flag)

        # Execute tool
        exit_code = runner.execute_tool(tool_config, remaining)
        return exit_code

    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
        return 130

    except Exception as e:
        logger.error(f"Toolbelt error: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

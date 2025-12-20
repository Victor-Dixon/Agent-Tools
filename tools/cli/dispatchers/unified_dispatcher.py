#!/usr/bin/env python3
"""
Unified CLI Dispatcher - Tools CLI Framework
============================================

Unified dispatcher for all tool CLI commands.
Consolidates 391 tools CLI files into single entry point.

<!-- SSOT Domain: infrastructure -->

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-04
V2 Compliant: Yes (<300 lines)
"""

import argparse
import importlib
import sys
from pathlib import Path
from typing import Dict, Optional, List

PROJECT_ROOT = Path(__file__).parent.parent.parent


class UnifiedCLIDispatcher:
    """Unified dispatcher for tool CLI commands."""
    
    def __init__(self):
        """Initialize dispatcher with command registry."""
        self.commands: Dict[str, Dict] = {}
        self._load_command_registry()
    
    def _load_command_registry(self):
        """Load command registry from configuration."""
        try:
            from tools.cli.commands.registry import COMMAND_REGISTRY
            self.commands = COMMAND_REGISTRY.copy()
        except ImportError:
            # Fallback to empty registry if not available
            self.commands = {}
    
    def register_command(self, name: str, module: str, function: str = "main"):
        """Register a command."""
        self.commands[name] = {"module": module, "function": function}
    
    def dispatch(self, command: str, args: List[str]) -> int:
        """Dispatch command to appropriate handler."""
        if command not in self.commands:
            print(f"❌ Unknown command: {command}")
            print(f"\nAvailable commands ({len(self.commands)}):")
            # Group by category
            categories = {}
            for cmd_name, cmd_info in self.commands.items():
                cat = cmd_info.get("category", "general")
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(cmd_name)
            
            for cat in sorted(categories.keys()):
                print(f"\n  {cat.upper()} ({len(categories[cat])}):")
                for cmd in sorted(categories[cat])[:10]:  # Show first 10 per category
                    print(f"    - {cmd}")
                if len(categories[cat]) > 10:
                    print(f"    ... and {len(categories[cat]) - 10} more")
            return 1
        
        try:
            cmd_config = self.commands[command]
            module = importlib.import_module(cmd_config["module"])
            handler = getattr(module, cmd_config["function"])
            
            # Most tools expect sys.argv, so we need to reconstruct it
            # Save original argv
            original_argv = sys.argv[:]
            try:
                # Reconstruct argv: [script_name, command, ...args]
                sys.argv = [sys.argv[0], command] + args
                # Execute command handler
                if callable(handler):
                    result = handler()
                    return result if isinstance(result, int) else 0
                else:
                    return 1
            finally:
                # Restore original argv
                sys.argv = original_argv
        except ImportError as e:
            print(f"❌ Error importing module for '{command}': {e}")
            return 1
        except AttributeError as e:
            print(f"❌ Error: Function '{cmd_config['function']}' not found in module: {e}")
            return 1
        except Exception as e:
            print(f"❌ Error executing command '{command}': {e}")
            import traceback
            traceback.print_exc()
            return 1


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Unified CLI Dispatcher - Tools Framework",
        add_help=True
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        help="Command to execute"
    )
    
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Command arguments"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available commands"
    )
    
    return parser


def main() -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    dispatcher = UnifiedCLIDispatcher()
    
    if args.list:
        print(f"Available commands ({len(dispatcher.commands)}):\n")
        # Group by category
        categories = {}
        for cmd_name, cmd_info in dispatcher.commands.items():
            cat = cmd_info.get("category", "general")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(cmd_name)
        
        for cat in sorted(categories.keys()):
            print(f"{cat.upper()} ({len(categories[cat])}):")
            for cmd in sorted(categories[cat]):
                desc = dispatcher.commands[cmd].get("description", "")
                if desc:
                    print(f"  {cmd:50} - {desc[:60]}")
                else:
                    print(f"  {cmd}")
            print()
        return 0
    
    if not args.command:
        parser.print_help()
        print(f"\nUse --list to see all {len(dispatcher.commands)} available commands.")
        return 1
    
    return dispatcher.dispatch(args.command, args.args)


if __name__ == "__main__":
    sys.exit(main())

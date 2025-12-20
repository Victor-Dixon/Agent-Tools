"""
CLI Toolbelt Runner - Tool Execution Engine
============================================

Handles dynamic tool loading and execution with argument passthrough.

Architecture: Agent-2 (C-058-2)
Implementation: Agent-1 (C-058-1)
V2 Compliance: ~100 lines

Author: Agent-1 - Code Integration & Testing Specialist
Date: 2025-10-11
License: MIT
"""

import importlib
import logging
import sys
from typing import Any

logger = logging.getLogger(__name__)


class ToolRunner:
    """Tool execution engine for CLI Toolbelt."""

    def __init__(self):
        """Initialize tool runner."""
        self.logger = logger

    def execute_tool(self, tool_config: dict[str, Any], args: list[str]) -> int:
        """
        Execute tool with given arguments.

        Args:
            tool_config: Tool configuration from registry
            args: Command-line arguments to pass to tool

        Returns:
            Exit code from tool execution
        """
        try:
            # Import tool module dynamically
            module_name = tool_config["module"]
            self.logger.info(f"Loading tool module: {module_name}")

            module = importlib.import_module(module_name)

            # Get main function
            main_function_name = tool_config.get("main_function", "main")
            if not hasattr(module, main_function_name):
                self.logger.error(f"Tool {module_name} has no {main_function_name}() function")
                return 1

            main_func = getattr(module, main_function_name)

            # Setup argument passthrough if enabled
            args_passthrough = tool_config.get("args_passthrough", True)
            original_argv = None

            if args_passthrough and args:
                original_argv = sys.argv
                sys.argv = [module_name] + args
                self.logger.info(f"Passing {len(args)} arguments to tool")

            # Execute tool
            self.logger.info(f"Executing {tool_config['name']}...")
            exit_code = main_func()

            # Handle None return as success
            if exit_code is None:
                exit_code = 0

            self.logger.info(f"Tool completed with exit code {exit_code}")

            # Restore original argv
            if original_argv is not None:
                sys.argv = original_argv

            return exit_code

        except ImportError as e:
            self.logger.error(f"Failed to import tool module {tool_config['module']}: {e}")
            print(f"❌ Error: Tool '{tool_config['name']}' not found or cannot be imported")
            return 1

        except Exception as e:
            self.logger.error(f"Error executing {tool_config['name']}: {e}")
            print(f"❌ Error executing {tool_config['name']}: {e}")
            return 1

        finally:
            # Ensure argv is restored even on exception
            if original_argv is not None and sys.argv != original_argv:
                sys.argv = original_argv

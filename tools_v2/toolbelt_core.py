"""
Toolbelt Core Orchestrator
===========================

Thin orchestrator for Agent Toolbelt operations (resolve→validate→execute→record).

V2 Compliance: <240 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import logging
import time
from typing import Any

from .adapters.base_adapter import ToolResult
from .adapters.error_types import (
    ToolExecutionError,
    ToolNotFoundError,
    ToolValidationError,
    format_toolbelt_error,
)
from .tool_registry import get_tool_registry

logger = logging.getLogger(__name__)


class ToolbeltCore:
    """Core orchestrator for agent toolbelt operations."""

    def __init__(self):
        """Initialize toolbelt core."""
        self.registry = get_tool_registry()
        self.execution_history: list[dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)

    def run(
        self, tool_name: str, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """
        Run a tool with given parameters (resolve→validate→execute→record).

        Args:
            tool_name: Name of tool to run (e.g., "vector.context")
            params: Tool parameters
            context: Optional execution context

        Returns:
            Tool execution result
        """
        start_time = time.time()

        try:
            # Step 1: Resolve tool
            self.logger.info(f"Resolving tool: {tool_name}")
            adapter_class = self.registry.resolve(tool_name)
            adapter = adapter_class()

            # Step 2: Validate parameters
            self.logger.debug(f"Validating parameters for {tool_name}")
            is_valid, invalid_params = adapter.validate(params)
            if not is_valid:
                raise ToolValidationError(
                    f"Invalid parameters for {tool_name}",
                    tool_name=tool_name,
                    invalid_params=invalid_params,
                )

            # Step 3: Execute tool
            self.logger.info(f"Executing tool: {tool_name}")
            result = adapter.execute(params, context)
            result.execution_time = time.time() - start_time

            # Step 4: Record execution
            self._record_execution(tool_name, params, result)

            self.logger.info(f"Tool {tool_name} completed in {result.execution_time:.2f}s")
            return result

        except (ToolNotFoundError, ToolValidationError, ToolExecutionError) as e:
            # Known toolbelt errors
            error_msg = format_toolbelt_error(e)
            self.logger.error(error_msg)

            result = ToolResult(
                success=False,
                output=None,
                exit_code=1,
                error_message=str(e),
                execution_time=time.time() - start_time,
            )
            self._record_execution(tool_name, params, result)
            return result

        except Exception as e:
            # Unexpected errors
            self.logger.exception(f"Unexpected error running {tool_name}: {e}")

            result = ToolResult(
                success=False,
                output=None,
                exit_code=1,
                error_message=f"Unexpected error: {e}",
                execution_time=time.time() - start_time,
            )
            self._record_execution(tool_name, params, result)
            return result

    def list_tools(self) -> list[str]:
        """
        List all available tools.

        Returns:
            Sorted list of tool names
        """
        return self.registry.list_tools()

    def list_categories(self) -> dict[str, list[str]]:
        """
        List tools grouped by category.

        Returns:
            Dictionary mapping category to tool names
        """
        return self.registry.list_by_category()

    def get_tool_help(self, tool_name: str) -> str:
        """
        Get help text for a specific tool.

        Args:
            tool_name: Name of tool

        Returns:
            Help text

        Raises:
            ToolNotFoundError: If tool not found
        """
        adapter_class = self.registry.resolve(tool_name)
        adapter = adapter_class()
        return adapter.get_help()

    def get_execution_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get recent tool execution history.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of execution records
        """
        return self.execution_history[-limit:]

    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history.clear()
        self.logger.info("Execution history cleared")

    def _record_execution(self, tool_name: str, params: dict[str, Any], result: ToolResult) -> None:
        """
        Record tool execution for metrics and debugging.

        Args:
            tool_name: Name of tool executed
            params: Parameters used
            result: Execution result
        """
        record = {
            "tool_name": tool_name,
            "timestamp": time.time(),
            "success": result.success,
            "execution_time": result.execution_time,
            "exit_code": result.exit_code,
            "params_count": len(params),
            "had_error": result.error_message is not None,
        }

        self.execution_history.append(record)

        # Keep history limited to last 100 executions
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]


# Singleton instance
_core_instance: ToolbeltCore | None = None


def get_toolbelt_core() -> ToolbeltCore:
    """
    Get singleton toolbelt core instance.

    Returns:
        Toolbelt core instance
    """
    global _core_instance
    if _core_instance is None:
        _core_instance = ToolbeltCore()
    return _core_instance

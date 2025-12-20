"""
Base Tool Adapter
=================

Abstract base class for all tool adapters in the Agent Toolbelt.

V2 Compliance: <120 lines
Author: Agent-7 - Repository Cloning Specialist
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class ToolSpec:
    """Specification for a tool."""

    name: str
    version: str
    category: str
    summary: str
    required_params: list[str]
    optional_params: dict[str, Any]

    def validate_params(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate tool parameters.

        Args:
            params: Parameters to validate

        Returns:
            Tuple of (is_valid, missing_params)
        """
        missing = [p for p in self.required_params if p not in params]
        return (len(missing) == 0, missing)


@dataclass
class ToolResult:
    """Result from tool execution."""

    success: bool
    output: Any
    exit_code: int = 0
    error_message: str | None = None
    execution_time: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "output": self.output,
            "exit_code": self.exit_code,
            "error_message": self.error_message,
            "execution_time": self.execution_time,
        }


class IToolAdapter(ABC):
    """Abstract base class for tool adapters."""

    @abstractmethod
    def get_spec(self) -> ToolSpec:
        """
        Get tool specification.

        Returns:
            Tool specification with metadata
        """
        pass

    @abstractmethod
    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate tool parameters.

        Args:
            params: Parameters to validate

        Returns:
            Tuple of (is_valid, missing/invalid_params)
        """
        pass

    @abstractmethod
    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """
        Execute the tool with given parameters.

        Args:
            params: Tool parameters
            context: Optional execution context (agent_id, session_id, etc.)

        Returns:
            Tool execution result
        """
        pass

    def get_help(self) -> str:
        """
        Get help text for the tool.

        Returns:
            Help text describing tool usage
        """
        spec = self.get_spec()
        help_text = [
            f"Tool: {spec.name} (v{spec.version})",
            f"Category: {spec.category}",
            f"Summary: {spec.summary}",
            "",
            "Required parameters:",
        ]

        for param in spec.required_params:
            help_text.append(f"  - {param}")

        if spec.optional_params:
            help_text.append("")
            help_text.append("Optional parameters:")
            for param, default in spec.optional_params.items():
                help_text.append(f"  - {param} (default: {default})")

        return "\n".join(help_text)

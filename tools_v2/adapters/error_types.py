"""
Toolbelt Error Types
====================

Error taxonomy for Agent Toolbelt operations.

V2 Compliance: <120 lines
Author: Agent-7 - Repository Cloning Specialist
"""


class ToolbeltError(Exception):
    """Base exception for toolbelt operations."""

    def __init__(self, message: str, tool_name: str | None = None):
        """
        Initialize toolbelt error.

        Args:
            message: Error description
            tool_name: Name of tool that raised error
        """
        self.tool_name = tool_name
        super().__init__(message)


class ToolNotFoundError(ToolbeltError):
    """Raised when requested tool is not found in registry."""

    pass


class ToolValidationError(ToolbeltError):
    """Raised when tool parameter validation fails."""

    def __init__(
        self, message: str, tool_name: str | None = None, invalid_params: list[str] | None = None
    ):
        """
        Initialize validation error.

        Args:
            message: Error description
            tool_name: Name of tool
            invalid_params: List of invalid parameter names
        """
        self.invalid_params = invalid_params or []
        super().__init__(message, tool_name)


class ToolExecutionError(ToolbeltError):
    """Raised when tool execution fails."""

    def __init__(self, message: str, tool_name: str | None = None, exit_code: int | None = None):
        """
        Initialize execution error.

        Args:
            message: Error description
            tool_name: Name of tool
            exit_code: Process exit code if applicable
        """
        self.exit_code = exit_code
        super().__init__(message, tool_name)


class ToolDependencyError(ToolbeltError):
    """Raised when tool dependencies are missing."""

    def __init__(
        self, message: str, tool_name: str | None = None, missing_deps: list[str] | None = None
    ):
        """
        Initialize dependency error.

        Args:
            message: Error description
            tool_name: Name of tool
            missing_deps: List of missing dependency names
        """
        self.missing_deps = missing_deps or []
        super().__init__(message, tool_name)


class ToolConfigurationError(ToolbeltError):
    """Raised when tool configuration is invalid."""

    pass


# Error handling utilities


def format_toolbelt_error(error: ToolbeltError) -> str:
    """
    Format toolbelt error for user display.

    Args:
        error: Toolbelt error instance

    Returns:
        Formatted error message
    """
    parts = ["❌ Toolbelt Error"]

    if error.tool_name:
        parts.append(f"[{error.tool_name}]")

    parts.append(f": {str(error)}")

    if isinstance(error, ToolValidationError) and error.invalid_params:
        parts.append(f" (Invalid params: {', '.join(error.invalid_params)})")
    elif isinstance(error, ToolExecutionError) and error.exit_code is not None:
        parts.append(f" (Exit code: {error.exit_code})")
    elif isinstance(error, ToolDependencyError) and error.missing_deps:
        parts.append(f" (Missing: {', '.join(error.missing_deps)})")

    return "".join(parts)

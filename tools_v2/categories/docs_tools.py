"""
Documentation Tools
===================

Tool adapters for documentation operations.

V2 Compliance: <180 lines
Author: Agent-7 - Repository Cloning Specialist
"""

import logging
import subprocess
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class DocsSearchTool(IToolAdapter):
    """Search project documentation semantically."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="docs.search",
            version="1.0.0",
            category="docs",
            summary="Semantic search across project documentation",
            required_params=["query"],
            optional_params={"agent_id": None, "results": 5},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute documentation search."""
        try:
            cmd = [
                "python",
                "scripts/agent_documentation_cli.py",
                "search",
                params["query"],
                "--results",
                str(params.get("results", 5)),
            ]

            if params.get("agent_id"):
                cmd.extend(["--agent", params["agent_id"]])

            result = subprocess.run(cmd, capture_output=True, text=True)

            return ToolResult(
                success=result.returncode == 0,
                output=result.stdout,
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error searching docs: {e}")
            raise ToolExecutionError(str(e), tool_name="docs.search")


class DocsExportTool(IToolAdapter):
    """Export agent knowledge base."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="docs.export",
            version="1.0.0",
            category="docs",
            summary="Export agent knowledge base to JSON",
            required_params=["agent_id"],
            optional_params={"output_file": None},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        spec = self.get_spec()
        return spec.validate_params(params)

    def execute(self, params: dict[str, Any], context: dict[str, Any] | None = None) -> ToolResult:
        """Execute knowledge base export."""
        try:
            agent_id = params["agent_id"]
            output_file = params.get("output_file") or f"agent_{agent_id}_knowledge.json"

            cmd = [
                "python",
                "scripts/agent_documentation_cli.py",
                "export",
                output_file,
                "--agent",
                agent_id,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            return ToolResult(
                success=result.returncode == 0,
                output={"file": output_file, "agent_id": agent_id},
                exit_code=result.returncode,
                error_message=result.stderr if result.returncode != 0 else None,
            )
        except Exception as e:
            logger.error(f"Error exporting docs: {e}")
            raise ToolExecutionError(str(e), tool_name="docs.export")

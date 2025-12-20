"""
Web Tools - Agent Toolbelt V2
==============================

Web development and web interface tools for agents.

V2 Compliance: <400 lines
Author: Agent-7 (Web Development Specialist) - 2025-01-27
Architecture Review: Agent-2 (Architecture & Design)
"""

import logging
from pathlib import Path
from typing import Any

from ..adapters.base_adapter import IToolAdapter, ToolResult, ToolSpec
from ..adapters.error_types import ToolExecutionError

logger = logging.getLogger(__name__)


class DiscordMermaidRendererTool(IToolAdapter):
    """Render Mermaid diagrams to images for Discord posting."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="web.mermaid_render",
            version="1.0.0",
            category="web",
            summary="Render Mermaid diagrams to images for Discord",
            required_params=["content"],
            optional_params={"output_dir": "reports/mermaid", "format": "png"},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        if not params.get("content"):
            return (False, ["content parameter required"])
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute Mermaid rendering."""
        try:
            # V2 Compliance: Import from tools_v2/utils/ (migrated 2025-01-27)
            from ..utils.discord_mermaid_renderer import DiscordMermaidRenderer

            renderer = DiscordMermaidRenderer()
            content = params["content"]
            output_dir = Path(params.get("output_dir", "reports/mermaid"))
            output_dir.mkdir(parents=True, exist_ok=True)

            diagrams = renderer.extract_mermaid_diagrams(content)
            results = []

            for diagram_code, pos in diagrams:
                try:
                    image_path = renderer.render_to_file(
                        diagram_code, output_dir / f"diagram_{pos}.png"
                    )
                    results.append({"position": pos, "image_path": str(image_path)})
                except Exception as e:
                    results.append({"position": pos, "error": str(e)})

            return ToolResult(
                success=len(results) > 0,
                output={"diagrams_rendered": len(results), "results": results},
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error rendering Mermaid: {e}")
            raise ToolExecutionError(str(e), tool_name="web.mermaid_render")


class DiscordWebTestTool(IToolAdapter):
    """Automate Discord web interface testing."""

    def get_spec(self) -> ToolSpec:
        """Get tool specification."""
        return ToolSpec(
            name="web.discord_test",
            version="1.0.0",
            category="web",
            summary="Automate Discord bot testing via web interface",
            required_params=["commands"],
            optional_params={"channel": None, "timeout": 30},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate parameters."""
        if not params.get("commands"):
            return (False, ["commands parameter required (list of commands to test)"])
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """Execute Discord web testing."""
        try:
            # TODO: Migrate to tools_v2/utils/ when ready
            # Legacy dependency: tools/coordination/discord_web_test_automation.py
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "coordination"))
            from discord_web_test_automation import DiscordWebTester

            tester = DiscordWebTester()
            commands = params["commands"]
            if isinstance(commands, str):
                commands = [commands]

            results = []
            for cmd in commands:
                try:
                    result = tester.test_command(cmd, timeout=params.get("timeout", 30))
                    results.append({"command": cmd, "success": result})
                except Exception as e:
                    results.append({"command": cmd, "success": False, "error": str(e)})

            return ToolResult(
                success=all(r.get("success", False) for r in results),
                output={"commands_tested": len(commands), "results": results},
                exit_code=0,
            )
        except Exception as e:
            logger.error(f"Error testing Discord web: {e}")
            raise ToolExecutionError(str(e), tool_name="web.discord_test")


__all__ = [
    "DiscordMermaidRendererTool",
    "DiscordWebTestTool",
]



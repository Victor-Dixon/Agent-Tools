"""
Discord Profile Tools - Agent Toolbelt V2
=========================================

Tools for viewing and managing Discord username mappings in profiles.

Author: Agent-4 (Captain)
Date: 2025-01-27
V2 Compliance: <300 lines per tool
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

from ..adapters.base_adapter import IToolAdapter, ToolResult
from ..core.tool_spec import ToolSpec

logger = logging.getLogger(__name__)


class DiscordProfileViewerTool(IToolAdapter):
    """View Discord username mappings in agent profiles."""

    def get_name(self) -> str:
        return "discord_profile.view"

    def get_description(self) -> str:
        return "View Discord username mappings from agent profiles"

    def get_spec(self) -> ToolSpec:
        return ToolSpec(
            name="discord_profile.view",
            version="1.0.0",
            category="profiles",
            summary="View Discord profiles",
            required_params=[],
            optional_params={"agent_id": None},
        )

    def validate(self, params: dict[str, Any]) -> tuple[bool, list[str]]:
        return (True, [])

    def execute(
        self, params: dict[str, Any], context: dict[str, Any] | None = None
    ) -> ToolResult:
        """View Discord profiles."""
        try:
            agent_id = params.get("agent_id")
            profiles = {}

            if agent_id:
                # Single agent
                profile = self._load_profile(agent_id)
                if profile:
                    profiles[agent_id] = profile
            else:
                # All agents
                for i in range(1, 9):
                    aid = f"Agent-{i}"
                    profile = self._load_profile(aid)
                    if profile:
                        profiles[aid] = profile

            output = {
                "profiles": profiles,
                "total": len(profiles),
                "with_discord": sum(
                    1 for p in profiles.values() if p.get("discord_username")
                ),
            }

            return ToolResult(success=True, output=output)

        except Exception as e:
            logger.error(f"Discord profile viewing failed: {e}")
            return ToolResult(
                success=False, output=None, error_message=str(e), exit_code=1
            )

    def _load_profile(self, agent_id: str) -> dict[str, Any] | None:
        """Load agent profile."""
        profile_file = Path("agent_workspaces") / agent_id / "profile.json"
        if not profile_file.exists():
            return None

        try:
            return json.loads(profile_file.read_text())
        except Exception:
            return None


#!/usr/bin/env python3
"""
Leaderboard Executor - Agent Toolbelt V2
========================================

Handles competition leaderboard operations:
- Show current standings
- Agent details
- Top N agents
- Award achievements

Author: Agent-8 (SSOT & Documentation Specialist)
Created: 2025-10-15
Mission: Toolbelt expansion Phase 1
V2 Compliance: <100 lines, focused executor
"""

import logging
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


class LeaderboardExecutor:
    """Execute leaderboard commands via autonomous_leaderboard.py."""

    def __init__(self):
        """Initialize leaderboard executor."""
        self.leaderboard_tool = "tools/autonomous_leaderboard.py"

    def execute(self, args) -> int:
        """
        Execute leaderboard command.

        Args:
            args: Parsed arguments with lb_action

        Returns:
            Exit code (0 for success)
        """
        action = args.lb_action

        if action == "show":
            return self._show_leaderboard(args)
        elif action == "agent":
            return self._agent_details(args)
        elif action == "top":
            return self._top_agents(args)
        elif action == "award":
            return self._award_achievement(args)
        else:
            print(f"❌ Unknown leaderboard action: {action}")
            return 1

    def _show_leaderboard(self, args) -> int:
        """Show current competition standings."""
        cmd = ["python", self.leaderboard_tool, "show"]
        print("🏆 Current Competition Standings:")
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode

    def _agent_details(self, args) -> int:
        """Show details for specific agent."""
        if not hasattr(args, "agent_id") or not args.agent_id:
            print("❌ agent_id required")
            return 1

        cmd = ["python", self.leaderboard_tool, "details", args.agent_id]
        print(f"📊 Details for {args.agent_id}:")
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode

    def _top_agents(self, args) -> int:
        """Show top N agents."""
        n = getattr(args, "n", 5)
        cmd = ["python", self.leaderboard_tool, "top", str(n)]
        print(f"🥇 Top {n} Agents:")
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode

    def _award_achievement(self, args) -> int:
        """Award achievement to agent."""
        if not hasattr(args, "agent_id") or not hasattr(args, "achievement"):
            print("❌ agent_id and achievement required")
            return 1

        cmd = [
            "python",
            self.leaderboard_tool,
            "award",
            args.agent_id,
            args.achievement,
        ]
        print(f"🏅 Awarding achievement to {args.agent_id}...")
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode


__all__ = ["LeaderboardExecutor"]


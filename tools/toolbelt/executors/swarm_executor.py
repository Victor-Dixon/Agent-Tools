#!/usr/bin/env python3
"""
Swarm Executor - Agent Toolbelt V2
==================================

Handles swarm status and coordination operations:
- Captain snapshot (quick overview)
- Agent check-in system
- Active agents listing
- Swarm health status

Author: Agent-8 (SSOT & Documentation Specialist)
Created: 2025-10-15
Mission: Toolbelt expansion Phase 1
V2 Compliance: <100 lines, focused executor
"""

import logging
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


class SwarmExecutor:
    """Execute swarm coordination commands."""

    def __init__(self):
        """Initialize swarm executor."""
        self.snapshot_tool = "tools/captain_snapshot.py"
        self.checkin_tool = "tools/agent_checkin.py"

    def execute(self, args) -> int:
        """
        Execute swarm command.

        Args:
            args: Parsed arguments with swarm_action

        Returns:
            Exit code (0 for success)
        """
        action = args.swarm_action

        if action == "snapshot":
            return self._captain_snapshot(args)
        elif action == "checkin":
            return self._agent_checkin(args)
        elif action == "active":
            return self._active_agents(args)
        elif action == "health":
            return self._swarm_health(args)
        else:
            print(f"❌ Unknown swarm action: {action}")
            return 1

    def _captain_snapshot(self, args) -> int:
        """Show captain's swarm snapshot."""
        cmd = ["python", self.snapshot_tool]
        print("📊 Captain's Swarm Snapshot:")
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode

    def _agent_checkin(self, args) -> int:
        """Agent check-in to swarm system."""
        if not hasattr(args, "agent") or not args.agent:
            print("❌ --agent required for check-in")
            return 1

        status = getattr(args, "status", "ACTIVE")
        cmd = ["python", self.checkin_tool, "--agent", args.agent, "--status", status]
        print(f"✅ Checking in {args.agent}...")
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode

    def _active_agents(self, args) -> int:
        """Show currently active agents."""
        print("🐝 Active Agents:")
        cmd = ["python", self.snapshot_tool, "--active-only"]
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode

    def _swarm_health(self, args) -> int:
        """Show overall swarm health status."""
        print("💚 Swarm Health Status:")
        cmd = ["python", self.snapshot_tool, "--health"]
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode


__all__ = ["SwarmExecutor"]


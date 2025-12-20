#!/usr/bin/env python3
"""
Messaging Executor - Agent Toolbelt
===================================

Execute messaging operations for agent toolbelt.

Author: Agent-2 (Extracted from agent_toolbelt_executors.py for V2 compliance)
V2 Compliance: <100 lines, single responsibility
"""

import logging
import subprocess

logger = logging.getLogger(__name__)


class MessagingExecutor:
    """Execute messaging operations."""

    @staticmethod
    def execute(args):
        """Execute messaging operations."""
        cmd = ["python", "-m", "src.services.messaging_cli"]

        if args.broadcast:
            cmd.extend(["--broadcast", "--message", args.text])
        elif args.agent:
            cmd.extend(["--agent", args.agent, "--message", args.text])
        elif args.inbox:
            print(f"Reading inbox for {args.agent}")
            return 0
        elif args.status:
            cmd.append("--coordinates")

        if args.priority:
            cmd.extend(["--priority", args.priority])

        result = subprocess.run(cmd)
        return result.returncode

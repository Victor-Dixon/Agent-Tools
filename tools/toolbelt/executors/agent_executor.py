#!/usr/bin/env python3
"""
Agent Executor - Agent Toolbelt
===============================

Execute agent operations for agent toolbelt.

Author: Agent-2 (Extracted from agent_toolbelt_executors.py for V2 compliance)
V2 Compliance: <100 lines, single responsibility
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AgentExecutor:
    """Execute agent operations."""

    @staticmethod
    def execute(args):
        """Execute agent operations."""
        if args.agent_action == "status":
            from src.services.agent_management import AgentStatusManager

            status_mgr = AgentStatusManager(agent_id=args.agent)
            status = status_mgr.get_agent_status()
            print(f"\n📊 Agent Status: {args.agent}")
            for key, value in status.items():
                print(f"  {key}: {value}")
            return 0

        elif args.agent_action == "inbox":
            inbox_path = Path(f"agent_workspaces/{args.agent}/inbox")
            if args.search:
                from src.services.agent_management import TaskContextManager

                context_mgr = TaskContextManager(agent_id=args.agent)
                print(f"🔍 Searching inbox for: {args.search}")
            else:
                if inbox_path.exists():
                    messages = list(inbox_path.glob("*.md"))
                    print(f"\n📨 Inbox for {args.agent}: {len(messages)} messages")
                    for msg in messages[:10]:
                        print(f"  - {msg.name}")
                else:
                    print(f"❌ No inbox found for {args.agent}")
            return 0

        elif args.agent_action == "claim-task":
            print(f"🎯 Claiming next task for {args.agent}")
            return 0

        elif args.agent_action == "coordinates":
            coords_file = Path("cursor_agent_coords.json")
            if coords_file.exists():
                coords = json.loads(coords_file.read_text())
                print("\n📍 Agent Coordinates:")
                for agent_id, coord in coords.items():
                    print(f"  {agent_id}: {coord}")
            return 0

        return 1

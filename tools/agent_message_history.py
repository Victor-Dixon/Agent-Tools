#!/usr/bin/env python3
"""
Agent Message History - Recent Message Viewer
==============================================

View recent agent message exchanges to avoid duplicate/overlapping messages.
Shows sent/received messages with timestamps and priorities.

Usage:
    python tools/agent_message_history.py --agent Agent-6
    python tools/agent_message_history.py --agent Agent-6 --count 10
    python tools/agent_message_history.py --agent Agent-6 --sender Agent-4
    python tools/agent_message_history.py --between Agent-4 Agent-6

Author: Agent-6 - VSCode Forking & Quality Gates Specialist
Created: 2025-10-13
V2 Compliance: <400 lines
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class MessageHistoryViewer:
    """View agent message history."""

    def __init__(self, workspace_root: Path):
        """Initialize message history viewer."""
        self.workspace_root = workspace_root
        self.agent_workspaces = workspace_root / "agent_workspaces"
        self.message_queue = workspace_root / "message_queue"

    def get_agent_inbox(self, agent_id: str) -> list[dict[str, Any]]:
        """Get messages from agent's inbox."""
        inbox_path = self.agent_workspaces / agent_id / "inbox"

        if not inbox_path.exists():
            return []

        messages = []

        # Read all .md files in inbox
        for msg_file in inbox_path.glob("*.md"):
            try:
                content = msg_file.read_text(encoding="utf-8")

                # Parse message metadata from content
                msg = {
                    "filename": msg_file.name,
                    "timestamp": datetime.fromtimestamp(msg_file.stat().st_mtime),
                    "content": content,
                    "sender": self._extract_sender(content),
                    "priority": self._extract_priority(content),
                }
                messages.append(msg)
            except Exception as e:
                print(f"⚠️ Error reading {msg_file.name}: {e}", file=sys.stderr)

        return sorted(messages, key=lambda m: m["timestamp"], reverse=True)

    def get_sent_messages(self, agent_id: str) -> list[dict[str, Any]]:
        """Get messages sent by agent (from sent/ directory)."""
        sent_path = self.agent_workspaces / agent_id / "sent"

        if not sent_path.exists():
            return []

        messages = []

        for msg_file in sent_path.glob("*.md"):
            try:
                content = msg_file.read_text(encoding="utf-8")

                msg = {
                    "filename": msg_file.name,
                    "timestamp": datetime.fromtimestamp(msg_file.stat().st_mtime),
                    "content": content,
                    "recipient": self._extract_recipient(content),
                    "priority": self._extract_priority(content),
                }
                messages.append(msg)
            except Exception as e:
                print(f"⚠️ Error reading {msg_file.name}: {e}", file=sys.stderr)

        return sorted(messages, key=lambda m: m["timestamp"], reverse=True)

    def _extract_sender(self, content: str) -> str:
        """Extract sender from message content."""
        # Look for patterns like "[C2A] CAPTAIN" or "[A2A] AGENT-X"
        lines = content.split("\n")
        for line in lines[:5]:  # Check first 5 lines
            if "→" in line:
                parts = line.split("→")
                if len(parts) >= 2:
                    sender = parts[0].strip()
                    # Clean up formatting
                    sender = sender.replace("[C2A]", "").replace("[A2A]", "").strip()
                    return sender
        return "Unknown"

    def _extract_recipient(self, content: str) -> str:
        """Extract recipient from message content."""
        lines = content.split("\n")
        for line in lines[:5]:
            if "→" in line:
                parts = line.split("→")
                if len(parts) >= 2:
                    recipient = parts[1].split(":")[0].strip()
                    return recipient
        return "Unknown"

    def _extract_priority(self, content: str) -> str:
        """Extract priority from message content."""
        if "Priority: urgent" in content:
            return "urgent"
        elif "Priority: high" in content:
            return "high"
        elif "Priority: regular" in content:
            return "regular"
        else:
            return "unknown"

    def format_message_list(
        self, messages: list[dict[str, Any]], direction: str = "received", limit: int = 5
    ) -> str:
        """Format message list for display."""
        output = []

        arrow = "→" if direction == "sent" else "←"

        for i, msg in enumerate(messages[:limit]):
            timestamp = msg["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            priority_icon = self._get_priority_icon(msg["priority"])

            if direction == "sent":
                other_party = msg.get("recipient", "Unknown")
            else:
                other_party = msg.get("sender", "Unknown")

            # Extract first line of content (usually the title/subject)
            first_line = msg["content"].split("\n")[0][:50]

            output.append(f"{i+1}. {timestamp} {priority_icon} {arrow} {other_party}")
            output.append(f"   {first_line}...")
            output.append("")

        return "\n".join(output)

    def _get_priority_icon(self, priority: str) -> str:
        """Get icon for priority level."""
        icons = {"urgent": "🔥", "high": "⚡", "regular": "📝", "unknown": "❓"}
        return icons.get(priority, "❓")

    def show_conversation(self, agent1: str, agent2: str, limit: int = 10) -> None:
        """Show conversation between two agents."""
        print(f"\n{'='*60}")
        print(f"💬 Conversation: {agent1} ↔ {agent2}")
        print(f"{'='*60}\n")

        # Get messages both ways
        agent1_to_2 = self.get_sent_messages(agent1)
        agent2_to_1 = self.get_sent_messages(agent2)

        # Filter for messages to each other
        agent1_to_2 = [m for m in agent1_to_2 if agent2 in m.get("recipient", "")]
        agent2_to_1 = [m for m in agent2_to_1 if agent1 in m.get("recipient", "")]

        # Combine and sort by timestamp
        all_messages = []
        for msg in agent1_to_2:
            msg["direction"] = f"{agent1} → {agent2}"
            all_messages.append(msg)

        for msg in agent2_to_1:
            msg["direction"] = f"{agent2} → {agent1}"
            all_messages.append(msg)

        all_messages.sort(key=lambda m: m["timestamp"], reverse=True)

        if not all_messages:
            print(f"❌ No messages found between {agent1} and {agent2}")
            return

        # Display messages
        for i, msg in enumerate(all_messages[:limit]):
            timestamp = msg["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            priority_icon = self._get_priority_icon(msg["priority"])

            print(f"{i+1}. {timestamp} {priority_icon} {msg['direction']}")

            # Show snippet of content
            lines = msg["content"].split("\n")
            for line in lines[:3]:
                if line.strip():
                    print(f"   {line[:70]}")
            print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="💬 Agent Message History - View recent agent messages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # View received messages
  python tools/agent_message_history.py --agent Agent-6
  
  # View last 10 messages
  python tools/agent_message_history.py --agent Agent-6 --count 10
  
  # View messages from specific sender
  python tools/agent_message_history.py --agent Agent-6 --sender Agent-4
  
  # View conversation between two agents
  python tools/agent_message_history.py --between Agent-4 Agent-6

🐝 WE. ARE. SWARM. ⚡️🔥
        """,
    )

    parser.add_argument("--agent", type=str, help="Agent ID to check messages for")

    parser.add_argument(
        "--count", type=int, default=5, help="Number of messages to show (default: 5)"
    )

    parser.add_argument("--sender", type=str, help="Filter by sender")

    parser.add_argument(
        "--between",
        nargs=2,
        metavar=("AGENT1", "AGENT2"),
        help="Show conversation between two agents",
    )

    parser.add_argument(
        "--sent", action="store_true", help="Show sent messages instead of received"
    )

    args = parser.parse_args()

    # Initialize viewer
    workspace_root = Path(__file__).parent.parent
    viewer = MessageHistoryViewer(workspace_root)

    # Show conversation between two agents
    if args.between:
        viewer.show_conversation(args.between[0], args.between[1], args.count)
        return

    # Validate arguments
    if not args.agent:
        parser.print_help()
        print("\n❌ Error: Must specify --agent or --between")
        sys.exit(1)

    # Get messages
    if args.sent:
        messages = viewer.get_sent_messages(args.agent)
        direction = "sent"
        title = f"📤 Messages Sent by {args.agent}"
    else:
        messages = viewer.get_agent_inbox(args.agent)
        direction = "received"
        title = f"📥 Messages Received by {args.agent}"

    # Filter by sender if specified
    if args.sender and not args.sent:
        messages = [m for m in messages if args.sender in m.get("sender", "")]
        title += f" (from {args.sender})"

    # Display messages
    print(f"\n{'='*60}")
    print(title)
    print(f"{'='*60}\n")

    if not messages:
        print("❌ No messages found!")
    else:
        print(f"Showing {min(args.count, len(messages))} of {len(messages)} messages:\n")
        print(viewer.format_message_list(messages, direction, args.count))


if __name__ == "__main__":
    main()

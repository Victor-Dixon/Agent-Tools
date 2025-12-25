#!/usr/bin/env python3
"""
Swarm MCP Toolbelt CLI
"""

import argparse
import json
import sys
from pathlib import Path


def cmd_status(args):
    """Show swarm status."""
    from .core.coordinator import SwarmCoordinator
    
    swarm = SwarmCoordinator(
        agents=args.agents.split(",") if args.agents else ["agent-1"],
        workspace=args.workspace
    )
    
    print("🐝 Swarm Status")
    print("=" * 40)
    
    for agent_id in swarm.agents:
        status = swarm.get_status(agent_id)
        icon = "🟢" if status.status == "idle" else "🔵" if status.status == "working" else "⚪"
        print(f"{icon} {agent_id}: {status.status}")
        if status.current_task:
            print(f"   └─ Task: {status.current_task[:50]}...")
    
    idle = swarm.get_idle_agents()
    print(f"\n📊 {len(idle)}/{len(swarm.agents)} agents idle")


def cmd_send(args):
    """Send a message."""
    from .core.messaging import MessageQueue
    
    queue = MessageQueue(args.queue_dir)
    msg = queue.send(args.sender, args.recipient, args.message)
    
    print(f"✅ Message sent: {msg.id}")
    print(f"   From: {msg.sender} → To: {msg.recipient}")


def cmd_inbox(args):
    """Check inbox."""
    from .core.messaging import MessageQueue
    
    queue = MessageQueue(args.queue_dir)
    messages = queue.get_inbox(args.agent, unread_only=args.unread)
    
    print(f"📬 Inbox for {args.agent}")
    print("=" * 40)
    
    if not messages:
        print("(empty)")
        return
    
    for msg in messages:
        icon = "📩" if not msg.read else "📭"
        print(f"{icon} [{msg.priority.name}] From {msg.sender}:")
        print(f"   {msg.content[:60]}...")
        print()


def cmd_brain_search(args):
    """Search swarm brain."""
    from .core.brain import SwarmBrain
    
    brain = SwarmBrain(args.brain_dir)
    results = brain.search(args.query, limit=args.limit)
    
    print(f"🧠 Search results for '{args.query}'")
    print("=" * 40)
    
    if not results:
        print("(no results)")
        return
    
    for learning in results:
        print(f"📚 {learning.title}")
        print(f"   Category: {learning.category} | By: {learning.agent_id}")
        print(f"   {learning.content[:100]}...")
        print()


def cmd_brain_share(args):
    """Share a learning."""
    from .core.brain import SwarmBrain
    
    brain = SwarmBrain(args.brain_dir)
    learning = brain.share_learning(
        agent_id=args.agent,
        category=args.category,
        title=args.title,
        content=args.content,
        tags=args.tags.split(",") if args.tags else []
    )
    
    print(f"✅ Learning shared: {learning.id}")


def cmd_discover(args):
    """Discover tasks in codebase."""
    from .core.coordinator import SwarmCoordinator
    
    swarm = SwarmCoordinator(agents=["discovery"], workspace=args.workspace)
    tasks = swarm.discover_tasks(args.path)
    
    print(f"🔍 Discovered {len(tasks)} tasks in {args.path}")
    print("=" * 40)
    
    for task in tasks[:args.limit]:
        print(f"📋 [{task.task_type.upper()}] {task.description[:60]}...")
        if task.file_path:
            print(f"   └─ {task.file_path}")
        print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="swarm",
        description="🐝 Swarm MCP Toolbelt - Multi-Agent AI Coordination"
    )
    parser.add_argument("--workspace", default="./agent_workspaces", help="Agent workspace directory")
    parser.add_argument("--queue-dir", default="./messages", help="Message queue directory")
    parser.add_argument("--brain-dir", default="./swarm_brain", help="Swarm brain directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # status command
    status_parser = subparsers.add_parser("status", help="Show swarm status")
    status_parser.add_argument("--agents", help="Comma-separated agent IDs")
    status_parser.set_defaults(func=cmd_status)
    
    # send command
    send_parser = subparsers.add_parser("send", help="Send a message")
    send_parser.add_argument("sender", help="Sender agent ID")
    send_parser.add_argument("recipient", help="Recipient agent ID")
    send_parser.add_argument("message", help="Message content")
    send_parser.set_defaults(func=cmd_send)
    
    # inbox command
    inbox_parser = subparsers.add_parser("inbox", help="Check agent inbox")
    inbox_parser.add_argument("agent", help="Agent ID")
    inbox_parser.add_argument("--unread", action="store_true", help="Show unread only")
    inbox_parser.set_defaults(func=cmd_inbox)
    
    # brain search command
    search_parser = subparsers.add_parser("search", help="Search swarm brain")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")
    search_parser.set_defaults(func=cmd_brain_search)
    
    # brain share command
    share_parser = subparsers.add_parser("share", help="Share a learning")
    share_parser.add_argument("--agent", required=True, help="Agent ID")
    share_parser.add_argument("--category", required=True, help="Category")
    share_parser.add_argument("--title", required=True, help="Title")
    share_parser.add_argument("--content", required=True, help="Content")
    share_parser.add_argument("--tags", help="Comma-separated tags")
    share_parser.set_defaults(func=cmd_brain_share)
    
    # discover command
    discover_parser = subparsers.add_parser("discover", help="Discover tasks")
    discover_parser.add_argument("--path", default=".", help="Path to scan")
    discover_parser.add_argument("--limit", type=int, default=20, help="Max results")
    discover_parser.set_defaults(func=cmd_discover)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        args.func(args)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

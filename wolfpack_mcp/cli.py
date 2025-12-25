#!/usr/bin/env python3
"""
🐺 Wolfpack MCP Toolbelt CLI

"Alone we are strong. Together we are unstoppable."
"""

import argparse
import sys
from pathlib import Path


def cmd_status(args):
    """Show pack status."""
    from .core.coordinator import PackCoordinator
    
    pack = PackCoordinator(
        wolves=args.wolves.split(",") if args.wolves else ["alpha"],
        den=args.den
    )
    
    print("🐺 Pack Status")
    print("=" * 40)
    
    for wolf_id in pack.wolves:
        status = pack.get_status(wolf_id)
        if status.role == "alpha":
            icon = "👑"
        elif status.status == "ready":
            icon = "🟢"
        elif status.status == "hunting":
            icon = "🏃"
        else:
            icon = "💤"
        print(f"{icon} {wolf_id} [{status.role}]: {status.status}")
        if status.current_hunt:
            print(f"   └─ Hunt: {status.current_hunt[:50]}...")
    
    ready = pack.get_ready_wolves()
    print(f"\n📊 {len(ready)}/{len(pack.wolves)} wolves ready")


def cmd_howl(args):
    """Send a howl."""
    from .core.messaging import MessageQueue
    
    queue = MessageQueue(args.territory)
    msg = queue.send(args.sender, args.recipient, args.message)
    
    print(f"🐺 Howl sent: {msg.id}")
    print(f"   From: {msg.sender} → To: {msg.recipient}")


def cmd_listen(args):
    """Listen for howls."""
    from .core.messaging import MessageQueue
    
    queue = MessageQueue(args.territory)
    howls = queue.listen(args.wolf, unheard_only=args.unheard)
    
    print(f"🐺 Incoming howls for {args.wolf}")
    print("=" * 40)
    
    if not howls:
        print("(silence)")
        return
    
    for msg in howls:
        icon = "📢" if not msg.heard else "✓"
        urgency = "🚨" if msg.urgency.value <= 2 else ""
        print(f"{icon} {urgency}From {msg.sender}:")
        print(f"   {msg.content[:60]}...")
        print()


def cmd_recall(args):
    """Search pack memory."""
    from .core.memory import PackMemory
    
    memory = PackMemory(args.memory)
    results = memory.recall(args.query, limit=args.limit)
    
    print(f"🧠 Pack memory: '{args.query}'")
    print("=" * 40)
    
    if not results:
        print("(no wisdom found)")
        return
    
    for lore in results:
        print(f"📜 {lore.title}")
        print(f"   Category: {lore.category} | By: {lore.wolf_id}")
        print(f"   {lore.wisdom[:100]}...")
        print()


def cmd_share(args):
    """Share hunting wisdom."""
    from .core.memory import PackMemory
    
    memory = PackMemory(args.memory)
    lore = memory.share_lore(
        wolf_id=args.wolf,
        category=args.category,
        title=args.title,
        wisdom=args.wisdom,
        tags=args.tags.split(",") if args.tags else []
    )
    
    print(f"🐺 Wisdom shared: {lore.id}")


def cmd_scout(args):
    """Scout territory for prey."""
    from .core.coordinator import PackCoordinator
    
    pack = PackCoordinator(wolves=["scout"], den=args.den)
    prey = pack.scout_territory(args.path)
    
    print(f"🔍 Scouted {len(prey)} prey in {args.path}")
    print("=" * 40)
    
    for p in prey[:args.limit]:
        difficulty = "🟢" if p.difficulty <= 2 else "🟡" if p.difficulty <= 3 else "🔴"
        print(f"{difficulty} [{p.prey_type.upper()}] {p.description[:50]}...")
        if p.location:
            print(f"   └─ {p.location}")
        print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="wolfpack",
        description="🐺 Wolfpack MCP Toolbelt - Multi-Agent AI Coordination"
    )
    parser.add_argument("--den", default="./wolf_den", help="Pack den directory")
    parser.add_argument("--territory", default="./pack_messages", help="Message territory")
    parser.add_argument("--memory", default="./pack_memory", help="Pack memory directory")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # status command
    status_parser = subparsers.add_parser("status", help="Show pack status")
    status_parser.add_argument("--wolves", help="Comma-separated wolf IDs")
    status_parser.set_defaults(func=cmd_status)
    
    # howl command
    howl_parser = subparsers.add_parser("howl", help="Send a howl")
    howl_parser.add_argument("sender", help="Sending wolf")
    howl_parser.add_argument("recipient", help="Receiving wolf")
    howl_parser.add_argument("message", help="Howl content")
    howl_parser.set_defaults(func=cmd_howl)
    
    # listen command
    listen_parser = subparsers.add_parser("listen", help="Listen for howls")
    listen_parser.add_argument("wolf", help="Wolf ID")
    listen_parser.add_argument("--unheard", action="store_true", help="Unheard only")
    listen_parser.set_defaults(func=cmd_listen)
    
    # recall command
    recall_parser = subparsers.add_parser("recall", help="Search pack memory")
    recall_parser.add_argument("query", help="Search query")
    recall_parser.add_argument("--limit", type=int, default=10, help="Max results")
    recall_parser.set_defaults(func=cmd_recall)
    
    # share command
    share_parser = subparsers.add_parser("share", help="Share wisdom")
    share_parser.add_argument("--wolf", required=True, help="Wolf ID")
    share_parser.add_argument("--category", required=True, help="Category")
    share_parser.add_argument("--title", required=True, help="Title")
    share_parser.add_argument("--wisdom", required=True, help="The wisdom")
    share_parser.add_argument("--tags", help="Comma-separated tags")
    share_parser.set_defaults(func=cmd_share)
    
    # scout command
    scout_parser = subparsers.add_parser("scout", help="Scout for prey")
    scout_parser.add_argument("--path", default=".", help="Territory to scout")
    scout_parser.add_argument("--limit", type=int, default=20, help="Max results")
    scout_parser.set_defaults(func=cmd_scout)
    
    args = parser.parse_args()
    
    if not args.command:
        print("🐺 WOLFPACK MCP TOOLBELT")
        print("=" * 40)
        print('"Alone we are strong. Together we are unstoppable."')
        print()
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

#!/usr/bin/env python3
"""
Swarm Brain CLI - Easy Knowledge Sharing
Agent-8 (QA & Autonomous Systems Specialist)

Purpose: Simplify Swarm Brain contributions (10 min manual → 1 min automated!)
Impact: Encourages knowledge sharing across swarm
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.swarm_brain.swarm_memory import SwarmMemory


def share_learning(args):
    """Share a learning to Swarm Brain."""
    memory = SwarmMemory(agent_id=args.agent)
    
    print(f"\n🧠 SHARING LEARNING TO SWARM BRAIN")
    print(f"   Agent: {args.agent}")
    print(f"   Title: {args.title}")
    
    # Read content from file if provided
    content = args.content
    if args.file:
        content = Path(args.file).read_text(encoding='utf-8')
        print(f"   Content: From file {args.file}")
    else:
        print(f"   Content: {len(content)} characters")
    
    # Parse tags
    tags = [tag.strip() for tag in args.tags.split(',')] if args.tags else []
    print(f"   Tags: {', '.join(tags)}")
    
    # Share to Swarm Brain
    try:
        memory.share_learning(
            title=args.title,
            content=content,
            tags=tags
        )
        print(f"\n✅ LEARNING SHARED TO SWARM BRAIN!")
        print(f"   Other agents can now search and find this knowledge!")
    except Exception as e:
        print(f"\n❌ Failed to share learning: {e}")
        sys.exit(1)


def record_decision(args):
    """Record a decision to Swarm Brain."""
    memory = SwarmMemory(agent_id=args.agent)
    
    print(f"\n🧠 RECORDING DECISION TO SWARM BRAIN")
    print(f"   Title: {args.title}")
    
    participants = [p.strip() for p in args.participants.split(',')] if args.participants else [args.agent]
    
    try:
        memory.record_decision(
            title=args.title,
            decision=args.decision,
            rationale=args.rationale,
            participants=participants
        )
        print(f"\n✅ DECISION RECORDED!")
    except Exception as e:
        print(f"\n❌ Failed to record decision: {e}")
        sys.exit(1)


def search_knowledge(args):
    """Search Swarm Brain knowledge."""
    memory = SwarmMemory(agent_id=args.agent)
    
    print(f"\n🔍 SEARCHING SWARM BRAIN FOR: '{args.query}'")
    
    try:
        results = memory.search_swarm_knowledge(args.query)
        
        if not results:
            print(f"\n❌ No results found for '{args.query}'")
            return
        
        print(f"\n✅ FOUND {len(results)} RESULTS:\n")
        
        for i, result in enumerate(results[:args.limit], 1):
            print(f"{i}. {result.get('title', 'No title')}")
            if 'author' in result:
                print(f"   By: {result['author']}")
            if 'tags' in result:
                print(f"   Tags: {', '.join(result['tags'])}")
            if args.verbose and 'content' in result:
                preview = result['content'][:200]
                print(f"   Preview: {preview}...")
            print()
            
    except Exception as e:
        print(f"\n❌ Search failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Swarm Brain CLI - Easy knowledge sharing and search",
        epilog="Examples:\n"
               "  Share: python tools/swarm_brain_cli.py share --agent Agent-8 --title 'My Learning' --content 'Details...'\n"
               "  Search: python tools/swarm_brain_cli.py search --agent Agent-8 --query 'repository analysis'\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Share command
    share_parser = subparsers.add_parser('share', help='Share a learning')
    share_parser.add_argument('--agent', required=True, help='Your agent ID (e.g., Agent-8)')
    share_parser.add_argument('--title', required=True, help='Learning title')
    share_parser.add_argument('--content', help='Learning content (or use --file)')
    share_parser.add_argument('--file', type=Path, help='Read content from file')
    share_parser.add_argument('--tags', help='Comma-separated tags (e.g., "pattern,roi,analysis")')
    
    # Decision command
    decision_parser = subparsers.add_parser('decision', help='Record a decision')
    decision_parser.add_argument('--agent', required=True, help='Your agent ID')
    decision_parser.add_argument('--title', required=True, help='Decision title')
    decision_parser.add_argument('--decision', required=True, help='The decision made')
    decision_parser.add_argument('--rationale', required=True, help='Why this decision')
    decision_parser.add_argument('--participants', help='Comma-separated agent IDs')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search Swarm Brain')
    search_parser.add_argument('--agent', required=True, help='Your agent ID')
    search_parser.add_argument('--query', required=True, help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Max results (default: 10)')
    search_parser.add_argument('--verbose', action='store_true', help='Show content previews')
    
    args = parser.parse_args()
    
    if args.command == 'share':
        if not args.content and not args.file:
            print("❌ Must provide --content or --file!")
            sys.exit(1)
        share_learning(args)
    elif args.command == 'decision':
        record_decision(args)
    elif args.command == 'search':
        search_knowledge(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()


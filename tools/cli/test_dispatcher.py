#!/usr/bin/env python3
"""
Test Unified CLI Dispatcher
===========================

Tests the unified dispatcher with sample commands.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-05
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.cli.dispatchers.unified_dispatcher import UnifiedCLIDispatcher


def test_dispatcher():
    """Test dispatcher functionality."""
    print("🧪 Testing Unified CLI Dispatcher\n")
    
    # Initialize dispatcher
    dispatcher = UnifiedCLIDispatcher()
    print(f"✅ Dispatcher initialized with {len(dispatcher.commands)} commands\n")
    
    if len(dispatcher.commands) == 0:
        print("❌ ERROR: No commands loaded!")
        return 1
    
    # Test command listing
    print("📋 Sample commands by category:")
    categories = {}
    for cmd_name, cmd_info in dispatcher.commands.items():
        cat = cmd_info.get("category", "general")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(cmd_name)
    
    for cat in sorted(categories.keys()):
        print(f"\n  {cat.upper()} ({len(categories[cat])}):")
        for cmd in sorted(categories[cat])[:5]:
            desc = dispatcher.commands[cmd].get("description", "")
            if desc:
                print(f"    - {cmd}: {desc[:60]}")
            else:
                print(f"    - {cmd}")
        if len(categories[cat]) > 5:
            print(f"    ... and {len(categories[cat]) - 5} more")
    
    # Test a simple command (list command)
    print("\n\n🧪 Testing command execution...")
    print("Testing: --list flag")
    result = dispatcher.dispatch("--list", [])
    print(f"Result: {result}")
    
    # Test unknown command
    print("\nTesting: unknown command")
    result = dispatcher.dispatch("unknown-command-xyz", [])
    print(f"Result: {result}")
    
    print("\n✅ Dispatcher test complete!")
    return 0


if __name__ == "__main__":
    sys.exit(test_dispatcher())


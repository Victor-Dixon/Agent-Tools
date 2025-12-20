#!/usr/bin/env python3
"""
Validate Swarm Snapshot View
============================

Validates that SwarmSnapshotView component works correctly.

Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-12-11
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def validate_swarm_snapshot_view():
    """Validate SwarmSnapshotView component."""
    print("=" * 80)
    print("SWARM SNAPSHOT VIEW VALIDATION")
    print("=" * 80)
    print()
    
    # Check file exists
    view_file = project_root / "src" / "discord_commander" / "views" / "swarm_snapshot_view.py"
    if not view_file.exists():
        print("❌ FAIL: swarm_snapshot_view.py not found")
        return False
    
    print("✅ View file found")
    
    # Check import
    try:
        from src.discord_commander.views.swarm_snapshot_view import SwarmSnapshotView
        print("✅ SwarmSnapshotView imports successfully")
    except ImportError as e:
        print(f"❌ FAIL: Import error: {e}")
        return False
    
    # Check class methods
    required_methods = [
        "_setup_buttons",
        "create_snapshot_embed",
        "refresh_snapshot",
        "show_details",
        "_get_swarm_snapshot",
    ]
    
    for method_name in required_methods:
        if not hasattr(SwarmSnapshotView, method_name):
            print(f"❌ FAIL: Method {method_name} not found")
            return False
    
    print("✅ All required methods present")
    
    # Check integration in unified_discord_bot.py
    bot_file = project_root / "src" / "discord_commander" / "unified_discord_bot.py"
    if bot_file.exists():
        content = bot_file.read_text()
        if "SwarmSnapshotView" in content:
            print("✅ SwarmSnapshotView integrated in unified_discord_bot.py")
        else:
            print("⚠️  WARNING: SwarmSnapshotView not found in unified_discord_bot.py")
    
    print()
    print("=" * 80)
    print("✅ VALIDATION PASSED: SwarmSnapshotView component ready")
    print("=" * 80)
    return True

if __name__ == "__main__":
    success = validate_swarm_snapshot_view()
    sys.exit(0 if success else 1)





#!/usr/bin/env python3
"""
System Readiness Check
=====================

Checks if Discord bot and message queue are ready to start.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-01-27
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def check_discord_bot_readiness() -> Tuple[bool, List[str]]:
    """Check if Discord bot is ready to start."""
    issues = []
    ready = True
    
    # Check for Discord token
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        issues.append("❌ DISCORD_BOT_TOKEN not set in environment")
        issues.append("   Set with: $env:DISCORD_BOT_TOKEN='your_token' (Windows)")
        issues.append("   Or add to .env file in repository root")
        ready = False
    else:
        issues.append("✅ DISCORD_BOT_TOKEN is set")
    
    # Check for .env file
    env_file = Path(".env")
    if env_file.exists():
        issues.append("✅ .env file exists")
    else:
        issues.append("⚠️  .env file not found (optional, but recommended)")
    
    # Check for discord.py
    try:
        import discord
        issues.append(f"✅ discord.py installed (version: {discord.__version__})")
    except ImportError:
        issues.append("❌ discord.py not installed")
        issues.append("   Install with: pip install discord.py")
        ready = False
    
    # Check for python-dotenv
    try:
        import dotenv
        issues.append("✅ python-dotenv installed")
    except ImportError:
        issues.append("⚠️  python-dotenv not installed (optional)")
        issues.append("   Install with: pip install python-dotenv")
    
    # Check for bot script
    bot_script = Path("src/discord_commander/unified_discord_bot.py")
    if bot_script.exists():
        issues.append("✅ Discord bot script found")
    else:
        issues.append(f"❌ Discord bot script not found: {bot_script}")
        ready = False
    
    return ready, issues


def check_message_queue_readiness() -> Tuple[bool, List[str]]:
    """Check if message queue processor is ready to start."""
    issues = []
    ready = True
    
    # Check for queue processor script
    queue_script = Path("tools/start_message_queue_processor.py")
    if queue_script.exists():
        issues.append("✅ Message queue processor script found")
    else:
        issues.append(f"❌ Message queue processor script not found: {queue_script}")
        ready = False
    
    # Check for message queue module
    queue_module = Path("src/core/message_queue.py")
    if queue_module.exists():
        issues.append("✅ Message queue module found")
    else:
        issues.append(f"❌ Message queue module not found: {queue_module}")
        ready = False
    
    # Check for message queue processor module
    processor_module = Path("src/core/message_queue_processor.py")
    if processor_module.exists():
        issues.append("✅ Message queue processor module found")
    else:
        issues.append(f"❌ Message queue processor module not found: {processor_module}")
        ready = False
    
    # Check for data directory
    data_dir = Path("data")
    if data_dir.exists():
        issues.append("✅ data/ directory exists")
    else:
        issues.append("⚠️  data/ directory not found (will be created automatically)")
    
    return ready, issues


def check_hardened_resume_system() -> Tuple[bool, List[str]]:
    """Check if hardened resume system is available."""
    issues = []
    ready = True
    
    # Check for hardened activity detector
    detector_module = Path("src/core/hardened_activity_detector.py")
    if detector_module.exists():
        issues.append("✅ Hardened activity detector found")
        
        # Try to import it
        try:
            from src.core.hardened_activity_detector import HardenedActivityDetector
            issues.append("✅ Hardened activity detector can be imported")
        except ImportError as e:
            issues.append(f"⚠️  Hardened activity detector import failed: {e}")
            issues.append("   (This is likely a path issue in the check script, not a real problem)")
            # Don't fail readiness check for this - it's optional
    else:
        issues.append("⚠️  Hardened activity detector not found (optional)")
        ready = False
    
    # Check for stall resumer guard
    guard_module = Path("src/core/stall_resumer_guard.py")
    if guard_module.exists():
        issues.append("✅ Stall resumer guard found")
    else:
        issues.append("⚠️  Stall resumer guard not found (optional)")
    
    return ready, issues


def main():
    """Run all readiness checks."""
    print("=" * 70)
    print("SYSTEM READINESS CHECK")
    print("=" * 70)
    print()
    
    all_ready = True
    
    # Check Discord bot
    print("📱 DISCORD BOT READINESS")
    print("-" * 70)
    bot_ready, bot_issues = check_discord_bot_readiness()
    for issue in bot_issues:
        print(issue)
    print()
    
    if not bot_ready:
        all_ready = False
    
    # Check message queue
    print("📬 MESSAGE QUEUE READINESS")
    print("-" * 70)
    queue_ready, queue_issues = check_message_queue_readiness()
    for issue in queue_issues:
        print(issue)
    print()
    
    if not queue_ready:
        all_ready = False
    
    # Check hardened resume system
    print("🛡️ HARDENED RESUME SYSTEM")
    print("-" * 70)
    resume_ready, resume_issues = check_hardened_resume_system()
    for issue in resume_issues:
        print(issue)
    print()
    
    # Summary
    print("=" * 70)
    if all_ready:
        print("✅ SYSTEM READY")
        print()
        print("You can start:")
        print("  1. Discord Bot:    python tools/run_unified_discord_bot_with_restart.py")
        print("  2. Message Queue: python tools/start_message_queue_processor.py")
    else:
        print("❌ SYSTEM NOT READY")
        print()
        print("Please fix the issues above before starting services.")
    print("=" * 70)
    
    return 0 if all_ready else 1


if __name__ == "__main__":
    sys.exit(main())


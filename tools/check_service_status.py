#!/usr/bin/env python3
"""
Check Service Status - Message Queue, Twitch Bot, Discord Bot
============================================================

Checks if critical services are running:
- Message Queue Processor
- Twitch Bot
- Discord Bot

Author: Agent-2
V2 Compliant: <300 lines
"""

from dotenv import load_dotenv
import os
import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

load_dotenv()


def check_process_running(process_name):
    """Check if a process is running (Windows)."""
    try:
        result = subprocess.run(
            ['tasklist', '/FI', f'IMAGENAME eq {process_name}', '/FO', 'CSV'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return process_name.lower() in result.stdout.lower()
    except Exception:
        return False


def check_python_process(pattern):
    """Check if a Python process matching pattern is running."""
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Check if pattern appears in process list
        # Note: This is a simple check - full implementation would parse CSV
        return pattern.lower() in result.stdout.lower()
    except Exception:
        return False


def check_message_queue():
    """Check message queue processor status."""
    print("📬 MESSAGE QUEUE PROCESSOR")
    print("=" * 60)

    # Check if process is running
    queue_running = check_python_process("message_queue_processor")

    if queue_running:
        print("✅ Status: RUNNING (process detected)")
    else:
        print("❌ Status: NOT RUNNING")
        print("   To start: python tools/start_message_queue_processor.py")

    print()


def check_twitch_bot():
    """Check Twitch bot status."""
    print("📺 TWITCH BOT")
    print("=" * 60)

    # Check configuration
    channel = os.getenv("TWITCH_CHANNEL", "").strip()
    token = os.getenv("TWITCH_ACCESS_TOKEN", "").strip()

    print(f"   Channel: {channel if channel else 'NOT SET'}")
    print(f"   Token: {'SET' if token else 'NOT SET'}")

    # Check if process is running
    twitch_running = check_python_process(
        "twitch") or check_python_process("START_CHAT_BOT")

    if twitch_running:
        print("✅ Status: RUNNING (process detected)")
    else:
        print("❌ Status: NOT RUNNING")
        print("   To start: Check tools/START_CHAT_BOT_NOW.py or QUICK_START_TWITCH_BOT.md")

    print("   To verify: Check Twitch chat for bot messages or run: python tools/check_twitch_bot_live_status.py")
    print()


def check_discord_bot():
    """Check Discord bot status."""
    print("💬 DISCORD BOT")
    print("=" * 60)

    # Check configuration
    discord_token = os.getenv("DISCORD_BOT_TOKEN", "").strip()

    print(f"   Token: {'SET' if discord_token else 'NOT SET'}")

    # Check if process is running
    discord_running = check_python_process(
        "discord") or check_python_process("unified_discord_bot")

    if discord_running:
        print("✅ Status: RUNNING (process detected)")
    else:
        print("❌ Status: NOT RUNNING")
        print("   To start: Check src/discord_commander/lifecycle/bot_lifecycle.py")
        print("   Or: Check temp_repos/Thea/start_discord_bot.py")

    print()


def main():
    """Main execution."""
    print("\n🔍 SERVICE STATUS CHECK")
    print("=" * 60)
    print()

    check_message_queue()
    check_twitch_bot()
    check_discord_bot()

    print("=" * 60)
    print("💡 Note: Process detection may not be 100% accurate.")
    print("   For definitive status, check logs or test functionality directly.")
    print()


if __name__ == "__main__":
    main()





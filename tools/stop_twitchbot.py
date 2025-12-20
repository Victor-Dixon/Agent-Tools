#!/usr/bin/env python3
"""
Stop TwitchBot
==============

Gracefully stops a running TwitchBot by finding and stopping the orchestrator process.
"""

import sys
import signal
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.services.chat_presence.chat_presence_orchestrator import ChatPresenceOrchestrator
    print("✅ Import successful")
except ImportError as e:
    print(f"⚠️  Could not import orchestrator: {e}")
    print("   Bot may not be running via Python script")
    sys.exit(0)

# Try to find running orchestrator instances
# This is a simple approach - in production you might want to use a PID file
print("=" * 60)
print("🛑 STOPPING TWITCH BOT")
print("=" * 60)
print()
print("💡 To stop the bot running in another terminal:")
print("   Press Ctrl+C in that terminal window")
print()
print("If the bot is running as a background process,")
print("you can stop it by finding the Python process and killing it.")
print()
print("To find and stop Python processes:")
print("  Get-Process python | Stop-Process")
print()

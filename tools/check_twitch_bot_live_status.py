#!/usr/bin/env python3
"""
Check Twitch Bot Live Status
============================

Checks if the bot is actually connected and receiving messages.

<!-- SSOT Domain: infrastructure -->

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-03
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()


def check_connection_test():
    """Test if we can verify connection status."""
    print("=" * 60)
    print("🔍 TWITCH BOT LIVE STATUS CHECK")
    print("=" * 60)
    print()
    
    # Check configuration
    channel = os.getenv("TWITCH_CHANNEL", "").strip()
    token = os.getenv("TWITCH_ACCESS_TOKEN", "").strip()
    
    print("📋 Configuration:")
    print(f"   Channel: {channel}")
    print(f"   Token: {'SET' if token else 'NOT SET'} ({len(token)} chars)")
    print()
    
    # Extract channel name
    if "twitch.tv/" in channel.lower():
        parts = [p for p in channel.split("/") if p.strip()]
        channel = parts[-1].strip() if parts else channel
        channel = channel.rstrip("/").strip()
    
    print(f"✅ Extracted channel: {channel}")
    print()
    
    print("🔍 Connection Status:")
    print("   To verify the bot is working:")
    print("   1. Check your Twitch chat - bot should have sent an online message")
    print("   2. Try sending: !status")
    print("   3. Check terminal output for debug messages")
    print()
    
    print("📊 Expected Debug Output:")
    print("   ✅ DEBUG: Connected to Twitch IRC")
    print("   📺 DEBUG: Joined #digital_dreamscape")
    print("   📢 DEBUG: Sent online message to chat")
    print("   🔍 DEBUG: on_pubmsg called - (when you send a message)")
    print()
    
    print("🐛 Troubleshooting:")
    print("   If you don't see debug messages:")
    print("   1. Check if bot process is running")
    print("   2. Verify OAuth token is valid (not expired)")
    print("   3. Check if channel name matches exactly")
    print("   4. Verify bot account has permission to join channel")
    print()
    
    print("💡 Quick Test:")
    print("   Send this in your Twitch chat:")
    print("   !status")
    print()
    print("   You should see debug output in the terminal showing:")
    print("   - Message received")
    print("   - Handler called")
    print("   - Response sent")


if __name__ == "__main__":
    check_connection_test()


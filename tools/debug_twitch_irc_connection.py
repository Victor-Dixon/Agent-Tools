#!/usr/bin/env python3
"""
Debug Twitch IRC Connection
============================

Monitors IRC connection events to diagnose why bot isn't connecting.
"""

import sys
import asyncio
import time
import threading
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

import os
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def debug_connection():
    """Debug IRC connection with detailed monitoring."""
    print("=" * 60)
    print("🔍 DEBUGGING TWITCH IRC CONNECTION")
    print("=" * 60)
    print()
    
    from src.services.chat_presence.twitch_bridge import TwitchChatBridge
    
    access_token = os.getenv("TWITCH_ACCESS_TOKEN")
    channel = os.getenv("TWITCH_CHANNEL", "").strip()
    
    if "twitch.tv/" in channel.lower():
        parts = [p for p in channel.split("/") if p.strip()]
        channel = parts[-1].strip().rstrip("/")
        if channel.startswith("#"):
            channel = channel[1:]
    
    oauth_token = access_token if access_token.startswith("oauth:") else f"oauth:{access_token}"
    
    print(f"📋 Configuration:")
    print(f"   Channel: {channel}")
    print(f"   Token: {oauth_token[:25]}...")
    print()
    
    # Create bridge with message callback to see events
    connection_events = []
    
    def on_message(message_data):
        """Capture messages."""
        connection_events.append(("message", message_data))
        print(f"📨 Message received: {message_data.get('message', '')[:50]}")
    
    bridge = TwitchChatBridge(
        username=channel,
        oauth_token=oauth_token,
        channel=channel,
        on_message=on_message,
    )
    
    print("🔌 Starting connection...")
    result = await bridge.connect()
    
    if not result:
        print("❌ Connection failed immediately")
        return
    
    print(f"✅ Connection attempt returned: {result}")
    print(f"   Running: {bridge.running}")
    print(f"   Connected: {bridge.connected}")
    print()
    
    # Monitor connection for 10 seconds
    print("⏳ Monitoring connection for 10 seconds...")
    print("   (Watch for: on_welcome, on_join, on_error, on_disconnect)")
    print()
    
    for i in range(10):
        await asyncio.sleep(1)
        if bridge.bot and hasattr(bridge.bot, 'connection'):
            try:
                if hasattr(bridge.bot.connection, 'connected'):
                    connected = bridge.bot.connection.connected
                    print(f"   [{i+1}s] IRC connection.connected: {connected}")
                else:
                    print(f"   [{i+1}s] IRC connection object exists but no 'connected' attribute")
            except Exception as e:
                print(f"   [{i+1}s] Error checking connection: {e}")
        
        if bridge.connected:
            print(f"\n✅ CONNECTED! Bot joined channel at {i+1} seconds")
            break
    
    print()
    print("=" * 60)
    print("📊 FINAL STATUS")
    print("=" * 60)
    print(f"   Bridge Running: {bridge.running}")
    print(f"   Bridge Connected: {bridge.connected}")
    
    if bridge.bot:
        print(f"   Bot exists: True")
        if hasattr(bridge.bot, 'connection'):
            print(f"   Bot connection exists: True")
            try:
                if hasattr(bridge.bot.connection, 'connected'):
                    print(f"   IRC connection.connected: {bridge.bot.connection.connected}")
                else:
                    print(f"   IRC connection.connected: Attribute not found")
            except Exception as e:
                print(f"   Error checking IRC connection: {e}")
        else:
            print(f"   Bot connection: Not found")
    else:
        print(f"   Bot exists: False")
    
    print()
    
    if not bridge.connected:
        print("❌ DIAGNOSIS: Bot is not connected")
        print()
        print("Possible causes:")
        print("1. OAuth token invalid/expired")
        print("   → Check token at: https://twitchapps.com/tmi/")
        print("   → Regenerate if needed")
        print()
        print("2. Channel name mismatch")
        print(f"   → Current: {channel}")
        print("   → Verify exact channel name (case-sensitive)")
        print()
        print("3. Bot account permissions")
        print("   → Bot account must have permission to join channel")
        print("   → Check if bot account is banned/blocked")
        print()
        print("4. IRC connection issue")
        print("   → Check network/firewall")
        print("   → Verify irc.chat.twitch.tv:6667 is accessible")
        print()
        print("5. Check terminal output for IRC errors")
        print("   → Look for 'on_error', 'on_disconnect', 'on_notice' messages")
        print("   → Check for authentication errors")
    
    return bridge.connected

if __name__ == "__main__":
    result = asyncio.run(debug_connection())
    sys.exit(0 if result else 1)


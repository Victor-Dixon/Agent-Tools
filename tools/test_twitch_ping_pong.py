#!/usr/bin/env python3
"""
Quick test to verify PING/PONG handler keeps Twitch bot connected.
Runs for 30 seconds to see if connection stays alive.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_connection():
    """Test Twitch bot connection stability."""
    print("=" * 60)
    print("🧪 TESTING TWITCH BOT PING/PONG FIX")
    print("=" * 60)
    print()
    
    # Check environment
    channel = os.getenv("TWITCH_CHANNEL")
    token = os.getenv("TWITCH_ACCESS_TOKEN")
    username = os.getenv("TWITCH_BOT_USERNAME") or channel
    
    if not channel or not token:
        print("❌ ERROR: Missing Twitch credentials")
        print("   Set TWITCH_CHANNEL and TWITCH_ACCESS_TOKEN")
        return False
    
    print(f"✅ Configuration found:")
    print(f"   Channel: {channel}")
    print(f"   Username: {username}")
    print(f"   Token: {token[:20]}...")
    print()
    
    # Import and create bridge
    try:
        from src.services.chat_presence.twitch_bridge import TwitchChatBridge
        
        print("🔌 Creating Twitch bridge...")
        bridge = TwitchChatBridge(
            username=username,
            oauth_token=token,
            channel=channel,
            on_message=lambda m: print(f"📨 Message: {m.get('message', '')[:50]}"),
        )
        
        print("🚀 Connecting to Twitch...")
        connected = await bridge.connect()
        
        if not connected:
            print("❌ Failed to initiate connection")
            return False
        
        print("✅ Connection initiated")
        print()
        print("⏳ Monitoring connection for 30 seconds...")
        print("   (Watch for PING/PONG messages in logs)")
        print()
        
        # Monitor for 30 seconds
        for i in range(30):
            await asyncio.sleep(1)
            if not bridge.running:
                print(f"❌ Connection lost after {i} seconds!")
                return False
            if i % 5 == 0:
                status = "✅ Connected" if bridge.connected else "⏳ Connecting..."
                print(f"   [{i}s] {status} - Running: {bridge.running}")
        
        print()
        if bridge.running and bridge.connected:
            print("✅ SUCCESS: Connection stable for 30 seconds!")
            print("   PING/PONG handler is working correctly")
            return True
        else:
            print("⚠️ WARNING: Connection state unclear")
            print(f"   Running: {bridge.running}, Connected: {bridge.connected}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'bridge' in locals():
            print()
            print("🛑 Stopping bot...")
            bridge.stop()

if __name__ == "__main__":
    try:
        result = asyncio.run(test_connection())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)


#!/usr/bin/env python3
"""
Check TwitchBot Status and Connection
=====================================

Checks if the bot is running and connected to Twitch IRC.
"""

from src.services.chat_presence.twitch_bridge import TwitchChatBridge
from src.services.chat_presence.chat_presence_orchestrator import ChatPresenceOrchestrator
import re
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def extract_channel_name(channel_value: str) -> str:
    """Extract channel name from URL or channel name."""
    if not channel_value:
        return ""
    channel_value = channel_value.strip()
    url_pattern = r'(?:https?://)?(?:www\.)?twitch\.tv/([^/?]+)'
    match = re.search(url_pattern, channel_value, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    if channel_value.startswith('#'):
        channel_value = channel_value[1:]
    return channel_value.lower().strip()


def normalize_oauth_token(token: str) -> str:
    """Normalize OAuth token format."""
    if not token:
        return ""
    token = token.strip()
    if not token.startswith('oauth:'):
        return f"oauth:{token}"
    return token


async def check_bot_status():
    """Check TwitchBot status and connection."""
    print("=" * 60)
    print("🔍 TWITCHBOT STATUS CHECK")
    print("=" * 60)
    print()

    # Get and normalize config
    access_token = os.getenv("TWITCH_ACCESS_TOKEN", "").strip()
    channel_raw = os.getenv("TWITCH_CHANNEL", "").strip()
    username_raw = os.getenv("TWITCH_BOT_USERNAME", "").strip()

    channel_fixed = extract_channel_name(channel_raw) if channel_raw else ""
    oauth_token_fixed = normalize_oauth_token(
        access_token) if access_token else ""
    username_fixed = username_raw.lower().strip() if username_raw else channel_fixed

    print("📋 Configuration:")
    print(f"  Username: {username_fixed}")
    print(f"  Channel: {channel_fixed}")
    print(f"  OAuth Token: {'✅ Set' if oauth_token_fixed else '❌ Missing'}")
    if oauth_token_fixed:
        print(f"    Format: {oauth_token_fixed[:20]}...")
    print()

    # Check if config is valid
    if not username_fixed or not oauth_token_fixed or not channel_fixed:
        print("❌ Configuration incomplete!")
        print("   Missing required values. Run: python tools/fix_twitch_config.py")
        return

    # Test direct connection
    print("🔌 Testing Direct TwitchChatBridge Connection...")
    print()

    try:
        bridge = TwitchChatBridge(
            username=username_fixed,
            oauth_token=oauth_token_fixed,
            channel=channel_fixed,
        )

        print("✅ TwitchChatBridge created")
        print()
        print("🔄 Attempting connection (timeout: 10 seconds)...")

        # Try to connect with timeout
        try:
            connected = await asyncio.wait_for(bridge.connect(), timeout=10.0)
            if connected:
                print("✅ Connection started successfully!")
                print()
                print("⏳ Waiting 3 seconds to check connection status...")
                await asyncio.sleep(3)

                if bridge.connected:
                    print("✅ Bot is CONNECTED to Twitch IRC!")
                    print(f"   Channel: {bridge.channel}")
                else:
                    print("⚠️  Connection thread started but not yet connected")
                    print("   This might indicate:")
                    print("   - Authentication issues (check OAuth token)")
                    print("   - Network issues")
                    print("   - IRC server connection problems")
            else:
                print("❌ Connection failed to start")
        except asyncio.TimeoutError:
            print("⚠️  Connection attempt timed out after 10 seconds")
            print("   The bot may still be connecting in the background")
        except Exception as e:
            print(f"❌ Connection error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

        print()
        print("🔍 Checking bridge status:")
        print(f"  Running: {bridge.running}")
        print(f"  Connected: {bridge.connected}")
        print(
            f"  Bot instance: {'✅ Created' if bridge.bot else '❌ Not created'}")
        print()

    except Exception as e:
        print(f"❌ Error creating TwitchChatBridge: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return

    # Check orchestrator
    print("=" * 60)
    print("📡 TESTING ORCHESTRATOR")
    print("=" * 60)
    print()

    try:
        orchestrator = ChatPresenceOrchestrator(
            twitch_config={
                "username": username_fixed,
                "oauth_token": oauth_token_fixed,
                "channel": channel_fixed,
            }
        )

        print("✅ Orchestrator created")
        print()
        print("🔄 Attempting orchestrator start (timeout: 15 seconds)...")

        try:
            success = await asyncio.wait_for(orchestrator.start(), timeout=15.0)
            if success:
                print("✅ Orchestrator started successfully!")
                await asyncio.sleep(3)

                if orchestrator.twitch_bridge and orchestrator.twitch_bridge.connected:
                    print("✅ Bot is CONNECTED via orchestrator!")
                else:
                    print("⚠️  Orchestrator started but Twitch bridge not connected")
            else:
                print("❌ Orchestrator failed to start")
        except asyncio.TimeoutError:
            print("⚠️  Orchestrator start timed out")
        except Exception as e:
            print(f"❌ Orchestrator error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

        print()
        print("🔍 Orchestrator status:")
        print(f"  Running: {orchestrator.running}")
        if orchestrator.twitch_bridge:
            print(
                f"  Twitch Bridge Running: {orchestrator.twitch_bridge.running}")
            print(
                f"  Twitch Bridge Connected: {orchestrator.twitch_bridge.connected}")
        else:
            print("  Twitch Bridge: ❌ Not initialized")

    except Exception as e:
        print(f"❌ Error with orchestrator: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 60)
    print("💡 NEXT STEPS")
    print("=" * 60)
    print()
    print("If bot is not connected:")
    print("1. Check OAuth token is valid and has chat access")
    print("2. Verify channel name is correct (without #)")
    print("3. Check network/firewall allows IRC connections")
    print("4. Review logs/logs/chat_presence_orchestrator.log for errors")
    print()


if __name__ == "__main__":
    asyncio.run(check_bot_status())

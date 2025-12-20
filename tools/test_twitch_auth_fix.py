#!/usr/bin/env python3
"""
Test Twitch Auth Fix
====================

Tests the fixed authentication method with password in server_list.
"""

from src.services.chat_presence.twitch_bridge import TwitchChatBridge
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


async def test_auth_fix():
    """Test the authentication fix."""
    print("=" * 60)
    print("🔧 TESTING TWITCH AUTH FIX")
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

    print(f"Username: {username_fixed}")
    print(f"Channel: {channel_fixed}")
    print(f"OAuth Token: {oauth_token_fixed[:25]}...")
    print()

    if not username_fixed or not oauth_token_fixed or not channel_fixed:
        print("❌ Configuration incomplete!")
        return

    print("🔄 Creating TwitchChatBridge with FIXED authentication...")
    print("   (Password now passed via server_list tuple)")
    print()

    try:
        bridge = TwitchChatBridge(
            username=username_fixed,
            oauth_token=oauth_token_fixed,
            channel=channel_fixed,
        )

        print("✅ TwitchChatBridge created")
        print()
        print("🔄 Attempting connection (timeout: 15 seconds)...")
        print("   Watch for: 'on_welcome' event (means auth succeeded!)")
        print()

        try:
            connected = await asyncio.wait_for(bridge.connect(), timeout=15.0)
            if connected:
                print("✅ Connection started!")
                print()
                print("⏳ Waiting 5 seconds to check if 'on_welcome' was called...")
                await asyncio.sleep(5)

                if bridge.connected:
                    print("✅✅✅ SUCCESS! Bot is CONNECTED and JOINED channel!")
                    print("   This means authentication worked!")
                else:
                    print("⚠️  Connection thread started but not yet connected")
                    print(
                        "   Check logs for 'on_welcome' or 'Improperly formatted auth' messages")
            else:
                print("❌ Connection failed to start")
        except asyncio.TimeoutError:
            print("⚠️  Connection attempt timed out after 15 seconds")
        except Exception as e:
            print(f"❌ Connection error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 60)
    print("💡 WHAT TO CHECK")
    print("=" * 60)
    print()
    print("In the logs, look for:")
    print("✅ 'on_welcome called' = Authentication SUCCESS!")
    print("❌ 'Improperly formatted auth' = Still has auth issues")
    print()
    print("If you see 'on_welcome', the bot should connect!")
    print()


if __name__ == "__main__":
    asyncio.run(test_auth_fix())

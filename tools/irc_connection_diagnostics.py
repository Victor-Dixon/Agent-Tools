#!/usr/bin/env python3
"""
IRC Connection Diagnostics Tool
================================

Real-time IRC protocol message viewer for debugging TwitchBot connections.
Shows all IRC protocol messages (PASS, NICK, USER, CAP, etc.) in real-time.

Usage:
    python tools/irc_connection_diagnostics.py
"""

from src.services.chat_presence.twitch_bridge import TwitchChatBridge
import re
import logging
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


# Configure detailed IRC logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


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


async def main():
    """Run IRC connection diagnostics."""
    print("=" * 60)
    print("🔍 IRC CONNECTION DIAGNOSTICS")
    print("=" * 60)
    print()

    # Get config
    access_token = os.getenv("TWITCH_ACCESS_TOKEN", "").strip()
    channel_raw = os.getenv("TWITCH_CHANNEL", "").strip()
    username_raw = os.getenv("TWITCH_BOT_USERNAME", "").strip()

    channel_fixed = extract_channel_name(channel_raw) if channel_raw else ""
    oauth_token_fixed = normalize_oauth_token(
        access_token) if access_token else ""
    username_fixed = username_raw.lower().strip() if username_raw else channel_fixed

    print(f"Configuration:")
    print(f"  Username: {username_fixed}")
    print(f"  Channel: {channel_fixed}")
    print(f"  OAuth Token: {'✅ Set' if oauth_token_fixed else '❌ Missing'}")
    print()
    print("🔍 Monitoring IRC protocol messages in real-time...")
    print("   (Watch for PASS, NICK, USER, CAP, JOIN messages)")
    print("   Press Ctrl+C to stop")
    print()

    if not username_fixed or not oauth_token_fixed or not channel_fixed:
        print("❌ Configuration incomplete!")
        return

    try:
        bridge = TwitchChatBridge(
            username=username_fixed,
            oauth_token=oauth_token_fixed,
            channel=channel_fixed,
        )

        await bridge.connect()

        # Keep running to see protocol messages
        print("✅ Connection started. Monitoring protocol messages...")
        print()

        # Wait for user interrupt
        try:
            await asyncio.sleep(30)  # Run for 30 seconds or until interrupted
        except KeyboardInterrupt:
            print("\n🛑 Stopping diagnostics...")

        bridge.stop()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())

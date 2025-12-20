#!/usr/bin/env python3
"""
Start Twitch Bot with Configuration Fixes
==========================================

Applies configuration fixes and starts the Twitch bot with debugging enabled.
This script normalizes configuration values before starting the bot.

Usage:
    python tools/start_twitchbot_with_fixes.py
"""

import asyncio
import os
import re
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

# Import normalization functions from fix_twitch_config


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


def apply_config_fixes():
    """Apply configuration fixes to environment variables."""
    # Get raw values
    access_token = os.getenv("TWITCH_ACCESS_TOKEN", "").strip()
    channel_raw = os.getenv("TWITCH_CHANNEL", "").strip()
    username_raw = os.getenv("TWITCH_BOT_USERNAME", "").strip()

    # Apply fixes
    channel_fixed = extract_channel_name(channel_raw) if channel_raw else ""
    oauth_token_fixed = normalize_oauth_token(
        access_token) if access_token else ""
    username_fixed = username_raw.lower().strip() if username_raw else channel_fixed

    # Update environment variables in this process
    if channel_fixed and channel_fixed != channel_raw:
        os.environ["TWITCH_CHANNEL"] = channel_fixed
        print(f"✅ Fixed TWITCH_CHANNEL: '{channel_raw}' → '{channel_fixed}'")

    if oauth_token_fixed and oauth_token_fixed != access_token:
        os.environ["TWITCH_ACCESS_TOKEN"] = oauth_token_fixed
        print(f"✅ Fixed TWITCH_ACCESS_TOKEN: Added 'oauth:' prefix")

    if username_fixed and (not username_raw or username_fixed != username_raw.lower().strip()):
        os.environ["TWITCH_BOT_USERNAME"] = username_fixed
        if not username_raw:
            print(
                f"✅ Set TWITCH_BOT_USERNAME: '{username_fixed}' (from channel)")
        else:
            print(
                f"✅ Fixed TWITCH_BOT_USERNAME: '{username_raw}' → '{username_fixed}'")

    return {
        "username": username_fixed,
        "oauth_token": oauth_token_fixed,
        "channel": channel_fixed,
    }


async def main():
    """Main entry point."""
    print("=" * 60)
    print("🚀 STARTING TWITCH BOT WITH CONFIGURATION FIXES")
    print("=" * 60)
    print()

    # Apply configuration fixes
    print("🔧 Applying configuration fixes...")
    print()
    config = apply_config_fixes()
    print()

    # Validate configuration
    if not config["username"] or not config["oauth_token"] or not config["channel"]:
        print("❌ Configuration incomplete after fixes")
        print()
        print("Required environment variables:")
        print("  - TWITCH_ACCESS_TOKEN (OAuth token)")
        print("  - TWITCH_CHANNEL (channel name or URL)")
        print("  - TWITCH_BOT_USERNAME (optional, defaults to channel)")
        print()
        sys.exit(1)

    print("✅ Configuration validated!")
    print()
    print(f"  Username: {config['username']}")
    print(f"  Channel: {config['channel']}")
    print(f"  Token: {config['oauth_token'][:15]}...")
    print()

    # Import after fixes applied
    try:
        from src.services.chat_presence import ChatPresenceOrchestrator
        import logging

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

        print("=" * 60)
        print("🔌 Connecting to Twitch...")
        print("=" * 60)
        print()

        # Create orchestrator with fixed config
        orchestrator = ChatPresenceOrchestrator(
            twitch_config=config,
            obs_config=None,  # Disable OBS for now
        )

        # Start system
        success = await orchestrator.start()

        if not success:
            print()
            print("❌ Failed to start chat bot")
            print()
            print("Common issues:")
            print("  - Invalid OAuth token (check at https://twitchapps.com/tmi/)")
            print("  - Token expired")
            print("  - Network connectivity issues")
            print("  - Channel name mismatch")
            return

        print()
        print("=" * 60)
        print("✅ TWITCH BOT IS LIVE!")
        print("=" * 60)
        print()
        print("The swarm is now active in your Twitch chat!")
        print()
        print("Test commands in chat:")
        print("  !agent7 hello - Agent-7 responds")
        print("  !team status - All agents respond")
        print("  !swarm hello - Broadcast message")
        print()
        print("Press Ctrl+C to stop")
        print()

        try:
            # Keep running
            while orchestrator.running:
                await asyncio.sleep(1)

        except KeyboardInterrupt:
            print()
            print("🛑 Shutting down...")
            await orchestrator.stop()
            print("✅ Shutdown complete")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print()
        print("Make sure all dependencies are installed:")
        print("  pip install irc python-dotenv")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

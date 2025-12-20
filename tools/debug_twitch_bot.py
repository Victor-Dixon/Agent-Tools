#!/usr/bin/env python3
"""
Debug Twitch Bot - Check Configuration and Start with Debugging
==============================================================

Shows actual configuration values and attempts to start the bot
with detailed error messages.

Usage:
    python tools/debug_twitch_bot.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load .env
try:
    from dotenv import load_dotenv, dotenv_values
    env_vars = dotenv_values(".env")
    for key, value in env_vars.items():
        if value and key not in os.environ:
            os.environ[key] = value
    load_dotenv()
except ImportError:
    pass

from src.services.chat_presence import ChatPresenceOrchestrator
import logging

logging.basicConfig(
    level=logging.DEBUG,  # DEBUG level for detailed logs
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def extract_channel_name(channel_value: str) -> str:
    """Extract channel name from URL or channel name."""
    import re
    if not channel_value:
        return ""
    channel_value = channel_value.strip()
    # Extract from URL if present
    url_pattern = r'(?:https?://)?(?:www\.)?twitch\.tv/([^/?]+)'
    match = re.search(url_pattern, channel_value, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    # Remove # prefix if present
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


def show_config():
    """Show current Twitch configuration (masked for security)."""
    print("=" * 60)
    print("🔍 TWITCH CONFIGURATION DEBUG")
    print("=" * 60)
    print()
    
    # Check all possible config sources
    access_token = os.getenv("TWITCH_ACCESS_TOKEN")
    channel_raw = os.getenv("TWITCH_CHANNEL")
    username_raw = os.getenv("TWITCH_BOT_USERNAME")
    swarm_voice = os.getenv("TWITCH_SWARM_VOICE")
    
    print("Environment Variables (Raw):")
    print(f"  TWITCH_ACCESS_TOKEN: {'✅ Set' if access_token else '❌ Not set'}")
    if access_token:
        masked = access_token[:10] + "..." if len(access_token) > 10 else "***"
        print(f"    Value: {masked}")
    
    print(f"  TWITCH_CHANNEL: {'✅ Set' if channel_raw else '❌ Not set'}")
    if channel_raw:
        print(f"    Value: {channel_raw}")
    
    print(f"  TWITCH_BOT_USERNAME: {'✅ Set' if username_raw else '❌ Not set'}")
    if username_raw:
        print(f"    Value: {username_raw}")
    
    print(f"  TWITCH_SWARM_VOICE: {'✅ Set' if swarm_voice else '❌ Not set'}")
    if swarm_voice:
        parts = swarm_voice.split("|")
        print(f"    Parts: {len(parts)}")
        if len(parts) >= 1:
            print(f"    Part 1 (username): {parts[0][:10]}...")
        if len(parts) >= 2:
            masked_token = parts[1][:15] + "..." if len(parts[1]) > 15 else "***"
            print(f"    Part 2 (token): {masked_token}")
        if len(parts) >= 3:
            print(f"    Part 3 (channel): {parts[2]}")
        else:
            print(f"    ⚠️  Missing channel (need 3 parts: username|token|channel)")
    
    print()
    
    # Normalize values
    channel = extract_channel_name(channel_raw) if channel_raw else None
    oauth_token = normalize_oauth_token(access_token) if access_token else None
    username = username_raw.lower().strip() if username_raw else (channel if channel else None)
    
    # Determine what config we can build
    twitch_config = None
    
    if oauth_token and channel:
        twitch_config = {
            "username": username,
            "oauth_token": oauth_token,
            "channel": channel,
        }
        print("✅ Configuration Method: TWITCH_ACCESS_TOKEN + TWITCH_CHANNEL")
        if channel_raw != channel:
            print(f"   📝 Channel normalized: '{channel_raw}' → '{channel}'")
        if access_token != oauth_token:
            print(f"   📝 OAuth token normalized: Added 'oauth:' prefix")
    elif swarm_voice:
        parts = swarm_voice.split("|")
        if len(parts) == 3:
            username, oauth_token, channel = [p.strip() for p in parts]
            twitch_config = {
                "username": username,
                "oauth_token": oauth_token,
                "channel": channel,
            }
            print("✅ Configuration Method: TWITCH_SWARM_VOICE (3 parts)")
        else:
            print(f"❌ Configuration Method: TWITCH_SWARM_VOICE incomplete ({len(parts)}/3 parts)")
            if len(parts) == 1:
                print("   ⚠️  Only 1 part found - might be just a token")
                print("   💡 Add channel: TWITCH_CHANNEL=your_channel_name")
            elif len(parts) == 2:
                print("   ⚠️  Only 2 parts found - missing channel")
                print("   💡 Format should be: username|token|channel")
    else:
        print("❌ No valid configuration found")
        print()
        print("💡 Setup Options:")
        print("   1. Set TWITCH_ACCESS_TOKEN and TWITCH_CHANNEL")
        print("   2. Set TWITCH_SWARM_VOICE=username|oauth:token|channel")
        print("   3. Run: python tools/twitch_oauth_setup.py")
    
    print()
    return twitch_config


async def main():
    """Main debug entry point."""
    print()
    
    # Show configuration
    twitch_config = show_config()
    
    if not twitch_config:
        print("❌ Cannot start bot - configuration incomplete")
        print()
        print("See: docs/chat_presence/TWITCH_OAUTH_SETUP.md")
        return
    
    print("=" * 60)
    print("🚀 ATTEMPTING TO START TWITCH BOT")
    print("=" * 60)
    print()
    
    # Show config (masked)
    print("Configuration (masked):")
    print(f"  Username: {twitch_config['username']}")
    print(f"  Token: {twitch_config['oauth_token'][:15]}...")
    print(f"  Channel: {twitch_config['channel']}")
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    try:
        import irc.bot
        print("  ✅ irc library available")
    except ImportError:
        print("  ❌ irc library missing")
        print("  💡 Install: pip install irc")
        return
    
    try:
        from src.services.chat_presence import ChatPresenceOrchestrator
        print("  ✅ ChatPresenceOrchestrator available")
    except ImportError as e:
        print(f"  ❌ ChatPresenceOrchestrator import failed: {e}")
        return
    
    print()
    print("🔌 Connecting to Twitch...")
    print()
    
    # Create orchestrator
    try:
        orchestrator = ChatPresenceOrchestrator(
            twitch_config=twitch_config,
            obs_config=None,  # Disable OBS for now
        )
        
        # Start system
        success = await orchestrator.start()
        
        if not success:
            print()
            print("❌ Failed to start chat bot")
            print()
            print("Common issues:")
            print("  - Invalid OAuth token (must start with 'oauth:')")
            print("  - Token expired (get new token from https://twitchapps.com/tmi/)")
            print("  - Wrong channel name (must match your Twitch username)")
            print("  - Bot account not authorized")
            return
        
        print()
        print("=" * 60)
        print("✅ CHAT BOT IS LIVE!")
        print("=" * 60)
        print()
        print("The swarm is now active in your Twitch chat!")
        print()
        print("Test commands:")
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
    
    except Exception as e:
        print()
        print(f"❌ Error starting bot: {e}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("Debug info:")
        print(f"  Config keys: {list(twitch_config.keys())}")
        print(f"  Username: {twitch_config.get('username', 'MISSING')}")
        print(f"  Channel: {twitch_config.get('channel', 'MISSING')}")
        print(f"  Token present: {bool(twitch_config.get('oauth_token'))}")


if __name__ == "__main__":
    asyncio.run(main())


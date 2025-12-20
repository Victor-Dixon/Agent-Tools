#!/usr/bin/env python3
"""
Twitch Connection Diagnostic Test - TDD Approach
=================================================

Run this to diagnose connection issues step by step.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-03
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

load_dotenv()


def test_channel_name_extraction():
    """Test 1: Channel name extraction."""
    print("\n" + "="*60)
    print("TEST 1: Channel Name Extraction")
    print("="*60)
    
    channel = os.getenv("TWITCH_CHANNEL", "").strip()
    print(f"Original channel from .env: '{channel}'")
    
    # Extract channel name from URL if needed
    if channel:
        if "twitch.tv/" in channel.lower():
            parts = [p for p in channel.split("/") if p.strip()]
            channel = parts[-1].strip() if parts else channel
            channel = channel.rstrip("/").strip()
            print(f"🔧 Extracted channel name: '{channel}'")
        if channel.startswith("#"):
            channel = channel[1:]
            print(f"🔧 Removed # prefix: '{channel}'")
    
    print(f"✅ Final channel name: '{channel}'")
    assert channel and channel != "", "❌ Channel name is empty!"
    assert not channel.startswith("http"), "❌ Channel name still contains URL!"
    return channel


def test_oauth_token_format():
    """Test 2: OAuth token format."""
    print("\n" + "="*60)
    print("TEST 2: OAuth Token Format")
    print("="*60)
    
    token = os.getenv("TWITCH_ACCESS_TOKEN", "").strip()
    print(f"Original token from .env: '{token[:20]}...' (length: {len(token)})")
    
    # Ensure oauth: prefix
    if token and not token.startswith("oauth:"):
        token = f"oauth:{token}"
        print(f"🔧 Added oauth: prefix")
    
    print(f"✅ Final token format: '{token[:25]}...'")
    assert token.startswith("oauth:"), "❌ Token doesn't start with oauth:!"
    assert len(token) > 10, "❌ Token is too short!"
    return token


def test_bot_username():
    """Test 3: Bot username."""
    print("\n" + "="*60)
    print("TEST 3: Bot Username")
    print("="*60)
    
    channel = test_channel_name_extraction()
    username = os.getenv("TWITCH_BOT_USERNAME", "").strip() or channel
    print(f"Bot username: '{username}'")
    
    assert username, "❌ Bot username is empty!"
    return username


def test_configuration_complete():
    """Test 4: Complete configuration check."""
    print("\n" + "="*60)
    print("TEST 4: Configuration Check")
    print("="*60)
    
    channel = test_channel_name_extraction()
    token = test_oauth_token_format()
    username = test_bot_username()
    
    config = {
        "username": username,
        "oauth_token": token,
        "channel": channel,
    }
    
    print(f"\n✅ Configuration:")
    print(f"   Username: {config['username']}")
    print(f"   Channel: {config['channel']}")
    print(f"   Token: {config['oauth_token'][:25]}...")
    
    return config


def test_import_availability():
    """Test 5: Check if required libraries are available."""
    print("\n" + "="*60)
    print("TEST 5: Library Availability")
    print("="*60)
    
    try:
        import irc.bot
        import irc.client
        print("✅ irc library available")
        return True
    except ImportError as e:
        print(f"❌ irc library not available: {e}")
        print("   Install with: pip install irc")
        return False


def test_bridge_initialization():
    """Test 6: Test bridge initialization."""
    print("\n" + "="*60)
    print("TEST 6: Bridge Initialization")
    print("="*60)
    
    if not test_import_availability():
        return False
    
    config = test_configuration_complete()
    
    try:
        from src.services.chat_presence.twitch_bridge import TwitchChatBridge
        
        bridge = TwitchChatBridge(
            username=config["username"],
            oauth_token=config["oauth_token"],
            channel=config["channel"],
            on_message=None
        )
        
        print(f"✅ Bridge initialized")
        print(f"   Channel: {bridge.channel}")
        print(f"   Username: {bridge.username}")
        print(f"   Token format: {bridge.oauth_token[:25]}...")
        
        # Verify channel format
        assert bridge.channel.startswith("#"), f"❌ Channel should start with #, got: {bridge.channel}"
        assert bridge.channel == f"#{config['channel']}", f"❌ Channel mismatch: {bridge.channel} != #{config['channel']}"
        
        return True
    except Exception as e:
        print(f"❌ Bridge initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all diagnostic tests."""
    print("\n" + "="*60)
    print("🔍 TWITCH BOT CONNECTION DIAGNOSTIC TESTS")
    print("="*60)
    
    results = []
    
    results.append(("Channel Name", test_channel_name_extraction() is not None))
    results.append(("OAuth Token", test_oauth_token_format() is not None))
    results.append(("Bot Username", test_bot_username() is not None))
    results.append(("Libraries", test_import_availability()))
    results.append(("Bridge Init", test_bridge_initialization()))
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✅ All diagnostic tests passed!")
        print("   Configuration looks good. Try running the bot now.")
    else:
        print("\n❌ Some tests failed. Fix the issues above before running the bot.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


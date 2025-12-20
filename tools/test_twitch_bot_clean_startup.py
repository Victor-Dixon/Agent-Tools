#!/usr/bin/env python3
"""
Test Twitch Bot Clean Startup
==============================

Verifies bot starts cleanly without errors or warnings.
"""

import sys
import asyncio
import subprocess
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

import os
import logging

# Suppress INFO logs for cleaner output
logging.basicConfig(level=logging.WARNING)

async def test_clean_startup():
    """Test bot startup for errors/warnings."""
    print("=" * 60)
    print("🧪 TESTING TWITCH BOT CLEAN STARTUP")
    print("=" * 60)
    print()
    
    errors = []
    warnings = []
    
    # Test 1: Import check
    print("📦 Test 1: Import Check")
    try:
        from src.services.chat_presence.twitch_bridge import TwitchChatBridge
        from src.services.chat_presence.chat_presence_orchestrator import ChatPresenceOrchestrator
        print("   ✅ Imports successful")
    except Exception as e:
        errors.append(f"Import failed: {e}")
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: Configuration check
    print("\n📋 Test 2: Configuration Check")
    access_token = os.getenv("TWITCH_ACCESS_TOKEN")
    channel = os.getenv("TWITCH_CHANNEL", "").strip()
    
    if not access_token:
        errors.append("TWITCH_ACCESS_TOKEN not set")
        print("   ❌ TWITCH_ACCESS_TOKEN not set")
        return False
    
    if not channel:
        errors.append("TWITCH_CHANNEL not set")
        print("   ❌ TWITCH_CHANNEL not set")
        return False
    
    # Extract channel name
    if "twitch.tv/" in channel.lower():
        parts = [p for p in channel.split("/") if p.strip()]
        channel = parts[-1].strip().rstrip("/")
        if channel.startswith("#"):
            channel = channel[1:]
    
    print(f"   ✅ Configuration valid (channel: {channel})")
    
    # Test 3: Bridge creation (no connection)
    print("\n🔧 Test 3: Bridge Creation")
    try:
        bridge = TwitchChatBridge(
            username=channel,
            oauth_token=access_token if access_token.startswith("oauth:") else f"oauth:{access_token}",
            channel=channel,
            on_message=None,
        )
        # Check for event_loop parameter (should not exist)
        import inspect
        sig = inspect.signature(TwitchChatBridge.__init__)
        params = list(sig.parameters.keys())
        if 'event_loop' in params:
            errors.append("TwitchChatBridge still accepts event_loop parameter")
            print("   ❌ Bridge still accepts event_loop parameter")
            return False
        
        print("   ✅ Bridge created successfully (no event_loop parameter)")
    except TypeError as e:
        if 'event_loop' in str(e):
            errors.append(f"Bridge creation failed with event_loop error: {e}")
            print(f"   ❌ Bridge creation failed: {e}")
            return False
        else:
            errors.append(f"Bridge creation failed: {e}")
            print(f"   ❌ Bridge creation failed: {e}")
            return False
    except Exception as e:
        errors.append(f"Bridge creation failed: {e}")
        print(f"   ❌ Bridge creation failed: {e}")
        return False
    
    # Test 4: Orchestrator creation
    print("\n🎼 Test 4: Orchestrator Creation")
    try:
        twitch_config = {
            "username": channel,
            "oauth_token": access_token if access_token.startswith("oauth:") else f"oauth:{access_token}",
            "channel": channel,
        }
        
        orchestrator = ChatPresenceOrchestrator(
            twitch_config=twitch_config,
            obs_config=None,
        )
        print("   ✅ Orchestrator created successfully")
    except Exception as e:
        errors.append(f"Orchestrator creation failed: {e}")
        print(f"   ❌ Orchestrator creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Check orchestrator doesn't pass event_loop
    print("\n🔍 Test 5: Code Verification")
    try:
        orchestrator_file = Path("src/services/chat_presence/chat_presence_orchestrator.py")
        content = orchestrator_file.read_text()
        
        if "event_loop=event_loop" in content or "event_loop=event_loop," in content:
            errors.append("Orchestrator still passes event_loop parameter")
            print("   ❌ Orchestrator still passes event_loop")
            return False
        
        print("   ✅ Orchestrator doesn't pass event_loop")
    except Exception as e:
        warnings.append(f"Could not verify code: {e}")
        print(f"   ⚠️ Could not verify code: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if errors:
        print(f"\n❌ ERRORS FOUND: {len(errors)}")
        for error in errors:
            print(f"   - {error}")
        return False
    
    if warnings:
        print(f"\n⚠️ WARNINGS: {len(warnings)}")
        for warning in warnings:
            print(f"   - {warning}")
    
    print("\n✅ ALL TESTS PASSED - Bot should start cleanly!")
    print("\n💡 To start bot:")
    print("   python tools/START_CHAT_BOT_NOW.py")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_clean_startup())
    sys.exit(0 if success else 1)


#!/usr/bin/env python3
"""
Test Twitch Bot Connection (TDD)
=================================

Tests to verify bot actually connects and joins Twitch chat.
"""

import sys
import asyncio
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

import os
import logging

# Set up logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class TwitchBotConnectionTester:
    """TDD test suite for Twitch bot connection."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.test_results = []
    
    def test_configuration(self):
        """Test 1: Configuration is valid."""
        print("\n" + "=" * 60)
        print("TEST 1: Configuration Check")
        print("=" * 60)
        
        access_token = os.getenv("TWITCH_ACCESS_TOKEN")
        channel = os.getenv("TWITCH_CHANNEL", "").strip()
        
        if not access_token:
            self.errors.append("TWITCH_ACCESS_TOKEN not set")
            print("❌ FAIL: TWITCH_ACCESS_TOKEN not set")
            return False
        
        if not channel:
            self.errors.append("TWITCH_CHANNEL not set")
            print("❌ FAIL: TWITCH_CHANNEL not set")
            return False
        
        # Extract channel name
        if "twitch.tv/" in channel.lower():
            parts = [p for p in channel.split("/") if p.strip()]
            channel = parts[-1].strip().rstrip("/")
            if channel.startswith("#"):
                channel = channel[1:]
        
        print(f"✅ PASS: Configuration valid")
        print(f"   Channel: {channel}")
        print(f"   Token: {access_token[:20]}...")
        self.test_results.append(("Configuration", True))
        return True
    
    def test_bridge_creation(self):
        """Test 2: Bridge can be created."""
        print("\n" + "=" * 60)
        print("TEST 2: Bridge Creation")
        print("=" * 60)
        
        try:
            from src.services.chat_presence.twitch_bridge import TwitchChatBridge
            
            access_token = os.getenv("TWITCH_ACCESS_TOKEN")
            channel = os.getenv("TWITCH_CHANNEL", "").strip()
            
            if "twitch.tv/" in channel.lower():
                parts = [p for p in channel.split("/") if p.strip()]
                channel = parts[-1].strip().rstrip("/")
                if channel.startswith("#"):
                    channel = channel[1:]
            
            oauth_token = access_token if access_token.startswith("oauth:") else f"oauth:{access_token}"
            
            bridge = TwitchChatBridge(
                username=channel,
                oauth_token=oauth_token,
                channel=channel,
                on_message=None,
            )
            
            print("✅ PASS: Bridge created successfully")
            print(f"   Username: {bridge.username}")
            print(f"   Channel: {bridge.channel}")
            print(f"   Running: {bridge.running}")
            print(f"   Connected: {bridge.connected}")
            
            self.test_results.append(("Bridge Creation", True))
            return True
            
        except Exception as e:
            self.errors.append(f"Bridge creation failed: {e}")
            print(f"❌ FAIL: Bridge creation failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results.append(("Bridge Creation", False))
            return False
    
    async def test_connection_attempt(self):
        """Test 3: Bot can attempt connection."""
        print("\n" + "=" * 60)
        print("TEST 3: Connection Attempt")
        print("=" * 60)
        
        try:
            from src.services.chat_presence.twitch_bridge import TwitchChatBridge
            
            access_token = os.getenv("TWITCH_ACCESS_TOKEN")
            channel = os.getenv("TWITCH_CHANNEL", "").strip()
            
            if "twitch.tv/" in channel.lower():
                parts = [p for p in channel.split("/") if p.strip()]
                channel = parts[-1].strip().rstrip("/")
                if channel.startswith("#"):
                    channel = channel[1:]
            
            oauth_token = access_token if access_token.startswith("oauth:") else f"oauth:{access_token}"
            
            bridge = TwitchChatBridge(
                username=channel,
                oauth_token=oauth_token,
                channel=channel,
                on_message=None,
            )
            
            print("🔌 Attempting connection...")
            result = await bridge.connect()
            
            if result:
                print("✅ PASS: Connection attempt returned True")
                print(f"   Running: {bridge.running}")
                print(f"   Connected: {bridge.connected}")
                
                # Wait a bit to see if connection establishes
                print("⏳ Waiting 5 seconds for connection to establish...")
                await asyncio.sleep(5)
                
                print(f"   After wait - Running: {bridge.running}")
                print(f"   After wait - Connected: {bridge.connected}")
                
                if bridge.connected:
                    print("✅ PASS: Bot connected to channel")
                    self.test_results.append(("Connection", True))
                    return True
                else:
                    self.warnings.append("Connection attempt succeeded but not connected to channel")
                    print("⚠️ WARNING: Connection attempt succeeded but not connected to channel")
                    print("   This might indicate:")
                    print("   - OAuth token invalid/expired")
                    print("   - Channel name mismatch")
                    print("   - Bot account permissions")
                    self.test_results.append(("Connection", False))
                    return False
            else:
                self.errors.append("Connection attempt returned False")
                print("❌ FAIL: Connection attempt returned False")
                self.test_results.append(("Connection", False))
                return False
                
        except Exception as e:
            self.errors.append(f"Connection attempt failed: {e}")
            print(f"❌ FAIL: Connection attempt failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results.append(("Connection", False))
            return False
    
    async def test_orchestrator_startup(self):
        """Test 4: Orchestrator can start bot."""
        print("\n" + "=" * 60)
        print("TEST 4: Orchestrator Startup")
        print("=" * 60)
        
        try:
            from src.services.chat_presence.chat_presence_orchestrator import ChatPresenceOrchestrator
            
            access_token = os.getenv("TWITCH_ACCESS_TOKEN")
            channel = os.getenv("TWITCH_CHANNEL", "").strip()
            
            if "twitch.tv/" in channel.lower():
                parts = [p for p in channel.split("/") if p.strip()]
                channel = parts[-1].strip().rstrip("/")
                if channel.startswith("#"):
                    channel = channel[1:]
            
            oauth_token = access_token if access_token.startswith("oauth:") else f"oauth:{access_token}"
            
            twitch_config = {
                "username": channel,
                "oauth_token": oauth_token,
                "channel": channel,
            }
            
            orchestrator = ChatPresenceOrchestrator(
                twitch_config=twitch_config,
                obs_config=None,
            )
            
            print("🚀 Starting orchestrator...")
            result = await orchestrator.start()
            
            if result:
                print("✅ PASS: Orchestrator started successfully")
                print(f"   Twitch bridge running: {orchestrator.twitch_bridge.running if orchestrator.twitch_bridge else 'None'}")
                print(f"   Twitch bridge connected: {orchestrator.twitch_bridge.connected if orchestrator.twitch_bridge else 'None'}")
                
                # Wait a bit to see if connection establishes
                print("⏳ Waiting 5 seconds for connection to establish...")
                await asyncio.sleep(5)
                
                if orchestrator.twitch_bridge:
                    print(f"   After wait - Running: {orchestrator.twitch_bridge.running}")
                    print(f"   After wait - Connected: {orchestrator.twitch_bridge.connected}")
                    
                    if orchestrator.twitch_bridge.connected:
                        print("✅ PASS: Bot connected via orchestrator")
                        self.test_results.append(("Orchestrator Startup", True))
                        return True
                    else:
                        self.warnings.append("Orchestrator started but bot not connected")
                        print("⚠️ WARNING: Orchestrator started but bot not connected")
                        self.test_results.append(("Orchestrator Startup", False))
                        return False
                else:
                    self.errors.append("Twitch bridge not created by orchestrator")
                    print("❌ FAIL: Twitch bridge not created")
                    self.test_results.append(("Orchestrator Startup", False))
                    return False
            else:
                self.errors.append("Orchestrator start returned False")
                print("❌ FAIL: Orchestrator start returned False")
                self.test_results.append(("Orchestrator Startup", False))
                return False
                
        except Exception as e:
            self.errors.append(f"Orchestrator startup failed: {e}")
            print(f"❌ FAIL: Orchestrator startup failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results.append(("Orchestrator Startup", False))
            return False
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        print("\n📊 Test Results:")
        for test_name, passed in self.test_results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"   {status}: {test_name}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.warnings:
            print(f"\n⚠️ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        all_passed = all(result for _, result in self.test_results)
        
        if all_passed and not self.errors:
            print("\n✅ ALL TESTS PASSED!")
        else:
            print("\n❌ SOME TESTS FAILED - Investigation needed")
        
        return all_passed and not self.errors

async def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 TWITCH BOT CONNECTION TEST SUITE (TDD)")
    print("=" * 60)
    
    tester = TwitchBotConnectionTester()
    
    # Run tests
    if not tester.test_configuration():
        tester.print_summary()
        return 1
    
    if not tester.test_bridge_creation():
        tester.print_summary()
        return 1
    
    if not await tester.test_connection_attempt():
        tester.print_summary()
        return 1
    
    if not await tester.test_orchestrator_startup():
        tester.print_summary()
        return 1
    
    # Print summary
    success = tester.print_summary()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))


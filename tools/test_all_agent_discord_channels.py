#!/usr/bin/env python3
"""
Test All Agent Discord Channels
=================================

Tests all agent Discord channels to verify webhook URLs are configured correctly.
Checks that each agent has a valid webhook URL and that channel IDs are not being used as webhooks.

Author: Agent-2 (Architecture & Design Specialist)
Date: 2025-01-27
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
from src.core.config.timeout_constants import TimeoutConstants

# Load environment
load_dotenv()

def is_webhook_url(value: str) -> bool:
    """Check if value is a webhook URL (not a channel ID)."""
    if not value:
        return False
    # Webhook URLs start with https://discord.com/api/webhooks/ or https://discordapp.com/api/webhooks/
    return value.startswith("https://discord.com/api/webhooks/") or value.startswith("https://discordapp.com/api/webhooks/")

def is_channel_id(value: str) -> bool:
    """Check if value is a channel ID (numeric string)."""
    if not value:
        return False
    # Channel IDs are numeric strings
    return value.isdigit()

def test_webhook(webhook_url: str, agent_id: str) -> tuple[bool, str]:
    """Test if webhook URL is valid by sending a test message."""
    if not webhook_url:
        return False, "No webhook URL provided"
    
    if not is_webhook_url(webhook_url):
        return False, f"Invalid webhook URL format (not a webhook URL)"
    
    # Send a test message
    payload = {
        "content": f"🧪 Test message from Agent-2 - Testing {agent_id} channel configuration",
        "username": "Agent-2 Channel Tester"
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=TimeoutConstants.HTTP_SHORT)
        if response.status_code == 204:
            return True, "✅ Webhook valid - test message sent"
        else:
            return False, f"❌ Webhook error: {response.status_code} - {response.text[:100]}"
    except Exception as e:
        return False, f"❌ Webhook test failed: {str(e)[:100]}"

def main():
    """Test all agent Discord channels."""
    print("=" * 70)
    print("🧪 TESTING ALL AGENT DISCORD CHANNELS")
    print("=" * 70)
    print()
    
    agents = ["agent-1", "agent-2", "agent-3", "agent-4", "agent-5", "agent-6", "agent-7", "agent-8"]
    results = {}
    
    for agent in agents:
        agent_num = agent.split("-")[1]
        agent_cap = f"Agent-{agent_num}"
        
        print(f"📋 Testing {agent_cap}...")
        
        # Check environment variables
        webhook_1 = os.getenv(f"DISCORD_WEBHOOK_AGENT_{agent_num}")
        webhook_2 = os.getenv(f"DISCORD_AGENT{agent_num}_WEBHOOK")
        channel_id = os.getenv(f"DISCORD_CHANNEL_AGENT_{agent_num}")
        
        # Determine which webhook to use (priority order)
        webhook_url = webhook_1 or webhook_2
        
        print(f"   DISCORD_WEBHOOK_AGENT_{agent_num}: {'✅ SET' if webhook_1 else '❌ NOT SET'}")
        if webhook_1:
            if is_webhook_url(webhook_1):
                print(f"      Type: Webhook URL ✅")
            elif is_channel_id(webhook_1):
                print(f"      Type: Channel ID ❌ (WRONG - should be webhook URL)")
            else:
                print(f"      Type: Unknown format ⚠️")
        
        print(f"   DISCORD_AGENT{agent_num}_WEBHOOK: {'✅ SET' if webhook_2 else '❌ NOT SET'}")
        if webhook_2:
            if is_webhook_url(webhook_2):
                print(f"      Type: Webhook URL ✅")
            elif is_channel_id(webhook_2):
                print(f"      Type: Channel ID ❌ (WRONG - should be webhook URL)")
            else:
                print(f"      Type: Unknown format ⚠️")
        
        print(f"   DISCORD_CHANNEL_AGENT_{agent_num}: {'✅ SET' if channel_id else '❌ NOT SET'}")
        if channel_id:
            if is_channel_id(channel_id):
                print(f"      Type: Channel ID ✅ (correct - this is channel ID, not webhook)")
            elif is_webhook_url(channel_id):
                print(f"      Type: Webhook URL ⚠️ (unexpected - should be channel ID)")
            else:
                print(f"      Type: Unknown format ⚠️")
        
        # Test webhook if available
        if webhook_url:
            print(f"   Testing webhook...")
            success, message = test_webhook(webhook_url, agent_cap)
            print(f"   {message}")
            results[agent] = {
                "webhook_url": webhook_url,
                "webhook_valid": success,
                "message": message,
                "channel_id": channel_id
            }
        else:
            print(f"   ❌ No webhook URL found for {agent_cap}")
            results[agent] = {
                "webhook_url": None,
                "webhook_valid": False,
                "message": "No webhook URL configured",
                "channel_id": channel_id
            }
        
        print()
    
    # Summary
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print()
    
    valid_count = sum(1 for r in results.values() if r["webhook_valid"])
    total_count = len(results)
    
    for agent, result in results.items():
        agent_cap = f"Agent-{agent.split('-')[1]}"
        status = "✅ VALID" if result["webhook_valid"] else "❌ INVALID"
        print(f"{agent_cap:12} {status:12} - {result['message']}")
    
    print()
    print(f"Total: {valid_count}/{total_count} agents have valid webhook URLs")
    print()
    
    if valid_count == total_count:
        print("✅ All agent channels configured correctly!")
        return 0
    else:
        print(f"⚠️ {total_count - valid_count} agent(s) need webhook configuration")
        return 1

if __name__ == "__main__":
    sys.exit(main())



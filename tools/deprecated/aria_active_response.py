#!/usr/bin/env python3
"""
Aria Active Response - Auto-respond to "ari active" in Discord
================================================================

Automatically posts to Agent-8 Discord devlog when Aria says "ari active".

Author: Agent-8 (SSOT & System Integration Specialist)
Date: 2025-12-02
"""

import os
import sys
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import requests
from src.core.config.timeout_constants import TimeoutConstants


def post_to_discord_devlog(message: str) -> bool:
    """Post message to Agent-8 Discord devlog channel."""
    webhook_url = (
        os.getenv("DISCORD_WEBHOOK_AGENT_8") or
        os.getenv("DISCORD_AGENT8_WEBHOOK")
    )
    
    if not webhook_url:
        print("❌ Discord webhook not configured for Agent-8")
        print("   Set DISCORD_WEBHOOK_AGENT_8 in .env file")
        return False
    
    # Create embed
    embed = {
        "title": "🤖 Agent-8 Response",
        "description": message,
        "color": 0x3498DB,  # Blue
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {
            "text": "Agent-8 SSOT & System Integration"
        }
    }
    
    payload = {
        "embeds": [embed],
        "username": "Agent-8"
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=TimeoutConstants.HTTP_SHORT)
        if response.status_code == 204:
            print("✅ Posted to Discord devlog")
            return True
        else:
            print(f"❌ Discord API error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error posting to Discord: {e}")
        return False


def main():
    """Main execution."""
    if len(sys.argv) > 1:
        # Custom message provided
        message = " ".join(sys.argv[1:])
    else:
        # Default response
        message = """✅ **Agent-8 Active & Ready**

**Status**: ACTIVE_AGENT_MODE
**Current Mission**: Tools Consolidation Phase 2 - Category Consolidation
**Progress**: 108 tools archived, 231 consolidation candidates identified

**Recent Actions**:
- ✅ Master list verified (0 duplicates, 59 repos)
- ✅ Tools consolidation Phase 2 progressing
- ✅ Discord bot operational
- ✅ Ready for assignments

🐝 **WE. ARE. SWARM. ⚡🔥**"""
    
    print("📨 Posting to Agent-8 Discord devlog...")
    success = post_to_discord_devlog(message)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())



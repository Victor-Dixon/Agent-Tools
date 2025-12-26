#!/usr/bin/env python3
"""
Check Stuck Messages
====================

Checks for unheard messages in the swarm messaging system.
Rewritten for Swarm MCP.

Usage:
    python tools/check_stuck_messages.py [--agent AGENT]

Author: Agent-6
Date: 2025-12-26
"""

import argparse
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from swarm_mcp.core.messaging import MessageQueue, Howl
except ImportError:
    print("❌ Failed to import MessageQueue from swarm_mcp.core.messaging", file=sys.stderr)
    sys.exit(1)

def check_stuck_messages(agent_id: str = None, threshold_minutes: int = 15):
    """Check for messages that haven't been heard for a while."""
    queue = MessageQueue()
    
    # Identify inboxes
    territory = queue.territory
    agents = []
    if agent_id:
        agents = [agent_id]
    else:
        # Scan territory for agents
        if territory.exists():
            agents = [d.name for d in territory.iterdir() if d.is_dir()]
            
    if not agents:
        print("⚠️ No agents found with inboxes.")
        return

    stuck_count = 0
    now = datetime.now()
    threshold = timedelta(minutes=threshold_minutes)
    
    print(f"🔍 Checking for messages unheard for > {threshold_minutes} minutes")
    print("=" * 50)

    for agent in agents:
        unheard = queue.listen(agent, unheard_only=True, limit=100)
        for msg in unheard:
            # msg.timestamp is already a datetime object in new system
            age = now - msg.timestamp
            
            if age > threshold:
                stuck_count += 1
                urgency_icon = "🚨" if msg.urgency.value <= 2 else "⚠️"
                print(f"{urgency_icon} Stuck Message for {agent}:")
                print(f"   ID: {msg.id}")
                print(f"   From: {msg.sender}")
                print(f"   Age: {age}")
                print(f"   Content: {msg.content[:50]}...")
                print("-" * 30)

    if stuck_count == 0:
        print("✅ No stuck messages found.")
    else:
        print(f"⚠️ Found {stuck_count} stuck messages.")

def main():
    parser = argparse.ArgumentParser(description='Check for stuck messages')
    parser.add_argument('--agent', help='Check specific agent')
    parser.add_argument('--minutes', type=int, default=15, help='Threshold in minutes')
    args = parser.parse_args()
    
    check_stuck_messages(args.agent, args.minutes)

if __name__ == "__main__":
    main()

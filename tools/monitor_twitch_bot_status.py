#!/usr/bin/env python3
"""
Twitch Bot Status Monitor - A Tool We Wished We Had
====================================================

Monitors Twitch bot connection status, command responses, and health metrics.
Provides real-time dashboard view of bot activity.

Created: 2025-12-15
Author: Agent-3
"""

import asyncio
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.services.chat_presence.chat_presence_orchestrator import ChatPresenceOrchestrator


class TwitchBotMonitor:
    """Monitor Twitch bot status and health."""
    
    def __init__(self):
        self.orchestrator = None
        self.metrics = {
            "uptime_start": None,
            "messages_received": 0,
            "commands_processed": 0,
            "errors": [],
            "last_activity": None
        }
    
    async def start_monitoring(self, check_interval: int = 30):
        """Start monitoring bot status."""
        print("=" * 70)
        print("🐺 TWITCH BOT STATUS MONITOR")
        print("=" * 70)
        print()
        
        # Create orchestrator with normalized config
        from tools.start_twitchbot_with_fixes import apply_config_fixes
        config = apply_config_fixes()
        
        self.orchestrator = ChatPresenceOrchestrator(
            twitch_config=config,
            obs_config=None
        )
        
        print("🔌 Starting bot...")
        await self.orchestrator.start()
        self.metrics["uptime_start"] = datetime.now()
        
        print()
        print("=" * 70)
        print("✅ MONITORING ACTIVE")
        print("=" * 70)
        print(f"Check interval: {check_interval} seconds")
        print("Press Ctrl+C to stop")
        print()
        
        try:
            while True:
                await asyncio.sleep(check_interval)
                self._print_status()
        except KeyboardInterrupt:
            print("\n🛑 Stopping monitor...")
            await self.orchestrator.stop()
            print("✅ Monitor stopped")
    
    def _print_status(self):
        """Print current status."""
        if not self.orchestrator or not self.orchestrator.twitch_bridge:
            print("⚠️  Bot not initialized")
            return
        
        bridge = self.orchestrator.twitch_bridge
        uptime = (datetime.now() - self.metrics["uptime_start"]).total_seconds() if self.metrics["uptime_start"] else 0
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
              f"Status: {'🟢 CONNECTED' if bridge.connected else '🔴 DISCONNECTED'} | "
              f"Running: {bridge.running} | "
              f"Uptime: {int(uptime)}s | "
              f"Messages: {self.metrics['messages_received']}")


async def main():
    """Main entry point."""
    monitor = TwitchBotMonitor()
    await monitor.start_monitoring(check_interval=30)


if __name__ == "__main__":
    asyncio.run(main())

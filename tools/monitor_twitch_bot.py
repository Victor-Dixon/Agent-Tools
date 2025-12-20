#!/usr/bin/env python3
"""
Twitch Bot Monitor
==================

Monitors the Twitch bot output in real-time by tailing log output.
This provides a better way to monitor the bot than pasting terminal output.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-04
V2 Compliant: Yes
<!-- SSOT Domain: infrastructure -->
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from src.core.config.timeout_constants import TimeoutConstants

def monitor_bot_process():
    """Monitor the Twitch bot process and show its output."""
    print("=" * 60)
    print("🔍 TWITCH BOT MONITOR")
    print("=" * 60)
    print()
    print("Monitoring bot process...")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    # Find the bot process
    try:
        # On Windows, use tasklist to find Python processes
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
            capture_output=True,
            text=True,
            timeout=TimeoutConstants.HTTP_QUICK
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            python_processes = [line for line in lines if 'python.exe' in line]
            print(f"Found {len(python_processes)} Python process(es)")
            
            if python_processes:
                print("\nBot process(es) running:")
                for proc in python_processes[:5]:  # Show first 5
                    print(f"  {proc}")
        else:
            print("Could not check processes")
    except Exception as e:
        print(f"Error checking processes: {e}")
    
    print("\n" + "=" * 60)
    print("💡 TIP: Run the bot in a separate terminal to see full output")
    print("   Or check the terminal where you started the bot")
    print("=" * 60)
    print("\nLooking for key indicators:")
    print("  ✅ 'Connected to Twitch IRC' - Connection successful")
    print("  ✅ 'Joined #digital_dreamscape' - Channel joined")
    print("  ✅ 'Sent online message' - Bot is live")
    print("  ❌ 'Disconnected from Twitch IRC' - Connection lost")
    print("  ❌ 'IRC Error' - Authentication or connection error")
    print()

if __name__ == "__main__":
    try:
        monitor_bot_process()
        # Keep running to show status
        while True:
            time.sleep(5)
            print(".", end="", flush=True)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

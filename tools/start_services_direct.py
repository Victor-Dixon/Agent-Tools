#!/usr/bin/env python3
"""
Start Message Queue and Discord Bot Directly
===========================================

Bypasses main.py and starts both services directly in the background.

Author: Agent-7
V2 Compliant: Yes
"""

import sys
import subprocess
import time
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def start_message_queue():
    """Start message queue processor in background."""
    print("📬 Starting Message Queue Processor...")
    script = project_root / "tools" / "start_message_queue_processor.py"
    
    try:
        # Start in background (Windows)
        if sys.platform == "win32":
            process = subprocess.Popen(
                [sys.executable, str(script)],
                cwd=str(project_root),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            process = subprocess.Popen(
                [sys.executable, str(script)],
                cwd=str(project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        print(f"   ✅ Message Queue Processor started (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"   ❌ Failed to start Message Queue: {e}")
        return None


def start_discord_bot():
    """Start Discord bot in background."""
    print("💬 Starting Discord Bot...")
    script = project_root / "tools" / "run_unified_discord_bot_with_restart.py"
    
    try:
        # Start in background (Windows)
        if sys.platform == "win32":
            process = subprocess.Popen(
                [sys.executable, str(script)],
                cwd=str(project_root),
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            process = subprocess.Popen(
                [sys.executable, str(script)],
                cwd=str(project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        print(f"   ✅ Discord Bot started (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"   ❌ Failed to start Discord Bot: {e}")
        return None


def main():
    """Main execution."""
    print("🚀 Starting Message Queue and Discord Bot Directly")
    print("=" * 60)
    print()
    
    processes = {}
    
    # Start Message Queue
    mq_process = start_message_queue()
    if mq_process:
        processes['message_queue'] = mq_process
    
    time.sleep(1)
    
    # Start Discord Bot
    discord_process = start_discord_bot()
    if discord_process:
        processes['discord'] = discord_process
    
    print()
    print("=" * 60)
    print(f"✅ Started {len(processes)}/2 services")
    print()
    print("Services are running in background.")
    print("To stop services, use Task Manager or:")
    print(f"   taskkill /PID {mq_process.pid if mq_process else 'N/A'} /F  # Message Queue")
    print(f"   taskkill /PID {discord_process.pid if discord_process else 'N/A'} /F  # Discord Bot")
    print()
    
    return 0 if len(processes) == 2 else 1


if __name__ == "__main__":
    sys.exit(main())


#!/usr/bin/env python3
"""
Direct Discord Bot Restart Script
==================================

Stops any running Discord bot processes and starts a new one.

Author: Agent-8
Date: 2025-12-13
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def stop_discord_bot():
    """Stop any running Discord bot processes."""
    print("🛑 Stopping Discord bot processes...")
    
    try:
        # Use wmic to find processes with unified_discord_bot in command line
        result = subprocess.run(
            ['wmic', 'process', 'where', 'commandline like "%unified_discord_bot%"', 'get', 'processid', '/format:csv'],
            capture_output=True,
            text=True,
            check=False
        )
        
        killed_count = 0
        lines = result.stdout.strip().split('\n')
        
        for line in lines:
            if 'ProcessId' in line or not line.strip() or ',' not in line:
                continue
            parts = line.split(',')
            if len(parts) >= 2:
                pid = parts[-1].strip()
                if pid and pid.isdigit():
                    try:
                        subprocess.run(['taskkill', '/F', '/PID', pid], 
                                     capture_output=True, check=False)
                        killed_count += 1
                    except:
                        pass
        
        if killed_count > 0:
            print(f"   Stopped {killed_count} Discord bot process(es)")
            time.sleep(2)  # Wait for processes to fully stop
        else:
            print("   No Discord bot processes found")
            
    except Exception as e:
        print(f"   Warning: Could not stop processes: {e}")
        # Fallback: try to find and kill by script name
        print("   Attempting fallback method...")

def start_discord_bot():
    """Start the Discord bot."""
    print("🚀 Starting Discord bot...")
    
    project_root = Path(__file__).parent.parent
    bot_script = project_root / "src" / "discord_commander" / "unified_discord_bot.py"
    
    if not bot_script.exists():
        print(f"❌ Bot script not found: {bot_script}")
        return False
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_root)
    
    # Start bot in background
    process = subprocess.Popen(
        [sys.executable, str(bot_script)],
        cwd=str(project_root),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    print(f"   Bot started with PID: {process.pid}")
    print("   Bot is running in background")
    return True

if __name__ == "__main__":
    stop_discord_bot()
    time.sleep(1)
    start_discord_bot()
    print("\n✅ Discord bot restart complete")

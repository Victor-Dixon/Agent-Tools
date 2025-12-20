#!/usr/bin/env python3
"""
Test Discord Bot - Debug Instance
==================================

Starts a new Discord bot instance for debugging without stopping the existing one.
Uses a different process name and optional test token.

Author: Agent-1 (Integration & Core Systems Specialist)
Date: 2025-12-06
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add project root to path
from src.core.config.timeout_constants import TimeoutConstants

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def check_existing_bot():
    """Check if Discord bot is already running."""
    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_QUICK
            )
            if "unified_discord_bot" in result.stdout.lower():
                print("⚠️  Found existing Discord bot process")
                return True
        else:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=TimeoutConstants.HTTP_QUICK
            )
            if "unified_discord_bot" in result.stdout:
                print("⚠️  Found existing Discord bot process")
                return True
    except Exception as e:
        print(f"⚠️  Could not check for existing bot: {e}")
    
    return False

def start_debug_bot():
    """Start a new Discord bot instance for debugging."""
    print("=" * 70)
    print("🔧 STARTING DISCORD BOT DEBUG INSTANCE")
    print("=" * 70)
    print()
    
    # Check for existing bot
    if check_existing_bot():
        print("ℹ️  Existing bot detected - this is a debug instance")
        print("   Both bots can run simultaneously for testing")
        print()
    
    # Check for token
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ DISCORD_BOT_TOKEN not set in environment")
        print("   Set it in .env file or environment variable")
        return False
    
    print("✅ Discord bot token found")
    print()
    
    # Start bot in new console/process
    bot_script = project_root / "src" / "discord_commander" / "unified_discord_bot.py"
    
    if not bot_script.exists():
        print(f"❌ Bot script not found: {bot_script}")
        return False
    
    print(f"🚀 Starting debug bot instance...")
    print(f"   Script: {bot_script}")
    print()
    
    try:
        if sys.platform == "win32":
            # Windows: Start in new console window
            process = subprocess.Popen(
                [sys.executable, str(bot_script)],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=str(project_root)
            )
        else:
            # Linux/Mac: Start in background
            process = subprocess.Popen(
                [sys.executable, str(bot_script)],
                start_new_session=True,
                cwd=str(project_root)
            )
        
        print(f"✅ Debug bot started (PID: {process.pid})")
        print(f"   Check the new console window for bot output")
        print()
        print("💡 To stop this debug instance:")
        print(f"   - Close the console window, or")
        if sys.platform == "win32":
            print(f"   - Run: taskkill /F /PID {process.pid}")
        else:
            print(f"   - Run: kill {process.pid}")
        print()
        
        # Wait a moment to see if it crashes immediately
        time.sleep(3)
        
        if process.poll() is not None:
            print(f"❌ Bot exited immediately (exit code: {process.returncode})")
            print("   Check console output for errors")
            return False
        
        print("✅ Bot is running - check Discord for connection")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start debug bot: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = start_debug_bot()
    sys.exit(0 if success else 1)



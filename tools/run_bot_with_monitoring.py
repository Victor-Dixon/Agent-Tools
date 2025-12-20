#!/usr/bin/env python3
"""
Run Twitch Bot with Automated Monitoring
=========================================

Runs the bot and automatically monitors for connection status.
Provides clear success/failure indicators.

<!-- SSOT Domain: infrastructure -->

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-04
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_bot_with_monitoring():
    """Run bot and monitor for connection success."""
    print("=" * 60)
    print("🚀 STARTING TWITCH BOT WITH MONITORING")
    print("=" * 60)
    print()
    
    bot_script = project_root / "tools" / "START_CHAT_BOT_NOW.py"
    
    if not bot_script.exists():
        print(f"❌ Bot script not found: {bot_script}")
        return False
    
    print(f"📝 Running: {bot_script}")
    print()
    print("Monitoring for connection indicators...")
    print("  ✅ Looking for: 'Connected to Twitch IRC'")
    print("  ✅ Looking for: 'Joined #digital_dreamscape'")
    print("  ❌ Will detect: 'Disconnected from Twitch IRC'")
    print("  ❌ Will detect: 'IRC Error'")
    print()
    print("-" * 60)
    print()
    
    # Run the bot
    try:
        process = subprocess.Popen(
            [sys.executable, str(bot_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Monitor output
        connection_established = False
        channel_joined = False
        error_detected = False
        
        print("📊 BOT OUTPUT:")
        print("-" * 60)
        
        for line in process.stdout:
            print(line.rstrip())
            
            # Check for success indicators
            if "Connected to Twitch IRC" in line or "on_welcome called" in line:
                connection_established = True
                print("\n✅ CONNECTION ESTABLISHED!\n")
            
            if "Joined #digital_dreamscape" in line or "Joined" in line:
                channel_joined = True
                print("\n✅ CHANNEL JOINED!\n")
            
            if "Sent online message" in line:
                print("\n✅ BOT IS LIVE AND SENDING MESSAGES!\n")
            
            # Check for errors
            if "Disconnected from Twitch IRC" in line:
                error_detected = True
                print("\n❌ DISCONNECTION DETECTED!\n")
            
            if "IRC Error" in line or "❌" in line:
                error_detected = True
                print("\n❌ ERROR DETECTED!\n")
            
            # Flush output
            sys.stdout.flush()
        
        # Wait for process to complete
        return_code = process.wait()
        
        print("\n" + "=" * 60)
        print("📊 FINAL STATUS:")
        print("=" * 60)
        print(f"  Connection Established: {'✅' if connection_established else '❌'}")
        print(f"  Channel Joined: {'✅' if channel_joined else '❌'}")
        print(f"  Errors Detected: {'❌ YES' if error_detected else '✅ NO'}")
        print(f"  Exit Code: {return_code}")
        print()
        
        if connection_established and channel_joined and not error_detected:
            print("✅ BOT IS WORKING CORRECTLY!")
            return True
        else:
            print("❌ BOT ENCOUNTERED ISSUES - CHECK OUTPUT ABOVE")
            return False
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        if 'process' in locals():
            process.terminate()
        return False
    except Exception as e:
        print(f"\n❌ Error running bot: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_bot_with_monitoring()
    sys.exit(0 if success else 1)


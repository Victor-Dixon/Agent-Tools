#!/usr/bin/env python3
"""
Run Discord Bot with Auto-Restart Support
==========================================

Enhanced runner script that supports !restart command.
When !restart is used, bot gracefully shuts down and automatically restarts.

<!-- SSOT Domain: infrastructure -->

Author: Agent-6 (Co-Captain) - Implementation
Spec: Agent-2 (Architecture LEAD)
Date: 2025-10-15
"""

import os
import sys
import time
from pathlib import Path

def main():
    """Main loop with auto-restart support."""
    print("🚀 Discord Bot Runner with Auto-Restart")
    print("🐝 WE. ARE. SWARM.\n")
    
    restart_flag = Path('.discord_bot_restart')
    crash_count = 0
    max_crashes = 3
    crash_cooldown = 10  # seconds
    
    while True:
        # Run bot
        print("▶️  Starting Discord bot...")
        exit_code = run_bot()
        
        # Check for restart flag (intentional restart via !restart command)
        if restart_flag.exists():
            # Restart requested via !restart command
            restart_flag.unlink()  # Remove flag file
            crash_count = 0  # Reset crash count on intentional restart
            print("\n🔄 Restart requested - restarting in 3 seconds...")
            time.sleep(3)
            continue  # Restart loop
        
        # Check if bot crashed (non-zero exit code)
        if exit_code != 0:
            crash_count += 1
            print(f"\n⚠️  Bot crashed (exit code: {exit_code})")
            print(f"   Crash count: {crash_count}/{max_crashes}")
            
            if crash_count >= max_crashes:
                print(f"\n❌ Bot crashed {max_crashes} times in a row!")
                print("   Stopping auto-restart to prevent infinite loop.")
                print("   Please investigate the issue before restarting manually.")
                break
            
            print(f"   Waiting {crash_cooldown} seconds before restart...")
            time.sleep(crash_cooldown)
            continue  # Restart after cooldown
        
        # Normal exit (from !shutdown or clean exit)
        print("\n👋 Bot shutdown complete")
        break


def run_bot():
    """Run the Discord bot and return exit code."""
    try:
        import sys
        import subprocess
        from pathlib import Path
        
        # CRITICAL FIX: True Linux-like restart - spawn new Python process
        # This ensures all modules are reloaded from disk, not from cache
        project_root = Path(__file__).parent.parent
        bot_script = project_root / "src" / "discord_commander" / "unified_discord_bot.py"
        
        if not bot_script.exists():
            print(f"❌ Bot script not found: {bot_script}")
            return 1
        
        # Spawn new Python process to run bot
        # This ensures fresh module imports (no cache)
        env = os.environ.copy()
        env['PYTHONPATH'] = str(project_root)

        process = subprocess.Popen(
            [sys.executable, str(bot_script)],
            cwd=str(project_root),
            env=env,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        
        # Wait for process to complete
        exit_code = process.wait()
        
        return exit_code
        
    except KeyboardInterrupt:
        print("\n⚠️  Bot interrupted by user (Ctrl+C)")
        return 1
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("💡 Make sure discord.py is installed: pip install discord.py")
        import traceback
        traceback.print_exc()
        return 1
        
    except Exception as e:
        print(f"\n❌ Bot error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Runner shutdown by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Fatal error in runner: {e}")
        sys.exit(1)


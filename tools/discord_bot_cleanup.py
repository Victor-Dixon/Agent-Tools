#!/usr/bin/env python3
"""
Discord Bot Cleanup Script
===========================

Stops all running Discord bot processes to allow clean restart.

<!-- SSOT Domain: infrastructure -->

Author: Agent-3 (Infrastructure & DevOps)
Date: 2025-01-27
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("🧹 DISCORD BOT CLEANUP")
print("=" * 70)
print()

# Try to use psutil for better process detection
try:
    import psutil
    
    print("🔍 Finding Discord bot processes...")
    current_pid = os.getpid()
    discord_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] == current_pid:
                continue
            
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if any(keyword in cmdline.lower() for keyword in [
                'unified_discord_bot',
                'start_discord',
                'discord_commander',
                'run_unified_discord_bot'
            ]):
                discord_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': cmdline[:100]
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if not discord_processes:
        print("✅ No Discord bot processes found running")
    else:
        print(f"⚠️  Found {len(discord_processes)} Discord bot process(es):")
        for p in discord_processes:
            print(f"   PID {p['pid']}: {p['cmdline']}")
        
        print()
        response = input("Stop all Discord bot processes? (y/N): ").strip().lower()
        
        if response == 'y':
            stopped = 0
            for p in discord_processes:
                try:
                    proc = psutil.Process(p['pid'])
                    proc.terminate()
                    try:
                        from src.core.config.timeout_constants import TimeoutConstants
                        proc.wait(timeout=TimeoutConstants.HTTP_QUICK)
                    except psutil.TimeoutExpired:
                        proc.kill()
                        proc.wait()
                    print(f"✅ Stopped PID {p['pid']}")
                    stopped += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    print(f"⚠️  Could not stop PID {p['pid']}: {e}")
            
            print(f"\n✅ Stopped {stopped}/{len(discord_processes)} processes")
            
            # Also remove lock file if it exists
            lock_file = project_root / "logs" / "discord_system.lock"
            if lock_file.exists():
                try:
                    lock_file.unlink()
                    print(f"✅ Removed lock file: {lock_file}")
                except Exception as e:
                    print(f"⚠️  Could not remove lock file: {e}")
        else:
            print("❌ Cleanup cancelled")
            sys.exit(0)
    
except ImportError:
    print("⚠️  psutil not installed - cannot detect processes automatically")
    print("💡 Install with: pip install psutil")
    print()
    print("💡 Manual cleanup:")
    print("   PowerShell: Get-Process python | Stop-Process -Force")
    print("   Or kill processes manually from Task Manager")
    sys.exit(1)

print()
print("=" * 70)
print("✅ CLEANUP COMPLETE")
print("=" * 70)
print()
print("💡 Now start the bot fresh:")
print("   python tools/start_discord_system.py")
print()


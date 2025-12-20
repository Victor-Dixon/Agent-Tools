#!/usr/bin/env python3
"""
Fix Message Queue Processes
===========================

Kills duplicate queue processor instances to prevent file locking and race conditions.
Only keeps one instance running.

Author: Agent-2
V2 Compliant: <200 lines
"""

import sys
import signal
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("⚠️  psutil not available - install with: pip install psutil")


def find_queue_processes():
    """Find all running queue processor processes."""
    if not HAS_PSUTIL:
        return []

    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if not cmdline:
                continue

            cmdline_str = ' '.join(str(arg) for arg in cmdline).lower()

            # Check if it's a queue processor
            if any(keyword in cmdline_str for keyword in [
                'start_message_queue_processor',
                'message_queue_processor',
                '--message-queue'
            ]):
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': ' '.join(cmdline[:3]),
                    'create_time': proc.info['create_time']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Sort by create_time (oldest first)
    processes.sort(key=lambda x: x['create_time'])
    return processes


def kill_process(pid: int, force: bool = False) -> bool:
    """Kill a process by PID."""
    if not HAS_PSUTIL:
        return False

    try:
        proc = psutil.Process(pid)
        if force:
            proc.kill()
        else:
            proc.terminate()
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        print(f"  ⚠️  Cannot kill PID {pid}: {e}")
        return False


def main():
    """Main fix routine."""
    print("=" * 70)
    print("MESSAGE QUEUE PROCESS FIX")
    print("=" * 70)
    print()

    if not HAS_PSUTIL:
        print("❌ psutil not available")
        print("   Install with: pip install psutil")
        return 1

    # Find all queue processes
    print("🔍 Finding queue processor processes...")
    processes = find_queue_processes()

    if not processes:
        print("  ✅ No queue processor processes found")
        return 0

    print(f"  ⚠️  Found {len(processes)} queue processor process(es)")
    print()

    # Show all processes
    print("📋 Running Processes:")
    for i, proc in enumerate(processes, 1):
        print(f"  {i}. PID {proc['pid']}: {proc['cmdline']}")
    print()

    # Keep the oldest one, kill the rest
    if len(processes) > 1:
        print("🔧 Fixing duplicate processes...")
        print(f"  ✅ Keeping PID {processes[0]['pid']} (oldest)")

        killed = 0
        for proc in processes[1:]:
            print(f"  🛑 Killing PID {proc['pid']}...")
            if kill_process(proc['pid']):
                killed += 1
                print(f"    ✅ Terminated")
            else:
                print(f"    ⚠️  Failed to terminate, trying force kill...")
                if kill_process(proc['pid'], force=True):
                    killed += 1
                    print(f"    ✅ Force killed")

        print()
        print(f"✅ Fixed: Killed {killed} duplicate process(es)")
        print(f"   Remaining: 1 process (PID {processes[0]['pid']})")
    else:
        print("✅ Only one process running - no action needed")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Captain Cycle Scheduler - Automated Force Multiplier System
==========================================================

Runs 4x daily captain cycles for force multiplier execution:
- Real-time idle detection
- Proactive task assignment
- Dependency monitoring
- Zero-idle-time enforcement

Author: Agent-4 (Captain)
Date: 2025-12-13
"""

import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def run_force_multiplier_monitor():
    """Run force multiplier monitor."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Running force multiplier monitor...")
    result = subprocess.run(
        [sys.executable, str(project_root / "tools/force_multiplier_monitor.py")],
        capture_output=True,
        text=True,
        cwd=str(project_root)
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.returncode == 0

def run_auto_assign_next_round():
    """Run auto-assign next round."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Running auto-assign next round...")
    result = subprocess.run(
        [sys.executable, str(project_root / "tools/auto_assign_next_round.py")],
        capture_output=True,
        text=True,
        cwd=str(project_root)
    )
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.returncode == 0

def run_dependency_chain_monitor():
    """Run dependency chain monitor."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Running dependency chain monitor...")
    result = subprocess.run(
        [sys.executable, str(project_root / "tools/monitor_4agent_dependency_chain.py")],
        capture_output=True,
        text=True,
        cwd=str(project_root)
    )
    print(result.stdout)
    return result.returncode == 0

def captain_cycle_full():
    """Full captain cycle (4x daily)."""
    print("=" * 70)
    print(f"CAPTAIN CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    # Step 1: Monitor all agents
    print("STEP 1: Force Multiplier Monitor")
    print("-" * 70)
    run_force_multiplier_monitor()
    print()
    
    # Step 2: Auto-assign next rounds
    print("STEP 2: Auto-Assign Next Rounds")
    print("-" * 70)
    run_auto_assign_next_round()
    print()
    
    # Step 3: Check dependencies
    print("STEP 3: Dependency Chain Monitor")
    print("-" * 70)
    run_dependency_chain_monitor()
    print()
    
    print("=" * 70)
    print("✅ CAPTAIN CYCLE COMPLETE")
    print("=" * 70)

def captain_cycle_quick():
    """Quick cycle (every 15 minutes)."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Quick Captain Cycle...")
    run_force_multiplier_monitor()
    run_auto_assign_next_round()

def main():
    """Main scheduler."""
    import argparse
    parser = argparse.ArgumentParser(description="Captain Cycle Scheduler")
    parser.add_argument("--mode", choices=["full", "quick", "continuous"], default="full",
                       help="Cycle mode: full (4x daily), quick (15-min), continuous (loop)")
    parser.add_argument("--interval", type=int, default=15,
                       help="Interval in minutes for continuous mode")
    
    args = parser.parse_args()
    
    if args.mode == "full":
        captain_cycle_full()
    elif args.mode == "quick":
        captain_cycle_quick()
    elif args.mode == "continuous":
        print("🔄 Starting continuous captain cycles (15-minute intervals)")
        print("🛑 Press Ctrl+C to stop")
        print()
        try:
            while True:
                captain_cycle_quick()
                print(f"\n⏱️  Next cycle in {args.interval} minutes...\n")
                time.sleep(args.interval * 60)
        except KeyboardInterrupt:
            print("\n🛑 Captain cycles stopped")

if __name__ == "__main__":
    main()



#!/usr/bin/env python3
"""
Check Keyboard Lock Status
===========================

Quick diagnostic tool to check if keyboard lock is held and by what.

<!-- SSOT Domain: infrastructure -->
"""

from src.core.keyboard_control_lock import (
    is_locked,
    get_current_holder,
    get_lock_status,
    force_release_lock
)
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Check and optionally release keyboard lock."""
    status = get_lock_status()

    print("=" * 60)
    print("KEYBOARD LOCK STATUS")
    print("=" * 60)
    print(f"Locked: {status['locked']}")
    print(f"Current Holder: {status['current_holder']}")
    print(f"Timeout: {status['timeout_seconds']}s")
    print("=" * 60)

    if status['locked']:
        print(f"\n⚠️ Lock is held by: {status['current_holder']}")
        response = input("\nForce release lock? (y/N): ").strip().lower()
        if response == 'y':
            if force_release_lock():
                print("✅ Lock force released")
            else:
                print("❌ Failed to release lock")
        else:
            print("Lock not released")
    else:
        print("\n✅ Lock is free - no issues")

    return 0


if __name__ == "__main__":
    sys.exit(main())

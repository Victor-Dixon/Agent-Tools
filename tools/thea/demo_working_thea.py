#!/usr/bin/env python3
"""
Working Thea Demo - Using Proven Pattern
=========================================

Uses the proven thea_automation.py approach that we know works.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Use the PROVEN working code
from thea_automation import TheaAutomation


def demo_working():
    """Demo using proven working code."""

    print()
    print("=" * 70)
    print("🎬 THEA AUTOMATION DEMO - PROVEN WORKING CODE")
    print("=" * 70)
    print()
    print("Using thea_automation.py (proven to work)")
    print("Browser will be VISIBLE - watch the automation!")
    print()

    # Create automation
    thea = TheaAutomation()

    message = """Hello Thea! Agent-3 here testing the automation.

Today's work:
- Discord: 9→4 files ✅
- Browser: 15→5 files ✅  
- V2 compliance: 100% ✅

Please confirm receipt! 🐝"""

    print(f"📤 Message: {message[:60]}...")
    print()
    print("👀 WATCH THE BROWSER - Starting in 3 seconds!")
    print()

    import time

    time.sleep(3)

    # Use the proven communicate method
    result = thea.communicate(message, save=True)

    print()
    print("=" * 70)
    print("📊 RESULT")
    print("=" * 70)
    print(f"Success: {result['success']}")

    if result["response"]:
        print("\n📨 Thea's Response:")
        print("-" * 70)
        print(result["response"])
        print("-" * 70)

    if result["file"]:
        print(f"\n💾 Saved to: {result['file']}")

    print()
    print("✅ Demo complete!")
    print()
    print("🐝 WE ARE SWARM!")
    print()


if __name__ == "__main__":
    demo_working()

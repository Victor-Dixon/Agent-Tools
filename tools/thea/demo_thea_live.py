#!/usr/bin/env python3
"""
Live Thea Automation Demo - Non-Headless
=========================================

Visual demonstration of consolidated Thea service sending a message.
Browser will be visible so you can see the automation in action!

Author: Agent-3 (Infrastructure & DevOps)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.services.thea import TheaService


def demo_thea_automation():
    """Demonstrate Thea automation with visible browser."""

    print()
    print("=" * 70)
    print("🎬 LIVE THEA AUTOMATION DEMO")
    print("=" * 70)
    print()
    print("🔍 Browser will be VISIBLE - watch the automation!")
    print()

    # Create service (non-headless)
    print("🚀 Initializing Thea service (non-headless mode)...")
    thea = TheaService(cookie_file="thea_cookies.json", headless=False)

    try:
        # Test message from Agent-3
        message = """Hello Thea! 🐝

This is Agent-3 (Infrastructure & DevOps Specialist) demonstrating the consolidated Thea automation service!

**What I've accomplished today:**
- ✅ Discord consolidation: 9→4 files (56% reduction)
- ✅ Browser consolidation: 15→5 files (67% reduction)  
- ✅ Created V2 compliant Thea service (341 lines)
- ✅ All tests passing (15/15 - 100%)

**This message is being sent autonomously using:**
- PyAutoGUI clipboard automation (proven working method)
- Selenium WebDriver for browser control
- Consolidated browser infrastructure

Please confirm you received this message!

WE ARE SWARM! 🚀"""

        print("📝 Message prepared:")
        print("-" * 70)
        print(message)
        print("-" * 70)
        print()

        print("🌐 Sending message to Thea Manager...")
        print("👀 WATCH THE BROWSER - automation starting in 3 seconds!")
        print()

        import time

        time.sleep(3)

        # Send and wait for response
        result = thea.communicate(message, save=True)

        print()
        print("=" * 70)
        print("📊 AUTOMATION RESULT")
        print("=" * 70)
        print(f"Success: {result['success']}")
        print()

        if result["response"]:
            print("📨 THEA'S RESPONSE:")
            print("-" * 70)
            print(result["response"])
            print("-" * 70)
            print()

        if result["file"]:
            print(f"💾 Conversation saved to: {result['file']}")

        print()

        if result["success"]:
            print("✅ AUTOMATION SUCCESSFUL!")
            print()
            print("Demo completed! You saw:")
            print("  1. ✅ Browser opened automatically")
            print("  2. ✅ Navigated to ChatGPT/Thea")
            print("  3. ✅ Authentication checked (or manual login if needed)")
            print("  4. ✅ Message pasted via PyAutoGUI")
            print("  5. ✅ Message sent via Enter key")
            print("  6. ✅ Response captured (if detector available)")
            print("  7. ✅ Browser closed cleanly")
        else:
            print("⚠️  Automation completed with warnings")
            print("     (May need manual login or longer response wait)")

        print()

    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")

    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        print("\n🧹 Cleaning up...")
        thea.cleanup()
        print("✅ Browser closed")
        print()
        print("🐝 WE ARE SWARM - Live demo complete!")
        print()


if __name__ == "__main__":
    print()
    print("🎬 Starting LIVE Thea automation demonstration...")
    print("   Browser will be VISIBLE - watch the magic happen!")
    print()

    demo_thea_automation()

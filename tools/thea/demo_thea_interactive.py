#!/usr/bin/env python3
"""
Interactive Thea Automation Demo
=================================

Step-by-step demonstration with manual login support.
Browser stays open so you can see everything!
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.infrastructure.browser import BrowserConfig, TheaBrowserService


def interactive_demo():
    """Interactive demo with visible browser."""

    print()
    print("=" * 70)
    print("🎬 INTERACTIVE THEA AUTOMATION DEMO")
    print("=" * 70)
    print()

    # Initialize browser (visible)
    print("🚀 Step 1: Opening browser...")
    config = BrowserConfig(headless=False)
    browser = TheaBrowserService(config)

    if not browser.initialize():
        print("❌ Browser initialization failed")
        return

    print("✅ Browser opened!")
    print()

    # Navigate to ChatGPT
    print("🌐 Step 2: Navigating to ChatGPT...")
    chatgpt_url = "https://chatgpt.com/"

    if not browser.navigate_to(chatgpt_url, wait_seconds=3):
        print("❌ Navigation failed")
        browser.close()
        return

    print(f"✅ Navigated to {chatgpt_url}")
    print(f"   Current URL: {browser.get_current_url()}")
    print()

    # Check login status
    print("🔐 Step 3: Checking login status...")
    current_url = browser.get_current_url()

    if "auth" in current_url or "login" in current_url:
        print("⚠️  Not logged in - manual login required")
        print()
        print("=" * 70)
        print("👉 PLEASE LOG IN TO CHATGPT IN THE BROWSER WINDOW")
        print("=" * 70)
        print()
        print("I'll wait 60 seconds for you to log in...")
        print("(Browser will stay open)")
        print()

        time.sleep(60)

        print("✅ Login wait complete")
        print(f"   Current URL: {browser.get_current_url()}")
    else:
        print("✅ Already logged in!")

    print()

    # Prepare message
    print("📝 Step 4: Preparing message...")
    message = """Hello! This is Agent-3 demonstrating the V2 consolidated Thea browser service!

You should see this message appear in the ChatGPT interface through automated browser control.

🐝 WE ARE SWARM!"""

    print(f"   Message: {message[:80]}...")
    print()

    # Send using PyAutoGUI
    print("💬 Step 5: Sending message via PyAutoGUI...")
    print("   (Watch the browser - message will be pasted and sent!)")
    print()

    try:
        import pyautogui
        import pyperclip

        # Copy to clipboard
        pyperclip.copy(message)
        print("   📋 Message copied to clipboard")
        time.sleep(1)

        # Focus might be needed - click in the browser window first
        print("   ⌨️  Pasting message...")
        pyautogui.hotkey("ctrl", "v")
        time.sleep(2)

        print("   📨 Sending message...")
        pyautogui.press("enter")
        time.sleep(2)

        print("✅ Message sent!")
        print()

    except ImportError:
        print("❌ PyAutoGUI not available")
        print()
    except Exception as e:
        print(f"❌ Send error: {e}")
        print()

    # Keep browser open to see result
    print("=" * 70)
    print("👀 BROWSER WILL STAY OPEN FOR 30 SECONDS")
    print("=" * 70)
    print()
    print("Watch for Thea's response in the browser window!")
    print()
    print("Countdown:")

    for i in range(30, 0, -5):
        print(f"   {i} seconds remaining...")
        time.sleep(5)

    print()
    print("🧹 Closing browser...")
    browser.close()
    print("✅ Browser closed")
    print()

    print("=" * 70)
    print("✅ DEMO COMPLETE!")
    print("=" * 70)
    print()
    print("You witnessed:")
    print("  1. ✅ Browser opening automatically")
    print("  2. ✅ Navigation to ChatGPT")
    print("  3. ✅ Login detection")
    print("  4. ✅ Message pasted via clipboard (PyAutoGUI)")
    print("  5. ✅ Message sent via Enter key")
    print("  6. ✅ Browser stayed open to show result")
    print()
    print("🐝 WE ARE SWARM - Thea automation demonstrated!")
    print()


if __name__ == "__main__":
    print()
    print("🎬 Starting INTERACTIVE Thea automation demo...")
    print()
    print("⚠️  IMPORTANT:")
    print("   - Browser will open VISIBLY")
    print("   - You may need to log in manually if not already logged in")
    print("   - Watch the browser window for the automation!")
    print()
    input("Press ENTER to start demo...")
    print()

    interactive_demo()

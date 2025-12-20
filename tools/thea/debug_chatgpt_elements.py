#!/usr/bin/env python3
"""
Debug ChatGPT page elements for automation.

Opens the Thea page and prints all input/textarea/button elements
to help identify the correct selectors for automation.
"""

import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.infrastructure.browser.browser_models import BrowserConfig, TheaConfig
from src.infrastructure.browser.thea_browser_service import TheaBrowserService


def debug_chatgpt_elements():
    """Debug ChatGPT page elements."""
    print("🔍 Starting ChatGPT element debugging...")

    # Initialize browser
    cfg = BrowserConfig(headless=False)  # Visible for debugging
    svc = TheaBrowserService(cfg)

    if not svc.initialize():
        print("❌ Browser initialization failed")
        return

    print("✅ Browser initialized")

    # Navigate to Thea
    print(f"🌐 Navigating to: {svc.thea_config.conversation_url}")
    if not svc.navigate_to(svc.thea_config.conversation_url, wait_seconds=5):
        print("❌ Navigation failed")
        svc.close()
        return

    print("✅ Page loaded")

    # Wait for page to stabilize
    print("⏳ Waiting 5 seconds for page to stabilize...")
    time.sleep(5)

    # Get all relevant elements
    print("\n🎯 ANALYZING PAGE ELEMENTS")
    print("=" * 50)

    # Text inputs
    print("\n📝 TEXTAREA ELEMENTS:")
    textareas = svc.driver.find_elements("tag name", "textarea")
    for i, ta in enumerate(textareas):
        try:
            attrs = {}
            for attr in ['id', 'class', 'name', 'placeholder', 'aria-label', 'data-testid', 'role']:
                value = ta.get_attribute(attr)
                if value:
                    attrs[attr] = value

            print(f"  [{i}] Tag: textarea")
            print(f"      Attributes: {attrs}")
            print(f"      Location: {ta.location}")
            print(f"      Size: {ta.size}")
            print(f"      Visible: {ta.is_displayed()}")
            print(f"      Enabled: {ta.is_enabled()}")
            print()
        except Exception as e:
            print(f"  [{i}] Error analyzing textarea: {e}")

    # Contenteditable divs
    print("\n🔲 CONTENTEDITABLE DIVS:")
    contenteditables = svc.driver.find_elements("css selector", "div[contenteditable='true']")
    for i, div in enumerate(contenteditables):
        try:
            attrs = {}
            for attr in ['id', 'class', 'name', 'placeholder', 'aria-label', 'data-testid', 'role']:
                value = div.get_attribute(attr)
                if value:
                    attrs[attr] = value

            print(f"  [{i}] Tag: div[contenteditable='true']")
            print(f"      Attributes: {attrs}")
            print(f"      Location: {div.location}")
            print(f"      Size: {div.size}")
            print(f"      Visible: {div.is_displayed()}")
            print(f"      Enabled: {div.is_enabled()}")
            print(f"      Text: {div.text[:50] if div.text else 'None'}...")
            print()
        except Exception as e:
            print(f"  [{i}] Error analyzing contenteditable div: {e}")

    # Button elements
    print("\n🔘 BUTTON ELEMENTS:")
    buttons = svc.driver.find_elements("tag name", "button")
    for i, btn in enumerate(buttons[:10]):  # Limit to first 10
        try:
            attrs = {}
            for attr in ['id', 'class', 'name', 'type', 'aria-label', 'data-testid', 'role']:
                value = btn.get_attribute(attr)
                if value:
                    attrs[attr] = value

            print(f"  [{i}] Tag: button")
            print(f"      Attributes: {attrs}")
            print(f"      Location: {btn.location}")
            print(f"      Size: {btn.size}")
            print(f"      Visible: {btn.is_displayed()}")
            print(f"      Enabled: {btn.is_enabled()}")
            print(f"      Text: {btn.text[:30] if btn.text else 'None'}")
            print()
        except Exception as e:
            print(f"  [{i}] Error analyzing button: {e}")

    # Role=button elements
    print("\n🎭 ROLE=BUTTON ELEMENTS:")
    role_buttons = svc.driver.find_elements("css selector", "[role='button']")
    for i, btn in enumerate(role_buttons[:10]):  # Limit to first 10
        try:
            attrs = {}
            for attr in ['id', 'class', 'name', 'type', 'aria-label', 'data-testid', 'role']:
                value = btn.get_attribute(attr)
                if value:
                    attrs[attr] = value

            print(f"  [{i}] Tag: {btn.tag_name}[role='button']")
            print(f"      Attributes: {attrs}")
            print(f"      Location: {btn.location}")
            print(f"      Size: {btn.size}")
            print(f"      Visible: {btn.is_displayed()}")
            print(f"      Enabled: {btn.is_enabled()}")
            print(f"      Text: {btn.text[:30] if btn.text else 'None'}")
            print()
        except Exception as e:
            print(f"  [{i}] Error analyzing role=button: {e}")

    print("\n✅ Element analysis complete")
    print("💡 Use the selectors above to update the Thea automation code")
    print("🔍 Look for elements with location Y > 500 (near bottom of page)")

    # Keep browser open for manual inspection
    input("\n🔍 Press Enter to close browser and exit...")

    svc.close()
    print("✅ Browser closed")


if __name__ == "__main__":
    debug_chatgpt_elements()

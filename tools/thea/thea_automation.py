#!/usr/bin/env python3
"""
Thea Automation - Unified Cookie & Communication System
========================================================

Single, clean implementation for autonomous agent-to-agent communication with Thea.
No duplicates, no complexity - just working automation.

Features:
- Cookie-based session persistence (no repeated logins)
- Automatic login detection
- Message sending and response capture
- Autonomous operation with minimal manual intervention

Usage:
    from thea_automation import TheaAutomation

    # Initialize
    thea = TheaAutomation()

    # Send message and get response
    response = thea.send_message("Hello Thea!")
    print(response)
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# PyAutoGUI for message sending
try:
    import pyautogui
    import pyperclip

    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

# Response detector
try:
    from response_detector import ResponseDetector, ResponseWaitResult

    DETECTOR_AVAILABLE = True
except ImportError:
    DETECTOR_AVAILABLE = False


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TheaConfig:
    """Configuration for Thea automation."""

    thea_url: str = "https://chatgpt.com/g/g-67f437d96d7c81918b2dbc12f0423867-thea-manager"
    cookie_file: str = "thea_cookies.json"
    responses_dir: str = "thea_responses"
    headless: bool = False
    timeout: int = 120


class TheaAutomation:
    """
    Unified Thea automation system.

    Handles everything: cookies, login, messaging, and response capture.
    """

    def __init__(self, config: TheaConfig | None = None):
        """Initialize Thea automation."""
        self.config = config or TheaConfig()
        self.cookie_file = Path(self.config.cookie_file)
        self.responses_dir = Path(self.config.responses_dir)
        self.responses_dir.mkdir(exist_ok=True)

        self.driver = None
        self.detector = None

        # Check dependencies
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required: pip install selenium")
        if not PYAUTOGUI_AVAILABLE:
            raise ImportError("PyAutoGUI is required: pip install pyautogui pyperclip")
        if not DETECTOR_AVAILABLE:
            logger.warning("ResponseDetector not available - response capture may not work")

    # ========================================================================
    # COOKIE MANAGEMENT
    # ========================================================================

    def save_cookies(self) -> bool:
        """Save cookies from current session."""
        try:
            if not self.driver:
                return False

            cookies = self.driver.get_cookies()

            # Filter for ChatGPT/OpenAI cookies only
            auth_cookies = []
            for cookie in cookies:
                domain = cookie.get("domain", "").lower()
                name = cookie.get("name", "").lower()

                # Keep authentication-related cookies
                if any(d in domain for d in ["chatgpt.com", "openai.com"]):
                    # Skip analytics
                    if not any(skip in name for skip in ["_ga", "_gid", "_gat"]):
                        auth_cookies.append(cookie)

            # Save to file
            self.cookie_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cookie_file, "w", encoding="utf-8") as f:
                json.dump(auth_cookies, f, indent=2)

            logger.info(f"✅ Saved {len(auth_cookies)} cookies to {self.cookie_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")
            return False

    def load_cookies(self) -> bool:
        """Load cookies into current session."""
        try:
            if not self.driver or not self.cookie_file.exists():
                return False

            with open(self.cookie_file, encoding="utf-8") as f:
                cookies = json.load(f)

            # Load cookies
            loaded = 0
            for cookie in cookies:
                try:
                    if "name" in cookie and "value" in cookie:
                        self.driver.add_cookie(cookie)
                        loaded += 1
                except Exception as e:
                    logger.debug(f"Skipped cookie: {e}")

            logger.info(f"✅ Loaded {loaded} cookies from {self.cookie_file}")
            return loaded > 0

        except Exception as e:
            logger.error(f"Failed to load cookies: {e}")
            return False

    def has_valid_cookies(self) -> bool:
        """Check if valid cookies exist."""
        if not self.cookie_file.exists():
            return False

        try:
            with open(self.cookie_file, encoding="utf-8") as f:
                cookies = json.load(f)

            # Check for unexpired cookies
            current_time = time.time()
            valid_cookies = []

            for cookie in cookies:
                expiry = cookie.get("expiry")
                if not expiry or expiry > current_time:
                    valid_cookies.append(cookie)

            return len(valid_cookies) > 0

        except Exception:
            return False

    # ========================================================================
    # BROWSER & LOGIN
    # ========================================================================

    def start_browser(self) -> bool:
        """Initialize browser."""
        try:
            logger.info("🚀 Starting browser...")

            options = Options()
            if self.config.headless:
                options.add_argument("--headless=new")

            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

            self.driver = webdriver.Chrome(options=options)
            logger.info("✅ Browser started")
            return True

        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False

    def is_logged_in(self) -> bool:
        """Check if logged in to ChatGPT."""
        try:
            if not self.driver:
                return False

            # Look for textarea (message input)
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            visible_textareas = [ta for ta in textareas if ta.is_displayed()]

            if visible_textareas:
                return True

            # Look for send button
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for btn in buttons:
                try:
                    if btn.is_displayed() and "send" in str(btn.text or "").lower():
                        return True
                except:
                    continue

            return False

        except Exception as e:
            logger.debug(f"Login check error: {e}")
            return False

    def ensure_login(self) -> bool:
        """Ensure we're logged in to Thea."""
        try:
            logger.info("🔐 Checking login status...")

            # Navigate to ChatGPT first (for cookie loading)
            self.driver.get("https://chatgpt.com")
            time.sleep(2)

            # Try loading cookies if available
            if self.has_valid_cookies():
                logger.info("🍪 Loading saved cookies...")
                self.load_cookies()
                self.driver.refresh()
                time.sleep(3)

            # Navigate to Thea
            self.driver.get(self.config.thea_url)
            time.sleep(3)

            # Check if logged in
            if self.is_logged_in():
                logger.info("✅ Already logged in")
                return True

            # Manual login required
            logger.info("👤 Manual login required")
            logger.info("🔐 Please log in to ChatGPT in the browser")
            logger.info("⏰ Waiting for login (60 seconds)...")

            start_time = time.time()
            while time.time() - start_time < 60:
                if self.is_logged_in():
                    logger.info("✅ Login detected!")

                    # Save cookies
                    logger.info("🍪 Saving cookies...")
                    self.save_cookies()

                    # Navigate to Thea
                    self.driver.get(self.config.thea_url)
                    time.sleep(3)

                    return True

                time.sleep(2)

            logger.error("❌ Login timeout")
            return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    # ========================================================================
    # MESSAGING
    # ========================================================================

    def send_message(self, message: str, wait_for_response: bool = True) -> str | None:
        """
        Send message to Thea and optionally wait for response.

        Args:
            message: Message to send
            wait_for_response: Whether to wait for and capture response

        Returns:
            Response text if wait_for_response=True, else None
        """
        try:
            # Start browser if not already running
            if not self.driver:
                if not self.start_browser():
                    return None

            # Ensure logged in
            if not self.ensure_login():
                return None

            # Send message via clipboard paste
            logger.info(f"📤 Sending message: {message[:50]}...")
            pyperclip.copy(message)
            time.sleep(0.5)

            # Paste and send
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.5)
            pyautogui.press("enter")
            logger.info("✅ Message sent")

            # Wait for response if requested
            if wait_for_response:
                return self.wait_for_response()

            return None

        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None

    def wait_for_response(self) -> str | None:
        """Wait for and capture Thea's response."""
        try:
            logger.info("⏳ Waiting for response...")

            if not DETECTOR_AVAILABLE:
                logger.warning("ResponseDetector not available - manual wait")
                time.sleep(10)
                return "⚠️ Response detection not available"

            if not self.detector:
                self.detector = ResponseDetector(self.driver)

            # Wait for response
            result = self.detector.wait_until_complete(
                timeout=self.config.timeout, stable_secs=3.0, auto_continue=True
            )

            if result == ResponseWaitResult.COMPLETE:
                logger.info("✅ Response complete")
                response = self.detector.get_last_response_text()
                return response
            else:
                logger.warning(f"⚠️ Response status: {result}")
                response = self.detector.get_last_response_text()
                return response or f"⚠️ Response incomplete: {result}"

        except Exception as e:
            logger.error(f"Failed to capture response: {e}")
            return None

    def save_conversation(self, message: str, response: str) -> str:
        """Save conversation to file."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = self.responses_dir / f"conversation_{timestamp}.json"

            data = {
                "timestamp": timestamp,
                "message": message,
                "response": response,
                "thea_url": self.config.thea_url,
            }

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Saved to: {filename}")
            return str(filename)

        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
            return ""

    # ========================================================================
    # HIGH-LEVEL API
    # ========================================================================

    def communicate(self, message: str, save: bool = True) -> dict:
        """
        Complete communication cycle: send message and get response.

        Args:
            message: Message to send to Thea
            save: Whether to save the conversation

        Returns:
            dict with 'success', 'message', 'response', 'file' keys
        """
        result = {"success": False, "message": message, "response": "", "file": ""}

        try:
            # Send message and get response
            response = self.send_message(message, wait_for_response=True)

            if response:
                result["response"] = response
                result["success"] = True

                # Save if requested
                if save:
                    result["file"] = self.save_conversation(message, response)

            return result

        except Exception as e:
            result["response"] = f"Error: {e}"
            return result

    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("✅ Browser closed")
            except Exception as e:
                logger.debug(f"Error closing browser: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


# ============================================================================
# SIMPLE CLI
# ============================================================================


def main():
    """Simple CLI for testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Thea Automation")
    parser.add_argument("--message", required=True, help="Message to send")
    parser.add_argument("--headless", action="store_true", help="Headless mode")

    args = parser.parse_args()

    print("🐝 V2_SWARM THEA AUTOMATION")
    print("=" * 50)

    config = TheaConfig(headless=args.headless)

    with TheaAutomation(config) as thea:
        result = thea.communicate(args.message)

        print()
        if result["success"]:
            print("✅ SUCCESS!")
            print(f"\n📤 Message: {result['message']}")
            print(f"\n📥 Response: {result['response'][:500]}...")
            if result["file"]:
                print(f"\n💾 Saved: {result['file']}")
        else:
            print("❌ FAILED!")
            print(f"Error: {result['response']}")


if __name__ == "__main__":
    main()

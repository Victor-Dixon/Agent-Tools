#!/usr/bin/env python3
"""
Simple Thea Communication - Send & Receive
===========================================

Focus: Send prompt to Thea and capture response.
Fully automated login detection and cookie persistence.

Usage:
    python simple_thea_communication.py --message "Your message here"
    python simple_thea_communication.py --message "Hello Thea" --headless
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

import pyautogui
import pyperclip

from response_detector import ResponseDetector, ResponseWaitResult

# Import our modular login handler - import from root directory
import sys
import os

# Add browser directory to path for cookie manager
browser_dir = os.path.join(os.path.dirname(__file__), 'src', 'infrastructure', 'browser')
sys.path.insert(0, browser_dir)

# Import cookie manager from browser directory
from thea_cookie_manager import TheaCookieManager

# Import login handler from root directory (where the working implementation is)
root_dir = os.path.dirname(__file__)
sys.path.insert(0, root_dir)
from thea_login_handler import create_thea_login_handler


class SimpleTheaCommunication:
    """Simple send/receive communication with Thea."""

    def __init__(self, username=None, password=None, use_selenium=True, headless=False):
        self.thea_url = "https://chatgpt.com/g/g-67f437d96d7c81918b2dbc12f0423867-thea-manager"
        self.responses_dir = Path("thea_responses")
        self.responses_dir.mkdir(exist_ok=True)

        # Login configuration
        self.username = username
        self.password = password
        self.use_selenium = use_selenium
        self.headless = headless

        # Initialize components
        self.login_handler = create_thea_login_handler(
            username=username, password=password, cookie_file="thea_cookies.json"
        )
        self.cookie_manager = TheaCookieManager("thea_cookies.json")

        # Selenium driver (initialized when needed)
        self.driver = None
        self.detector = None

        # Check if Selenium is available
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options

            self.selenium_available = True
        except ImportError:
            self.selenium_available = False
            if use_selenium:
                print("❌ Selenium not available - automation required (pip install selenium)")
                self.use_selenium = False

    def initialize_driver(self):
        """Initialize Selenium WebDriver."""
        if not self.selenium_available or not self.use_selenium:
            return False

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options

            print("🚀 INITIALIZING SELENIUM DRIVER")
            print("-" * 35)

            # Configure Chrome options
            options = Options()
            if self.headless:
                print("🫥 HEADLESS MODE: Configuring browser to run invisibly...")
                options.add_argument("--headless=new")
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-plugins")
                options.add_argument("--disable-images")
                options.add_argument("--disable-web-security")
                options.add_argument("--disable-features=VizDisplayCompositor")
                options.add_argument("--remote-debugging-port=9222")
            else:
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")

            # Use Selenium Manager to auto-resolve ChromeDriver
            self.driver = webdriver.Chrome(options=options)
            print("✅ Chrome driver initialized (Selenium Manager)")
            return True

        except Exception as e:
            print(f"❌ Failed to initialize driver: {e}")
            return False

    def ensure_login(self) -> bool:
        """Ensure we're logged into Thea using cookies."""
        try:
            print("🔐 CHECKING LOGIN STATUS")
            print("-" * 25)

            # Navigate to Thea
            self.driver.get(self.thea_url)
            time.sleep(3)

            # Try to use saved cookies
            if self.cookie_manager.has_valid_cookies():
                print("🍪 Loading saved cookies...")
                
                # Need to be on the domain to load cookies
                self.driver.get("https://chatgpt.com")
                time.sleep(2)
                
                self.cookie_manager.load_cookies(self.driver)
                print("✅ Cookies loaded")
                
                # Navigate to Thea after loading cookies
                self.driver.get(self.thea_url)
                time.sleep(3)

                # Check if login worked
                if self.login_handler._is_logged_in(self.driver):
                    print("✅ Already logged in with cookies")
                    return True
                else:
                    print("⚠️ Cookies didn't work, need manual login")

            # Fall back to manual login
            print("👤 Manual login required")
            print("🔐 Please log in to ChatGPT in the browser window")
            print("⏰ Waiting for login (60 seconds)...")

            start_time = time.time()
            while time.time() - start_time < 60:
                if self.login_handler._is_logged_in(self.driver):
                    print("✅ Login detected!")
                    
                    # Save cookies for next time
                    print("🍪 Saving cookies for future use...")
                    self.cookie_manager.save_cookies(self.driver)
                    print("✅ Cookies saved")
                    
                    return True
                time.sleep(2)

            print("❌ Login timeout")
            return False

        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def send_message(self, message: str) -> bool:
        """Send a message to Thea using PyAutoGUI."""
        try:
            print("📤 SENDING MESSAGE TO THEA")
            print("-" * 30)
            print(f"💬 Message: {message}")

            # Copy message to clipboard
            pyperclip.copy(message)
            print("📋 Message copied to clipboard")

            # Wait a moment
            time.sleep(1)

            # Paste and send
            print("⌨️ Pasting message...")
            pyautogui.hotkey("ctrl", "v")
            time.sleep(0.5)

            print("📨 Sending message...")
            pyautogui.press("enter")
            print("✅ Message sent")

            return True

        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return False

    def wait_for_response(self, timeout: int = 120) -> str:
        """Wait for and capture Thea's response."""
        try:
            print("⏳ WAITING FOR RESPONSE")
            print("-" * 25)

            if not self.detector:
                self.detector = ResponseDetector(self.driver)

            # Wait for response to complete
            result = self.detector.wait_until_complete(
                timeout=timeout, stable_secs=3.0, auto_continue=True
            )

            if result == ResponseWaitResult.COMPLETE:
                print("✅ Response complete")
                response_text = self.detector.get_last_response_text()
                return response_text
            elif result == ResponseWaitResult.TIMEOUT:
                print("⏰ Response timeout")
                # Try to get partial response
                response_text = self.detector.get_last_response_text()
                return response_text or "⏰ Response timeout - no text captured"
            else:
                print(f"⚠️ Response status: {result}")
                response_text = self.detector.get_last_response_text()
                return response_text or f"⚠️ Response incomplete: {result}"

        except Exception as e:
            print(f"❌ Failed to capture response: {e}")
            return f"❌ Error: {e}"

    def save_response(self, message: str, response: str) -> str:
        """Save the message and response to a file."""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = self.responses_dir / f"conversation_{timestamp}.json"

            data = {
                "timestamp": timestamp,
                "message": message,
                "response": response,
                "thea_url": self.thea_url,
            }

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"💾 Response saved to: {filename}")
            return str(filename)

        except Exception as e:
            print(f"⚠️ Failed to save response: {e}")
            return ""

    def communicate(self, message: str) -> dict:
        """
        Complete communication cycle: send message and get response.

        Returns:
            dict with 'success', 'message', 'response', 'file' keys
        """
        result = {
            "success": False,
            "message": message,
            "response": "",
            "file": "",
        }

        try:
            # Initialize driver
            if not self.initialize_driver():
                result["response"] = "Failed to initialize browser"
                return result

            # Ensure login
            if not self.ensure_login():
                result["response"] = "Failed to login"
                return result

            # Send message
            if not self.send_message(message):
                result["response"] = "Failed to send message"
                return result

            # Wait for and capture response
            response = self.wait_for_response()
            result["response"] = response

            # Save conversation
            if response:
                result["file"] = self.save_response(message, response)
                result["success"] = True

            return result

        except Exception as e:
            result["response"] = f"Error: {e}"
            return result

        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Browser closed")
            except Exception as e:
                print(f"⚠️ Error closing browser: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Simple Thea Communication")
    parser.add_argument("--message", type=str, required=True, help="Message to send to Thea")
    parser.add_argument("--username", type=str, help="ChatGPT username (optional)")
    parser.add_argument("--password", type=str, help="ChatGPT password (optional)")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")

    args = parser.parse_args()

    print("🐝 V2_SWARM THEA COMMUNICATION")
    print("=" * 50)
    print()

    try:
        comm = SimpleTheaCommunication(
            username=args.username, password=args.password, headless=args.headless
        )

        result = comm.communicate(args.message)

        print()
        print("=" * 50)
        if result["success"]:
            print("🎉 COMMUNICATION SUCCESSFUL!")
            print()
            print("📤 YOUR MESSAGE:")
            print(f"   {result['message']}")
            print()
            print("📥 THEA'S RESPONSE:")
            print(f"   {result['response'][:500]}...")  # Show first 500 chars
            print()
            if result["file"]:
                print(f"💾 Full conversation saved to: {result['file']}")
        else:
            print("❌ COMMUNICATION FAILED!")
            print(f"   {result['response']}")

    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
    except Exception as e:
        print(f"\n💥 ERROR: {e}")


if __name__ == "__main__":
    main()

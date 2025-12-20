#!/usr/bin/env python3
"""
Discord Web Interface Test Automation
=====================================

Automates testing Discord bot commands via Discord web interface.
Uses browser automation to interact with Discord web client.

Author: Agent-6 (Coordination & Communication Specialist)
Date: 2025-01-27
Status: Discord Web Test Automation Tool
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import List, Dict, Any

# Try to import browser automation tools
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("⚠️  pyautogui not available - some features may be limited")

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  selenium not available - install with: pip install selenium")

logger = logging.getLogger(__name__)


class DiscordWebTester:
    """
    Automates Discord bot command testing via web interface.
    
    Usage:
        1. Navigate to Discord web interface
        2. Select channel
        3. Type commands
        4. Verify responses
    """
    
    def __init__(self, discord_url: str = "https://discord.com/channels/@me"):
        """Initialize Discord web tester."""
        self.discord_url = discord_url
        self.driver = None
        self.test_results = []
        
    def start_browser(self):
        """Start browser and navigate to Discord."""
        if not SELENIUM_AVAILABLE:
            raise ImportError("selenium not available - install with: pip install selenium")
        
        try:
            # Use Chrome (adjust for your browser)
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            
            chrome_options = Options()
            # Uncomment to run headless (no visible browser)
            # chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.get(self.discord_url)
            logger.info("✅ Browser opened and navigated to Discord")
            return True
        except Exception as e:
            logger.error(f"Error starting browser: {e}")
            return False
    
    def wait_for_login(self, timeout: int = 60):
        """Wait for user to log in to Discord."""
        print("\n🔐 Please log in to Discord in the browser window...")
        print(f"⏳ Waiting up to {timeout} seconds for login...")
        
        # Wait for Discord to load (look for channel list or message input)
        wait = WebDriverWait(self.driver, timeout)
        try:
            # Wait for message input to appear (indicates logged in)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][role='textbox']")))
            print("✅ Logged in to Discord!")
            time.sleep(2)  # Additional wait for full load
            return True
        except Exception as e:
            print(f"❌ Login timeout or error: {e}")
            return False
    
    def select_channel(self, channel_name: str):
        """Select a Discord channel by name."""
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # Find channel in sidebar by text content
            channel_selector = f"//div[contains(text(), '{channel_name}')]"
            channel = wait.until(EC.element_to_be_clickable((By.XPATH, channel_selector)))
            channel.click()
            
            print(f"✅ Selected channel: {channel_name}")
            time.sleep(1)  # Wait for channel to load
            return True
        except Exception as e:
            logger.error(f"Error selecting channel {channel_name}: {e}")
            return False
    
    def find_message_input(self):
        """Find the Discord message input box."""
        try:
            wait = WebDriverWait(self.driver, 10)
            # Discord message input selector
            message_input = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[contenteditable='true'][role='textbox'][data-slate-editor='true']")
            ))
            return message_input
        except:
            # Fallback selector
            try:
                wait = WebDriverWait(self.driver, 10)
                message_input = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[contenteditable='true'][role='textbox']")
                ))
                return message_input
            except Exception as e:
                logger.error(f"Error finding message input: {e}")
                return None
    
    def send_command(self, command: str) -> bool:
        """
        Send a Discord command message.
        
        Args:
            command: The command to send (e.g., "!status", "!help")
            
        Returns:
            True if command was sent successfully
        """
        try:
            message_input = self.find_message_input()
            if not message_input:
                print(f"❌ Could not find message input for command: {command}")
                return False
            
            # Click on input to focus
            message_input.click()
            time.sleep(0.5)
            
            # Type command
            message_input.send_keys(command)
            time.sleep(0.5)
            
            # Press Enter to send
            message_input.send_keys(Keys.RETURN)
            time.sleep(1)  # Wait for message to send
            
            print(f"✅ Sent command: {command}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending command {command}: {e}")
            print(f"❌ Error sending command {command}: {e}")
            return False
    
    def wait_for_response(self, timeout: int = 10):
        """Wait for bot response (check for bot messages)."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            # Wait for new message (bot response)
            # This is a simplified check - you may need to adjust selector
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[class*='message'][class*='bot']")
            ))
            return True
        except:
            # Bot might respond, or timeout
            return False
    
    def test_command(self, command: str, wait_time: int = 3) -> Dict[str, Any]:
        """
        Test a single Discord command.
        
        Args:
            command: The command to test
            wait_time: Time to wait for response (seconds)
            
        Returns:
            Test result dictionary
        """
        result = {
            "command": command,
            "sent": False,
            "response_received": False,
            "success": False,
            "error": None,
        }
        
        try:
            # Send command
            result["sent"] = self.send_command(command)
            
            if result["sent"]:
                # Wait for response
                time.sleep(wait_time)
                result["response_received"] = self.wait_for_response(timeout=TimeoutConstants.HTTP_QUICK)
                result["success"] = result["response_received"]
            else:
                result["error"] = "Failed to send command"
                
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error testing command {command}: {e}")
        
        self.test_results.append(result)
        return result
    
    def test_all_commands(self, commands: List[str], channel: str = None):
        """
        Test multiple Discord commands.
        
        Args:
            commands: List of commands to test
            channel: Channel name to select (optional)
        """
        print(f"\n🧪 Testing {len(commands)} Discord commands...\n")
        
        # Select channel if specified
        if channel:
            self.select_channel(channel)
        
        results = []
        for i, command in enumerate(commands, 1):
            print(f"\n[{i}/{len(commands)}] Testing: {command}")
            result = self.test_command(command, wait_time=3)
            results.append(result)
            
            # Status indicator
            if result["success"]:
                print(f"   ✅ Success")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        
        return results
    
    def close(self):
        """Close browser."""
        if self.driver:
            self.driver.quit()
            logger.info("✅ Browser closed")
    
    def print_results(self):
        """Print test results summary."""
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total - passed
        
        print(f"\nTotal Commands Tested: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        print("\n" + "-" * 60)
        print("Detailed Results:")
        print("-" * 60)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['command']}")
            if result.get("error"):
                print(f"   Error: {result['error']}")
        
        print("=" * 60 + "\n")


def main():
    """Main test execution."""
    print("=" * 60)
    print("🤖 Discord Web Interface Test Automation")
    print("=" * 60)
    
    if not SELENIUM_AVAILABLE:
        print("\n❌ Selenium not available!")
        print("   Install with: pip install selenium")
        print("   Also install ChromeDriver: https://chromedriver.chromium.org/")
        return 1
    
    # Commands to test
    test_commands = [
        "!help",
        "!control",
        "!status",
        "!gui",
        "!swarm_tasks",
        "!swarm_overview",
        # Add more commands as needed
    ]
    
    # Initialize tester
    tester = DiscordWebTester()
    
    try:
        # Start browser
        print("\n🌐 Opening browser...")
        if not tester.start_browser():
            print("❌ Failed to start browser")
            return 1
        
        # Wait for login
        if not tester.wait_for_login(timeout=TimeoutConstants.HTTP_LONG):
            print("❌ Login timeout")
            return 1
        
        # Ask user for channel
        print("\n channel selection...")
        channel = input("Enter channel name to test in (or press Enter to use current): ").strip()
        channel = channel if channel else None
        
        if channel:
            tester.select_channel(channel)
        else:
            print("Using current channel...")
        
        # Test commands
        print("\n🧪 Starting command tests...")
        print("   (Commands will be sent automatically - watch for bot responses)\n")
        results = tester.test_all_commands(test_commands, channel=None)
        
        # Print results
        tester.print_results()
        
        return 0 if all(r["success"] for r in results) else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Test error: {e}")
        print(f"\n❌ Test error: {e}")
        return 1
    finally:
        # Close browser
        input("\nPress Enter to close browser...")
        tester.close()


if __name__ == "__main__":
    import sys
from src.core.config.timeout_constants import TimeoutConstants
    sys.exit(main())





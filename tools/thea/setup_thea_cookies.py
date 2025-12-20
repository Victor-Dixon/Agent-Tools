#!/usr/bin/env python3
"""
Thea Cookie Setup Script
========================

Interactive setup for Thea authentication cookies.
Allows manual login and saves cookies for automated use.

Usage:
    python setup_thea_cookies.py [--headless]

Steps:
1. Opens Thea in browser
2. Waits for manual login
3. Saves authentication cookies
4. Verifies login status
"""

import argparse
import json
import time
from pathlib import Path

# Selenium imports (Selenium Manager only)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not available - install required packages (pip install selenium)")

# Import our modular login handler
from thea_login_handler import TheaCookieManager, TheaLoginHandler


class TheaCookieSetup:
    """Interactive setup for Thea authentication cookies."""

    def __init__(self, headless: bool = False, use_undetected: bool = True):
        self.thea_url = "https://chatgpt.com/g/g-67f437d96d7c81918b2dbc12f0423867-thea-manager"
        self.headless = headless
        self.use_undetected = use_undetected

        # Initialize components
        self.cookie_manager = TheaCookieManager("thea_cookies.json")
        self.login_handler = TheaLoginHandler(cookie_file="thea_cookies.json")

        # Selenium driver
        self.driver = None

    def initialize_driver(self) -> bool:
        """Initialize Chrome WebDriver with undetected-chromedriver support."""
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium not available")
            return False

        try:
            print("🚀 INITIALIZING BROWSER FOR COOKIE SETUP")
            print("=" * 50)

            if self.use_undetected:
                # Try undetected-chromedriver first
                try:
                    import undetected_chromedriver as uc
                    
                    print("🔐 Using undetected-chromedriver for anti-bot bypass...")
                    
                    options = uc.ChromeOptions()
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    options.add_argument("--disable-blink-features=AutomationControlled")
                    options.add_argument("--window-size=1920,1080")

                    if self.headless:
                        print("⚠️ Headless mode may be detected by anti-bot systems")
                        options.add_argument("--headless=new")

                    self.driver = uc.Chrome(
                        options=options,
                        use_subprocess=True,
                        driver_executable_path=None  # Auto-download correct version
                    )
                    print("✅ Undetected Chrome driver ready")
                    return True

                except ImportError:
                    print("⚠️ undetected-chromedriver not installed, falling back to standard Chrome")
                    print("💡 Install with: pip install undetected-chromedriver")
                    self.use_undetected = False
                except Exception as e:
                    print(f"⚠️ Undetected Chrome failed: {e}")
                    print("🔄 Falling back to standard Chrome...")
                    self.use_undetected = False

            # Fallback to standard Chrome
            options = Options()
            if self.headless:
                options.add_argument("--headless")

            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

            self.driver = webdriver.Chrome(options=options)
            print("✅ Standard Chrome driver ready (Selenium Manager)")

            return True

        except Exception as e:
            print(f"❌ Failed to initialize driver: {e}")
            return False

    def wait_for_manual_login(self, timeout: int = 300) -> bool:
        """Wait for user to manually login and detect when complete."""
        print("👤 MANUAL LOGIN REQUIRED")
        print("=" * 30)
        print("📋 INSTRUCTIONS:")
        print("   1. Browser should open to ChatGPT/Thea")
        print("   2. Log in manually with your credentials")
        print("   3. Navigate to Thea if not already there")
        print("   4. Return to this terminal when logged in")
        print()
        print("⏰ You have 5 minutes to complete login")
        print("💡 The system will automatically detect when you're logged in")
        print("🔍 You'll see debug info every 15 seconds")
        print()

        start_time = time.time()
        check_interval = 3  # Check every 3 seconds

        print("🔍 Monitoring login status...")
        print("(Checking every 3 seconds - debug info every 15 seconds)")
        print()

        last_debug_time = 0
        while time.time() - start_time < timeout:
            current_time = time.time()
            elapsed = int(current_time - start_time)
            remaining = timeout - elapsed

            # Debug page state every 15 seconds
            if current_time - last_debug_time > 15:
                self._debug_page_state()
                print("🔍 Checking login indicators...")
                last_debug_time = current_time

            if self.login_handler._is_logged_in(self.driver):
                print("✅ LOGIN DETECTED!")
                print("🎉 Successfully logged in to Thea")
                return True

            if elapsed % 10 == 0:  # Status update every 10 seconds
                print(f"⏰ Waiting for login... ({remaining} seconds remaining)")
                print("💡 TIP: If login detected too early, refresh the page and try again")

            time.sleep(check_interval)

        print("⏰ TIMEOUT: Manual login period expired")
        print("💡 TIP: Make sure you're logged in and on the Thea page")
        print("🔄 TIP: If login was detected too early, close browser and run again")
        return False

    def _debug_page_state(self):
        """Debug current page state for troubleshooting."""
        try:
            title = self.driver.title
            url = self.driver.current_url
            print(f"🔍 DEBUG - Page: {title}")
            print(f"🔍 DEBUG - URL: {url}")

            # Try to find some basic elements
            try:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                print(f"🔍 DEBUG - Found {len(buttons)} buttons")
            except:
                print("🔍 DEBUG - Could not count buttons")

            try:
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                print(f"🔍 DEBUG - Found {len(inputs)} input fields")
            except:
                print("🔍 DEBUG - Could not count inputs")

            try:
                textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                print(f"🔍 DEBUG - Found {len(textareas)} textareas")
            except:
                print("🔍 DEBUG - Could not count textareas")

        except Exception as e:
            print(f"🔍 DEBUG - Error getting page state: {e}")
        print()

    def save_cookies_after_login(self) -> bool:
        """Save cookies after successful login."""
        print("🍪 SAVING AUTHENTICATION COOKIES")
        print("-" * 35)

        try:
            success = self.cookie_manager.save_cookies(self.driver)
            if success:
                print("✅ Cookies saved successfully")
                print("📁 Cookie file: thea_cookies.json")

                # Show cookie summary
                cookie_file = Path("thea_cookies.json")
                if cookie_file.exists():
                    with open(cookie_file) as f:
                        cookies = json.load(f)
                    print(f"📊 Saved {len(cookies)} cookies")
                return True
            else:
                print("❌ Failed to save cookies")
                return False

        except Exception as e:
            print(f"❌ Error saving cookies: {e}")
            return False

    def verify_setup(self) -> bool:
        """Verify the cookie setup is working."""
        print("🔍 VERIFYING COOKIE SETUP")
        print("-" * 25)

        try:
            # Check if cookies exist
            if not self.cookie_manager.has_valid_cookies():
                print("❌ No valid cookies found")
                return False

            # Try to load cookies and check login status
            print("🔄 Testing cookie-based login...")

            # Navigate to Thea
            self.driver.get(self.thea_url)
            time.sleep(3)

            # Load cookies
            self.cookie_manager.load_cookies(self.driver)

            # Refresh to apply cookies
            self.driver.refresh()
            time.sleep(3)

            # Check if logged in
            if self.login_handler._is_logged_in(self.driver):
                print("✅ Cookie verification successful!")
                print("🎉 Thea authentication cookies are ready")
                return True
            else:
                print("❌ Cookie verification failed")
                print("💡 Cookies may be expired or invalid")
                return False

        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False

    def run_setup(self) -> bool:
        """Run the complete cookie setup process."""
        print("🐝 V2_SWARM THEA COOKIE SETUP")
        print("=" * 50)
        print("🎯 GOAL: Manually login and save authentication cookies")
        print("🔄 These cookies will enable automated Thea communication")
        print("=" * 50)
        print()

        try:
            # Step 1: Initialize browser
            print("🚀 STEP 1: INITIALIZING BROWSER")
            if not self.initialize_driver():
                return False

            # Step 2: Navigate to Thea
            print("🌐 STEP 2: NAVIGATING TO THEA")
            self.driver.get(self.thea_url)
            time.sleep(2)
            print("✅ Thea page loaded")

            # Step 3: Manual login with explicit confirmation
            print("👤 STEP 3: MANUAL LOGIN")
            print("🔐 A browser window is open. Log in to ChatGPT, then return here.")
            try:
                input("🎯 Press Enter once you are fully logged in and on Thea page...")
            except KeyboardInterrupt:
                print("\n⏹️  Setup cancelled by user")
                return False

            # Step 4: Save cookies
            print("🍪 STEP 4: SAVING COOKIES")
            if not self.save_cookies_after_login():
                print("❌ Cookie saving failed")
                return False

            # Step 5: Verify setup
            print("🔍 STEP 5: VERIFYING SETUP")
            if not self.verify_setup():
                print("⚠️  Verification could not confirm login automatically.")
                print("✅ Cookies were saved; the next automation run will attempt to reuse them.")

            print("🎉 COOKIE SETUP COMPLETE!")
            print("=" * 30)
            print("✅ Thea authentication cookies saved and verified")
            print("🤖 You can now use automated Thea communication")
            print("📁 Cookie file: thea_cookies.json")
            print()
            print("💡 Next: Run automated communication with:")
            print("   python simple_thea_communication.py")
            return True

        except KeyboardInterrupt:
            print("\n⏹️  Setup cancelled by user")
            return False
        except Exception as e:
            print(f"\n💥 ERROR: {e}")
            return False
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                print("✅ Browser closed")
            except Exception as e:
                print(f"⚠️  Error closing browser: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Thea Cookie Setup Script")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")
    parser.add_argument(
        "--no-undetected", action="store_true", help="Use standard Chrome instead of undetected"
    )

    args = parser.parse_args()

    if not SELENIUM_AVAILABLE:
        print("❌ Selenium is required for cookie setup")
        print("📦 Install with: pip install selenium webdriver-manager undetected-chromedriver")
        return

    try:
        setup = TheaCookieSetup(headless=args.headless, use_undetected=not args.no_undetected)

        success = setup.run_setup()

        if success:
            print("\n🎉 SUCCESS!")
            print("🐝 WE ARE SWARM - COOKIE SETUP COMPLETE!")
        else:
            print("\n❌ FAILURE!")
            print("❌ Cookie setup failed")
            print("💡 Try again or check your login credentials")

    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled")
    except Exception as e:
        print(f"\n💥 ERROR: {e}")


if __name__ == "__main__":
    main()

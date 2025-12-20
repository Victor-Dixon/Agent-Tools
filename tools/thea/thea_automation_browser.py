#!/usr/bin/env python3
"""
Thea Automation - Browser & Login Management Module
===================================================

Handles browser initialization and login verification.

V2 Compliance: Single responsibility (browser/login operations only)
"""

import logging
import time

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

logger = logging.getLogger(__name__)


class TheaBrowserManager:
    """Manages browser lifecycle and login verification."""

    def __init__(self, headless: bool = False):
        """
        Initialize browser manager.

        Args:
            headless: Whether to run browser in headless mode
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required: pip install selenium")

        self.headless = headless
        self.driver = None

    def start_browser(self) -> bool:
        """
        Initialize and start Chrome browser.

        Returns:
            bool: True if browser started successfully
        """
        try:
            logger.info("🚀 Starting browser...")

            options = Options()
            if self.headless:
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
        """
        Check if logged in to ChatGPT.

        Returns:
            bool: True if logged in
        """
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

    def ensure_login(self, thea_url: str, cookie_manager, login_timeout: int = 60) -> bool:
        """
        Ensure we're logged in to Thea, with automatic cookie loading.

        Args:
            thea_url: URL to Thea ChatGPT instance
            cookie_manager: TheaCookieManager instance for cookie operations
            login_timeout: Timeout in seconds for manual login

        Returns:
            bool: True if login successful
        """
        try:
            logger.info("🔐 Checking login status...")

            # Navigate to ChatGPT first (for cookie loading)
            self.driver.get("https://chatgpt.com")
            time.sleep(2)

            # Try loading cookies if available
            if cookie_manager.has_valid_cookies():
                logger.info("🍪 Loading saved cookies...")
                cookie_manager.load_cookies()
                self.driver.refresh()
                time.sleep(3)

            # Navigate to Thea
            self.driver.get(thea_url)
            time.sleep(3)

            # Check if logged in
            if self.is_logged_in():
                logger.info("✅ Already logged in")
                return True

            # Manual login required
            return self._handle_manual_login(thea_url, cookie_manager, login_timeout)

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    def _handle_manual_login(self, thea_url: str, cookie_manager, login_timeout: int) -> bool:
        """
        Handle manual login process.

        Args:
            thea_url: URL to Thea ChatGPT instance
            cookie_manager: TheaCookieManager instance for cookie operations
            login_timeout: Timeout in seconds

        Returns:
            bool: True if login successful
        """
        logger.info("👤 Manual login required")
        logger.info("🔐 Please log in to ChatGPT in the browser")
        logger.info(f"⏰ Waiting for login ({login_timeout} seconds)...")

        start_time = time.time()
        while time.time() - start_time < login_timeout:
            if self.is_logged_in():
                logger.info("✅ Login detected!")

                # Save cookies
                logger.info("🍪 Saving cookies...")
                cookie_manager.save_cookies()

                # Navigate to Thea
                self.driver.get(thea_url)
                time.sleep(3)

                return True

            time.sleep(2)

        logger.error("❌ Login timeout")
        return False

    def cleanup(self):
        """Clean up browser resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("✅ Browser closed")
            except Exception as e:
                logger.debug(f"Error closing browser: {e}")

    def get_driver(self):
        """
        Get the WebDriver instance.

        Returns:
            WebDriver: The browser driver instance
        """
        return self.driver

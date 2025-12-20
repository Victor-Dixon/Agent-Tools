#!/usr/bin/env python3
"""
Thea Authentication Handler - V2 Compliance Module
==================================================

Authentication operations for Thea (automated/manual login).
Extracted from thea_login_handler.py (671 lines → <400 each)

Author: Agent-1 (Integration & Core Systems Specialist) - V2 Critical Fix
Created: 2025-10-10
License: MIT
"""

import logging
import time

# Selenium imports
try:
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from thea_cookie_manager import TheaCookieManager
from thea_login_detector import TheaLoginDetector

logger = logging.getLogger(__name__)


class TheaAuthenticationHandler:
    """Handles automated and manual login for Thea/ChatGPT."""

    def __init__(
        self,
        username: str = None,
        password: str = None,
        totp_secret: str = None,
        cookie_file: str = "thea_cookies.json",
    ):
        """Initialize authentication handler."""
        self.username = username
        self.password = password
        self.totp_secret = totp_secret
        self.cookie_manager = TheaCookieManager(cookie_file)
        self.login_detector = TheaLoginDetector()

    def ensure_login(self, driver, allow_manual: bool = True, manual_timeout: int = 60) -> bool:
        """Ensure user is logged in (automated or manual)."""
        try:
            # Try loading cookies first
            if self.cookie_manager.load_cookies(driver):
                driver.refresh()
                time.sleep(3)

                if self.login_detector.is_logged_in(driver):
                    logger.info("✅ Logged in via cookies")
                    return True

            # Try automated login if credentials provided
            if self.username and self.password:
                if self._automated_login(driver):
                    self.cookie_manager.save_cookies(driver)
                    return True

            # Fall back to manual login
            if allow_manual:
                if self._manual_login(driver, manual_timeout):
                    self.cookie_manager.save_cookies(driver)
                    return True

            return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    def _automated_login(self, driver) -> bool:
        """Perform automated login with credentials."""
        try:
            logger.info("Attempting automated login...")

            # Navigate to login page
            driver.get("https://chat.openai.com/auth/login")
            time.sleep(2)

            # Find and fill username
            username_field = driver.find_element(By.CSS_SELECTOR, "input[type='email']")
            username_field.send_keys(self.username)

            # Click continue
            continue_button = driver.find_element(
                By.XPATH, "//button[contains(text(), 'Continue')]"
            )
            continue_button.click()
            time.sleep(2)

            # Find and fill password
            password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            password_field.send_keys(self.password)

            # Click login
            login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue')]")
            login_button.click()
            time.sleep(5)

            # Handle 2FA if secret provided
            if self.totp_secret:
                self._handle_2fa(driver)

            # Check if login successful
            if self.login_detector.is_logged_in(driver):
                logger.info("✅ Automated login successful")
                return True

            return False

        except Exception as e:
            logger.error(f"Automated login failed: {e}")
            return False

    def _handle_2fa(self, driver):
        """Handle 2FA if required."""
        try:
            # Wait for 2FA input
            totp_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
            )

            # Generate TOTP code
            import pyotp

            totp = pyotp.TOTP(self.totp_secret)
            code = totp.now()

            # Enter code
            totp_field.send_keys(code)
            time.sleep(1)

            # Submit
            submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue')]")
            submit_button.click()
            time.sleep(3)

            logger.info("✅ 2FA handled")

        except Exception as e:
            logger.debug(f"2FA handling error (may not be required): {e}")

    def _manual_login(self, driver, timeout: int) -> bool:
        """Manual login fallback."""
        try:
            logger.info(f"⏰ Manual login required. You have {timeout} seconds...")
            logger.info("Please complete login in the browser window")

            start_time = time.time()
            while time.time() - start_time < timeout:
                time.sleep(2)
                if self.login_detector.is_logged_in(driver):
                    logger.info("✅ Manual login successful!")
                    return True

            logger.error("❌ Manual login timeout")
            return False

        except Exception as e:
            logger.error(f"Manual login error: {e}")
            return False

    def force_logout(self, driver) -> bool:
        """Force logout from Thea/ChatGPT."""
        try:
            # Find and click logout button
            logout_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Log out')]")
            logout_button.click()
            time.sleep(2)
            logger.info("✅ Logged out successfully")
            return True
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False


__all__ = ["TheaAuthenticationHandler"]

#!/usr/bin/env python3
"""
Thea Login Detector - V2 Compliance Module
==========================================

Login status detection logic for Thea/ChatGPT.
Extracted from thea_login_handler.py (massive _is_logged_in function)

Author: Agent-1 (Integration & Core Systems Specialist) - V2 Critical Fix
Created: 2025-10-10
License: MIT
"""

import logging

# Selenium imports
try:
    from selenium.common.exceptions import NoSuchElementException, TimeoutException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

logger = logging.getLogger(__name__)


class TheaLoginDetector:
    """Detects login status on Thea/ChatGPT pages."""

    def __init__(self):
        """Initialize login detector."""
        pass

    def is_logged_in(self, driver) -> bool:
        """
        Check if user is logged in to ChatGPT/Thea.

        This uses multiple detection methods to be robust.
        """
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium not available")
            return False

        try:
            current_url = driver.current_url
            logger.info(f"🔍 Checking login status on: {current_url}")

            # Method 1: Check URL patterns
            if self._check_url_patterns(current_url):
                return True

            # Method 2: Check for logout button
            if self._check_logout_button(driver):
                return True

            # Method 3: Check for user menu
            if self._check_user_menu(driver):
                return True

            # Method 4: Check for new chat button
            if self._check_new_chat_button(driver):
                return True

            # Method 5: Check for login/signup buttons (negative indicator)
            if self._check_login_buttons(driver):
                return False

            # Default: assume not logged in
            logger.warning("Could not definitively determine login status")
            return False

        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False

    def _check_url_patterns(self, url: str) -> bool:
        """Check URL patterns for login indicators."""
        if not url:
            return False

        # Logged in if on chat page (not auth page)
        if "chat.openai.com" in url and "/auth/" not in url:
            logger.info("✅ Logged in (URL pattern: chat.openai.com, not /auth/)")
            return True

        return False

    def _check_logout_button(self, driver) -> bool:
        """Check for logout button (indicates logged in)."""
        try:
            logout_selectors = [
                "//button[contains(text(), 'Log out')]",
                "//a[contains(text(), 'Log out')]",
                "//*[contains(@class, 'logout')]",
            ]

            for selector in logout_selectors:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        logger.info("✅ Logged in (found logout button)")
                        return True
                except NoSuchElementException:
                    continue

            return False
        except Exception:
            return False

    def _check_user_menu(self, driver) -> bool:
        """Check for user menu (indicates logged in)."""
        try:
            user_menu_selectors = [
                "//button[contains(@aria-label, 'User menu')]",
                "//*[contains(@class, 'user-menu')]",
                "//*[contains(@data-testid, 'user-menu')]",
            ]

            for selector in user_menu_selectors:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        logger.info("✅ Logged in (found user menu)")
                        return True
                except NoSuchElementException:
                    continue

            return False
        except Exception:
            return False

    def _check_new_chat_button(self, driver) -> bool:
        """Check for new chat button (indicates logged in)."""
        try:
            new_chat_selectors = [
                "//a[contains(text(), 'New chat')]",
                "//button[contains(text(), 'New chat')]",
                "//*[contains(@aria-label, 'New chat')]",
            ]

            for selector in new_chat_selectors:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        logger.info("✅ Logged in (found new chat button)")
                        return True
                except NoSuchElementException:
                    continue

            return False
        except Exception:
            return False

    def _check_login_buttons(self, driver) -> bool:
        """Check for login/signup buttons (negative indicator)."""
        try:
            login_selectors = [
                "//button[contains(text(), 'Log in')]",
                "//button[contains(text(), 'Sign up')]",
                "//a[contains(text(), 'Log in')]",
            ]

            for selector in login_selectors:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        logger.info("❌ Not logged in (found login button)")
                        return True
                except NoSuchElementException:
                    continue

            return False
        except Exception:
            return False


__all__ = ["TheaLoginDetector"]

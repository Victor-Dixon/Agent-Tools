#!/usr/bin/env python3
"""
Thea Automation - Cookie Management Module
==========================================

Handles cookie persistence for session management.

V2 Compliance: Single responsibility (cookie operations only)
"""

import json
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class TheaCookieManager:
    """Manages cookie persistence for Thea automation."""

    def __init__(self, driver, cookie_file: str | Path):
        """
        Initialize cookie manager.

        Args:
            driver: Selenium WebDriver instance
            cookie_file: Path to cookie storage file
        """
        self.driver = driver
        self.cookie_file = Path(cookie_file)

    def save_cookies(self) -> bool:
        """
        Save cookies from current session to file.

        Returns:
            bool: True if cookies were saved successfully
        """
        try:
            if not self.driver:
                return False

            cookies = self.driver.get_cookies()

            # Filter for ChatGPT/OpenAI cookies only
            auth_cookies = self._filter_auth_cookies(cookies)

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
        """
        Load cookies from file into current session.

        Returns:
            bool: True if cookies were loaded successfully
        """
        try:
            if not self.driver or not self.cookie_file.exists():
                return False

            with open(self.cookie_file, encoding="utf-8") as f:
                cookies = json.load(f)

            # Load cookies into driver
            loaded = self._load_cookies_into_driver(cookies)

            logger.info(f"✅ Loaded {loaded} cookies from {self.cookie_file}")
            return loaded > 0

        except Exception as e:
            logger.error(f"Failed to load cookies: {e}")
            return False

    def has_valid_cookies(self) -> bool:
        """
        Check if valid (non-expired) cookies exist in file.

        Returns:
            bool: True if valid cookies exist
        """
        if not self.cookie_file.exists():
            return False

        try:
            with open(self.cookie_file, encoding="utf-8") as f:
                cookies = json.load(f)

            # Check for unexpired cookies
            valid_cookies = self._filter_valid_cookies(cookies)
            return len(valid_cookies) > 0

        except Exception:
            return False

    def _filter_auth_cookies(self, cookies: list[dict]) -> list[dict]:
        """
        Filter cookies to keep only authentication-related ones.

        Args:
            cookies: List of cookie dictionaries

        Returns:
            list[dict]: Filtered cookies
        """
        auth_cookies = []
        for cookie in cookies:
            domain = cookie.get("domain", "").lower()
            name = cookie.get("name", "").lower()

            # Keep authentication-related cookies
            if any(d in domain for d in ["chatgpt.com", "openai.com"]):
                # Skip analytics
                if not any(skip in name for skip in ["_ga", "_gid", "_gat"]):
                    auth_cookies.append(cookie)

        return auth_cookies

    def _load_cookies_into_driver(self, cookies: list[dict]) -> int:
        """
        Load cookies into WebDriver.

        Args:
            cookies: List of cookie dictionaries

        Returns:
            int: Number of cookies successfully loaded
        """
        loaded = 0
        for cookie in cookies:
            try:
                if "name" in cookie and "value" in cookie:
                    self.driver.add_cookie(cookie)
                    loaded += 1
            except Exception as e:
                logger.debug(f"Skipped cookie: {e}")

        return loaded

    def _filter_valid_cookies(self, cookies: list[dict]) -> list[dict]:
        """
        Filter cookies to keep only non-expired ones.

        Args:
            cookies: List of cookie dictionaries

        Returns:
            list[dict]: Valid (non-expired) cookies
        """
        current_time = time.time()
        valid_cookies = []

        for cookie in cookies:
            expiry = cookie.get("expiry")
            if not expiry or expiry > current_time:
                valid_cookies.append(cookie)

        return valid_cookies

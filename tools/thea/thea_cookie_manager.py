#!/usr/bin/env python3
"""
Thea Cookie Manager - V2 Compliance Module
==========================================

Cookie persistence and session management for Thea.
Extracted from thea_login_handler.py (671 lines → <400 each)

Author: Agent-1 (Integration & Core Systems Specialist) - V2 Critical Fix
Created: 2025-10-10
License: MIT
"""

import json
import logging
from pathlib import Path

# Selenium imports
try:
    from selenium import webdriver

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

logger = logging.getLogger(__name__)


class TheaCookieManager:
    """Manages cookie persistence for Thea sessions."""

    def __init__(self, cookie_file: str = "thea_cookies.json"):
        """Initialize the cookie manager."""
        self.cookie_file = Path(cookie_file)
        self.cookie_file.parent.mkdir(parents=True, exist_ok=True)

    def save_cookies(self, driver) -> bool:
        """Save cookies from the current driver session."""
        try:
            if not SELENIUM_AVAILABLE:
                logger.warning("Selenium not available - cannot save cookies")
                return False

            cookies = driver.get_cookies()
            logger.info(f"🔍 Found {len(cookies)} total cookies from browser")

            # Filter and save cookies - be more permissive for ChatGPT
            persistent_cookies = []
            for cookie in cookies:
                cookie_name = cookie.get("name", "").lower()
                domain = cookie.get("domain", "").lower()

                # Skip analytics and tracking cookies
                skip_names = ["_ga", "_gid", "_gat", "__gads", "_fbp", "_fbc"]
                if any(skip_name in cookie_name for skip_name in skip_names):
                    continue

                # Save all cookies for openai.com domains
                if any(
                    chatgpt_domain in domain
                    for chatgpt_domain in ["openai.com", "chatgpt.com", "chat.openai.com"]
                ):
                    persistent_cookies.append(cookie)
                elif not domain or domain == "":  # Local cookies
                    persistent_cookies.append(cookie)

            # Save to file
            with open(self.cookie_file, "w", encoding="utf-8") as f:
                json.dump(persistent_cookies, f, indent=2)

            logger.info(f"✅ Saved {len(persistent_cookies)} cookies to {self.cookie_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")
            return False

    def load_cookies(self, driver) -> bool:
        """Load cookies into the driver session."""
        try:
            if not SELENIUM_AVAILABLE:
                logger.warning("Selenium not available - cannot load cookies")
                return False

            if not self.cookie_file.exists():
                logger.info("No cookie file found - skipping cookie load")
                return False

            with open(self.cookie_file, encoding="utf-8") as f:
                cookies = json.load(f)

            logger.info(f"🔍 Loading {len(cookies)} cookies from {self.cookie_file}")

            # Must be on the domain before adding cookies
            driver.get("https://chat.openai.com")

            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    logger.debug(f"Failed to add cookie {cookie.get('name')}: {e}")

            logger.info(f"✅ Loaded {len(cookies)} cookies")
            return True

        except Exception as e:
            logger.error(f"Failed to load cookies: {e}")
            return False

    def has_valid_cookies(self) -> bool:
        """Check if valid cookies exist."""
        try:
            if not self.cookie_file.exists():
                return False

            with open(self.cookie_file, encoding="utf-8") as f:
                cookies = json.load(f)

            if not cookies or len(cookies) == 0:
                return False

            # Check for authentication cookies
            auth_cookie_names = ["__Secure-next-auth.session-token", "__Host-next-auth.csrf-token"]
            has_auth_cookie = any(cookie.get("name") in auth_cookie_names for cookie in cookies)

            return has_auth_cookie

        except Exception:
            return False

    def clear_cookies(self) -> bool:
        """Clear saved cookies."""
        try:
            if self.cookie_file.exists():
                self.cookie_file.unlink()
                logger.info("✅ Cookies cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cookies: {e}")
            return False


__all__ = ["TheaCookieManager"]

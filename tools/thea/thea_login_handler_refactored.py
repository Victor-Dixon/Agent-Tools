#!/usr/bin/env python3
"""
Thea Login Handler - V2 Compliance Facade
=========================================

Unified facade for Thea authentication system.
Refactored from 671 lines → 3 modules (<200 lines each)

Author: Agent-1 (Integration & Core Systems Specialist) - V2 Critical Fix
Created: 2025-10-10
License: MIT
"""

import logging

from thea_authentication_handler import TheaAuthenticationHandler
from thea_cookie_manager import TheaCookieManager
from thea_login_detector import TheaLoginDetector

logger = logging.getLogger(__name__)


class TheaLoginHandler:
    """
    Unified Thea login handler facade (V2 compliant).

    Delegates to:
    - TheaCookieManager (cookie persistence)
    - TheaLoginDetector (login status detection)
    - TheaAuthenticationHandler (authentication operations)
    """

    def __init__(
        self,
        username: str = None,
        password: str = None,
        totp_secret: str = None,
        cookie_file: str = "thea_cookies.json",
        timeout: int = 30,
    ):
        """Initialize Thea login handler."""
        self.auth_handler = TheaAuthenticationHandler(username, password, totp_secret, cookie_file)
        self.cookie_manager = self.auth_handler.cookie_manager
        self.login_detector = self.auth_handler.login_detector
        self.timeout = timeout

    # Delegate to authentication handler
    def ensure_login(self, driver, allow_manual: bool = True, manual_timeout: int = 60) -> bool:
        """Ensure user is logged in."""
        return self.auth_handler.ensure_login(driver, allow_manual, manual_timeout)

    def force_logout(self, driver) -> bool:
        """Force logout."""
        return self.auth_handler.force_logout(driver)

    # Direct access to components
    def _is_logged_in(self, driver) -> bool:
        """Check if logged in (backward compatibility)."""
        return self.login_detector.is_logged_in(driver)


__all__ = [
    "TheaLoginHandler",
    "TheaCookieManager",
    "TheaLoginDetector",
    "TheaAuthenticationHandler",
]

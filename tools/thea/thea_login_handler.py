#!/usr/bin/env python3
"""
Thea Login Handler - DEPRECATED (V2 VIOLATION FIXED)
====================================================

⚠️ DEPRECATED: This file exceeded V2 limits (671 lines).
Refactored into V2-compliant modules:
  - thea_cookie_manager.py (115 lines)
  - thea_login_detector.py (171 lines)
  - thea_authentication_handler.py (167 lines)
  - thea_login_handler_refactored.py (46 lines facade)

Use thea_login_handler_refactored.py instead.

DEPRECATED BY: Agent-1 (V2 Critical Fix)
DATE: 2025-10-10

Original: Modular Authentication System
Extracted and adapted from DreamVault's authentication system.
Handles automated login detection and cookie management for Thea communication.

Features:
- Automated login status detection
- Cookie-based session persistence
- Manual login fallback
- Selenium WebDriver integration
- ChatGPT/Thea specific selectors

Usage:
    from thea_login_handler import TheaLoginHandler

    handler = TheaLoginHandler(username="user@example.com", password="password")
    if handler.ensure_login(driver):
        print("Logged in successfully!")
"""

import json
import logging
import time
from pathlib import Path

# Selenium imports
try:
    from selenium import webdriver
    from selenium.common.exceptions import NoSuchElementException, TimeoutException
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not available - login handler will use fallback methods")

logger = logging.getLogger(__name__)


class TheaCookieManager:
    """Manages cookie persistence for Thea sessions."""

    def __init__(self, cookie_file: str = "thea_cookies.json"):
        """
        Initialize the cookie manager.

        Args:
            cookie_file: Path to cookie file for persistence
        """
        self.cookie_file = Path(cookie_file)
        self.cookie_file.parent.mkdir(parents=True, exist_ok=True)

    def save_cookies(self, driver) -> bool:
        """
        Save cookies from the current driver session.

        Args:
            driver: Selenium webdriver instance

        Returns:
            True if cookies saved successfully, False otherwise
        """
        try:
            if not SELENIUM_AVAILABLE:
                logger.warning("Selenium not available - cannot save cookies")
                return False

            cookies = driver.get_cookies()
            print(f"🔍 Found {len(cookies)} total cookies from browser")

            # Filter and save cookies - be more permissive for ChatGPT
            persistent_cookies = []
            for cookie in cookies:
                cookie_name = cookie.get("name", "")
                domain = cookie.get("domain", "")
                expiry = cookie.get("expiry")
                print(f"🔍 Cookie: {cookie_name} | Domain: {domain} | Expiry: {expiry}")
                # Skip obviously unimportant cookies
                cookie_name = cookie.get("name", "").lower()

                # Skip analytics and tracking cookies (optional)
                skip_names = ["_ga", "_gid", "_gat", "__gads", "_fbp", "_fbc"]
                if any(skip_name in cookie_name for skip_name in skip_names):
                    continue

                # For ChatGPT, save all cookies that are likely authentication-related
                # This includes session cookies which are often needed for login
                domain = cookie.get("domain", "").lower()
                if any(
                    chatgpt_domain in domain
                    for chatgpt_domain in ["openai.com", "chatgpt.com", "chat.openai.com"]
                ):
                    persistent_cookies.append(cookie)
                elif not domain or domain == "":  # Local cookies
                    persistent_cookies.append(cookie)
                elif cookie_name.startswith("__") and (
                    "openai" in cookie_name or "chatgpt" in cookie_name
                ):
                    # Special case for cookies with OpenAI/ChatGPT in name
                    persistent_cookies.append(cookie)

            with open(self.cookie_file, "w", encoding="utf-8") as f:
                json.dump(persistent_cookies, f, indent=2)

            logger.info(f"✅ Saved {len(persistent_cookies)} Thea cookies to {self.cookie_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")
            return False

    def load_cookies(self, driver) -> bool:
        """
        Load cookies into the current driver session.

        Args:
            driver: Selenium webdriver instance

        Returns:
            True if cookies loaded successfully, False otherwise
        """
        try:
            if not SELENIUM_AVAILABLE:
                logger.warning("Selenium not available - cannot load cookies")
                return False

            if not self.cookie_file.exists():
                logger.info(f"Cookie file not found: {self.cookie_file}")
                return False

            with open(self.cookie_file, encoding="utf-8") as f:
                cookies = json.load(f)

            # Add cookies to driver
            loaded_count = 0
            for cookie in cookies:
                try:
                    # Ensure cookie has required fields
                    if "name" in cookie and "value" in cookie:
                        driver.add_cookie(cookie)
                        loaded_count += 1
                except Exception as e:
                    logger.warning(f"Failed to add cookie {cookie.get('name', 'unknown')}: {e}")

            logger.info(f"✅ Loaded {loaded_count} cookies from {self.cookie_file}")
            return loaded_count > 0

        except Exception as e:
            logger.error(f"Failed to load cookies: {e}")
            return False

    def has_valid_cookies(self) -> bool:
        """
        Check if valid cookies exist.

        Returns:
            True if cookie file exists and contains cookies
        """
        if not self.cookie_file.exists():
            return False

        try:
            with open(self.cookie_file, encoding="utf-8") as f:
                cookies = json.load(f)

            if len(cookies) == 0:
                return False

            # Check if cookies are recent (within last 24 hours)
            # This helps avoid using very old/stale cookies
            import time

            current_time = time.time()
            recent_cookies = []

            for cookie in cookies:
                expiry = cookie.get("expiry")
                if expiry and expiry > current_time:
                    recent_cookies.append(cookie)
                elif not expiry:  # Session cookies are considered valid
                    recent_cookies.append(cookie)

            return len(recent_cookies) > 0

        except Exception as e:
            print(f"⚠️  Error checking cookies: {e}")
            return False

    def clear_cookies(self) -> bool:
        """
        Clear saved cookies.

        Returns:
            True if cookies cleared successfully, False otherwise
        """
        try:
            if self.cookie_file.exists():
                self.cookie_file.unlink()
                logger.info("✅ Cookies cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cookies: {e}")
            return False


class TheaLoginHandler:
    """
    Handles Thea/ChatGPT login with automated detection and cookie persistence.

    Adapted from DreamVault's authentication system for Thea communication.
    """

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        cookie_file: str = "thea_cookies.json",
        timeout: int = 30,
    ):
        """
        Initialize the Thea login handler.

        Args:
            username: ChatGPT username/email
            password: ChatGPT password
            cookie_file: Path to cookie file for persistence
            timeout: Timeout for login operations
        """
        self.username = username
        self.password = password
        self.timeout = timeout
        self.cookie_manager = TheaCookieManager(cookie_file)

        # Thea/ChatGPT specific URLs
        self.thea_url = "https://chatgpt.com/g/g-67f437d96d7c81918b2dbc12f0423867-thea-manager"
        self.chatgpt_base_url = "https://chat.openai.com"

    def ensure_login(self, driver, allow_manual: bool = True, manual_timeout: int = 60) -> bool:
        """
        Ensure user is logged into Thea/ChatGPT.

        Args:
            driver: Selenium webdriver instance
            allow_manual: Allow manual login if automated fails
            manual_timeout: Timeout for manual login

        Returns:
            True if login successful, False otherwise
        """
        try:
            logger.info("🔐 Ensuring Thea login...")

            # Navigate to Thea page
            driver.get(self.thea_url)
            time.sleep(3)

            # Check if already logged in and on Thea page
            if self._is_logged_in(driver) and self._is_on_thea_page(driver):
                logger.info("✅ Already logged in to Thea")
                return True

            # Try cookie-based authentication
            if self.cookie_manager.has_valid_cookies():
                logger.info("🍪 Trying cookie-based login...")
                self.cookie_manager.load_cookies(driver)
                driver.refresh()
                time.sleep(3)

                if self._is_logged_in(driver):
                    # First navigate to main ChatGPT page to ensure proper authentication
                    logger.info("🔄 Navigating to main ChatGPT page to ensure authentication...")
                    driver.get("https://chatgpt.com/")
                    time.sleep(3)

                    # Check if still logged in after navigation
                    if self._is_logged_in(driver):
                        logger.info("✅ Authentication confirmed on main page")
                    else:
                        logger.warning("⚠️ Lost authentication when navigating to main page")
                        return False

                    # Check if we're on Thea page, if not navigate there
                    if self._is_on_thea_page(driver):
                        logger.info("✅ Already on Thea page")
                        return True
                    else:
                        logger.info("🔄 Logged in but not on Thea page, navigating to Thea...")
                        if self._navigate_to_thea(driver):
                            return True

            # Try automated login if credentials provided
            if self.username and self.password:
                if self._automated_login(driver):
                    # Save cookies after successful login
                    self.cookie_manager.save_cookies(driver)
                    return True

            # Try manual login if allowed
            if allow_manual:
                logger.info("🔄 Attempting manual login...")
                return self._manual_login(driver, manual_timeout)

            logger.error("❌ Login failed - no credentials and manual login not allowed")
            return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    def _is_logged_in(self, driver) -> bool:
        """
        Check if user is logged in to Thea/ChatGPT.

        Uses multiple indicators to detect login status:
        - Send button presence
        - Conversation elements
        - Input field availability
        """
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium not available - cannot check login status")
            return False

        try:
            # First, let's debug what we can see on the page
            page_title = driver.title
            current_url = driver.current_url
            logger.debug(f"Page title: {page_title}")
            logger.debug(f"Current URL: {current_url}")

            # Look for logged-in indicators (Thea/ChatGPT specific)
            # More specific and accurate selectors
            logged_in_indicators = [
                # Most specific indicators first
                "//button[contains(@data-testid, 'send-button')]",
                "//button[contains(@aria-label, 'Send')]",
                "//textarea[contains(@data-testid, 'prompt-textarea')]",
                "//textarea[contains(@placeholder, 'Message')]",
                "//div[contains(@data-testid, 'conversation-turn')]",
                # Input area with specific attributes
                "textarea[data-testid*='prompt']",
                "textarea[placeholder*='Message']",
                # Specific ChatGPT elements that indicate logged-in state
                "//div[contains(@class, 'conversation-turn')]",
                "//div[contains(@class, 'message user-message')]",
                "//div[contains(@class, 'message assistant-message')]",
                # Navigation and UI elements that appear when logged in
                "//button[contains(@class, 'new-chat-button')]",
                "//div[contains(@class, 'sidebar')]",
            ]

            found_indicators = []
            login_page_found = False

            for indicator in logged_in_indicators:
                try:
                    if indicator.startswith("//"):
                        elements = driver.find_elements(By.XPATH, indicator)
                    else:
                        elements = driver.find_elements(By.CSS_SELECTOR, indicator)

                    visible_elements = [
                        elem for elem in elements if getattr(elem, "is_displayed", lambda: False)()
                    ]
                    if visible_elements:
                        found_indicators.append(f"{indicator} ({len(visible_elements)} found)")
                        logger.debug(
                            f"✅ Found login indicator: {indicator} ({len(visible_elements)} visible)"
                        )
                except Exception as e:
                    logger.debug(f"Error checking {indicator}: {e}")
                    continue

            logger.debug(f"Found {len(found_indicators)} potential login indicators")

            # Check for login page indicators (strong evidence of not logged in)
            login_indicators = [
                "//button[contains(text(), 'Log in')]",
                "//button[contains(text(), 'Sign up')]",
                "//a[contains(text(), 'Log in')]",
                "//a[contains(text(), 'Sign up')]",
                "//input[@name='username']",
                "//input[@name='password']",
                "//input[@type='email']",
                "//div[contains(text(), 'Welcome to ChatGPT')]",
                "//div[contains(text(), 'Log in to ChatGPT')]",
                "//h1[contains(text(), 'Welcome')]",
                "//div[contains(@class, 'login')]",
                "//form",  # Login forms
            ]

            for indicator in login_indicators:
                try:
                    element = driver.find_element(By.XPATH, indicator)
                    if getattr(element, "is_displayed", lambda: False)():
                        logger.debug(f"🔒 Found login page indicator: {indicator}")
                        login_page_found = True
                        break
                except NoSuchElementException:
                    continue

            # Decision logic:
            # If we found login page elements AND no logged-in indicators, definitely not logged in
            if login_page_found and len(found_indicators) == 0:
                logger.info(
                    "🔒 Login page detected with no logged-in indicators - user is NOT logged in"
                )
                return False

            # If we found login page elements but also have logged-in indicators, probably logged in
            # (e.g., "Sign up for free" might appear even when logged in)
            if login_page_found and len(found_indicators) > 0:
                logger.info(
                    "⚠️ Mixed signals: Login page elements found but also logged-in indicators"
                )
                # Prioritize logged-in indicators
                if len(found_indicators) >= 2:
                    logger.info("✅ Prioritizing logged-in indicators - user appears logged in")
                    return True

            # Check for strong indicators of being logged in
            # Look for profile/account selector button - very specific indicator
            try:
                # Look for the profile selector button that appears when logged in
                profile_selectors = [
                    "//button[contains(@class, '__menu-item')]",
                    "//button[contains(text(), 'Personal account')]",
                    "//button[contains(text(), 'account')]",
                    "//img[@alt='Profile image']",  # Profile image in account selector
                    "//div[contains(@class, 'bg-gray-500/30')]",  # Profile image container
                ]

                for selector in profile_selectors:
                    try:
                        if selector.startswith("//"):
                            elements = driver.find_elements(By.XPATH, selector)
                        else:
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)

                        visible_elements = [elem for elem in elements if elem.is_displayed()]
                        if visible_elements:
                            logger.info(
                                f"✅ Found profile selector element: {selector} - user is logged in"
                            )
                            return True
                    except Exception:
                        continue
            except Exception:
                pass

            # Look for textarea (message input) - strongest indicator
            try:
                textareas = driver.find_elements(By.TAG_NAME, "textarea")
                visible_textareas = [ta for ta in textareas if ta.is_displayed()]
                if visible_textareas:
                    logger.info(
                        f"✅ Found {len(visible_textareas)} visible textarea(s) - user is logged in"
                    )
                    return True
            except Exception:
                pass

            # Look for send button or similar
            try:
                buttons = driver.find_elements(By.TAG_NAME, "button")
                send_buttons = []
                for btn in buttons:
                    try:
                        if btn.is_displayed():
                            btn_text = str(btn.text or "").lower()
                            if any(keyword in btn_text for keyword in ["send", "submit"]):
                                send_buttons.append(btn)
                    except Exception:
                        continue  # Skip buttons that cause errors
                if send_buttons:
                    logger.info(f"✅ Found {len(send_buttons)} send button(s) - user is logged in")
                    return True
            except Exception as e:
                logger.debug(f"Error checking send buttons: {e}")

            # If we found multiple logged-in indicators, probably logged in
            if len(found_indicators) >= 2:
                logger.info(
                    f"✅ Found {len(found_indicators)} login indicators - user appears logged in"
                )
                return True

            # If we have buttons + inputs + textarea, likely logged in
            try:
                buttons = len(
                    [
                        btn
                        for btn in driver.find_elements(By.TAG_NAME, "button")
                        if btn.is_displayed()
                    ]
                )
                inputs = len(
                    [
                        inp
                        for inp in driver.find_elements(By.TAG_NAME, "input")
                        if inp.is_displayed()
                    ]
                )
                textareas = len(
                    [
                        ta
                        for ta in driver.find_elements(By.TAG_NAME, "textarea")
                        if ta.is_displayed()
                    ]
                )

                # Heuristic: if we have many buttons and some inputs/textareas, likely logged in
                if buttons > 10 and (inputs > 0 or textareas > 0):
                    logger.info(
                        f"✅ Found {buttons} buttons, {inputs} inputs, {textareas} textareas - user appears logged in"
                    )
                    return True
            except Exception:
                pass

            # Additional check: look for any input field that could be a message input
            try:
                # Look for any textarea or contenteditable div
                input_selectors = [
                    "textarea",
                    "div[contenteditable='true']",
                    "div[data-testid*='input']",
                    "input[type='text']",
                ]

                for selector in input_selectors:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            # Check if it's likely a message input (not search, etc.)
                            placeholder = element.get_attribute("placeholder") or ""
                            if any(
                                keyword in placeholder.lower()
                                for keyword in ["message", "ask", "send", "type"]
                            ):
                                logger.debug(
                                    f"✅ Found message input: {selector} with placeholder '{placeholder}'"
                                )
                                return True
                            # If no placeholder, check size/position (message inputs are usually large)
                            rect = element.rect
                            if rect["height"] > 50:  # Likely a message input
                                logger.debug(
                                    f"✅ Found large input field: {selector} (size: {rect['width']}x{rect['height']})"
                                )
                                return True
            except Exception as e:
                logger.debug(f"Error checking input fields: {e}")

            # If we found some indicators but not definitive ones, log what we found
            if found_indicators:
                logger.info(f"Found potential indicators but not definitive: {found_indicators}")

            # Treat visible sign-up/log-in prompts as not logged in
            try:
                signup_cta = driver.find_elements(
                    By.XPATH,
                    "//div[contains(text(), 'Sign up to chat') or contains(text(), 'Sign up')]",
                )
                buttons = driver.find_elements(
                    By.XPATH,
                    "//button//div[contains(text(), 'Sign up') or contains(text(), 'Log in')]",
                )
                any_visible_cta = any(
                    getattr(e, "is_displayed", lambda: False)() for e in signup_cta + buttons
                )
                if any_visible_cta:
                    logger.info("🔒 Login/signup CTA visible - NOT logged in")
                    return False
            except Exception:
                pass

            # Final fallback: if we're on the Thea URL and couldn't confirm login, assume not logged in
            if "thea-manager" in current_url:
                logger.warning(
                    "On Thea page but couldn't confirm login status - assuming not logged in"
                )
                return False

            logger.warning("⚠️ Could not definitively determine login status")
            logger.info(f"Debug info - Title: {page_title}, URL: {current_url}")
            return False

        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False

    def _automated_login(self, driver) -> bool:
        """
        Perform automated login with credentials.

        Args:
            driver: Selenium webdriver instance

        Returns:
            True if automated login successful, False otherwise
        """
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium not available - cannot perform automated login")
            return False

        try:
            logger.info("🔄 Attempting automated login...")

            # Wait for login form
            wait = WebDriverWait(driver, self.timeout)

            # Find and fill username
            try:
                username_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))
                username_field.clear()
                username_field.send_keys(self.username)

                # Click continue
                continue_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                continue_button.click()
                time.sleep(2)

            except TimeoutException:
                logger.warning("Username field not found - may already be on password page")

            # Find and fill password
            try:
                password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
                password_field.clear()
                password_field.send_keys(self.password)

                # Click login
                login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                login_button.click()
                time.sleep(3)

            except TimeoutException:
                logger.warning("Password field not found - login flow may have changed")

            # Check if login successful
            if self._is_logged_in(driver):
                logger.info("✅ Automated login successful")
                return True
            else:
                logger.warning("⚠️ Automated login failed - may need manual intervention")
                return False

        except Exception as e:
            logger.error(f"Automated login error: {e}")
            return False

    def _manual_login(self, driver, timeout: int) -> bool:
        """
        Allow manual login with timeout.

        Args:
            driver: Selenium webdriver instance
            timeout: Timeout in seconds

        Returns:
            True if manual login successful, False otherwise
        """
        try:
            logger.info(f"⏰ Manual login timeout: {timeout} seconds")
            logger.info("👤 Please log in manually in the browser...")
            logger.info("🔍 System will automatically detect when login is complete")

            start_time = time.time()
            check_interval = 2  # Check every 2 seconds

            while time.time() - start_time < timeout:
                if self._is_logged_in(driver):
                    logger.info("✅ Manual login successful")
                    # Save cookies after manual login
                    self.cookie_manager.save_cookies(driver)
                    return True

                time.sleep(check_interval)
                remaining = int(timeout - (time.time() - start_time))
                if remaining % 10 == 0:  # Log every 10 seconds
                    logger.info(f"⏰ Waiting for login... {remaining} seconds remaining")

            logger.error("❌ Manual login timeout")
            return False

        except Exception as e:
            logger.error(f"Manual login error: {e}")
            return False

    def _is_on_thea_page(self, driver) -> bool:
        """Check if we're currently on the Thea page."""
        try:
            current_url = driver.current_url
            page_title = driver.title

            # Check URL contains Thea identifier
            if "g-67f437d96d7c81918b2dbc12f0423867" in current_url:
                return True

            # Check title contains Thea
            if "thea" in page_title.lower():
                return True

            return False
        except Exception:
            return False

    def _navigate_to_thea(self, driver) -> bool:
        """Navigate to the Thea page if logged in but on wrong page."""
        try:
            logger.info("🌐 Navigating to Thea page...")

            # If we're not on Thea, navigate there
            if not self._is_on_thea_page(driver):
                driver.get(self.thea_url)
                time.sleep(3)

            # Check if navigation was successful
            if self._is_on_thea_page(driver):
                logger.info("✅ Successfully navigated to Thea")
                return True
            else:
                logger.info("⚠️ Navigation to Thea may have failed")
                return False

        except Exception as e:
            logger.error(f"Navigation error: {e}")
            return False

    def force_logout(self, driver) -> bool:
        """
        Force logout from ChatGPT.

        Args:
            driver: Selenium webdriver instance

        Returns:
            True if logout successful, False otherwise
        """
        try:
            logger.info("🚪 Forcing logout...")

            # Clear cookies
            self.cookie_manager.clear_cookies()

            # Navigate to logout if possible
            driver.get("https://chat.openai.com/auth/logout")
            time.sleep(2)

            logger.info("✅ Logout completed")
            return True

        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False


# Convenience functions for easy integration
def create_thea_login_handler(username=None, password=None, cookie_file="thea_cookies.json"):
    """
    Create a Thea login handler with default settings.

    Args:
        username: ChatGPT username/email
        password: ChatGPT password
        cookie_file: Path to cookie file

    Returns:
        TheaLoginHandler instance
    """
    return TheaLoginHandler(username=username, password=password, cookie_file=cookie_file)


def check_thea_login_status(driver) -> bool:
    """
    Quick check of Thea login status.

    Args:
        driver: Selenium webdriver instance

    Returns:
        True if logged in, False otherwise
    """
    handler = TheaLoginHandler()
    return handler._is_logged_in(driver)


if __name__ == "__main__":
    # Example usage
    print("🐝 V2_SWARM Thea Login Handler")
    print("=" * 40)

    # Create handler (add credentials as needed)
    handler = create_thea_login_handler()

    print("✅ Thea Login Handler created")
    print("📝 To use with credentials:")
    print(
        "   handler = create_thea_login_handler(username='your@email.com', password='your_password')"
    )
    print("   success = handler.ensure_login(driver)")

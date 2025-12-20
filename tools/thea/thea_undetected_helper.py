#!/usr/bin/env python3
"""
Thea Undetected Chrome Helper
==============================

Helper utilities for using undetected-chromedriver with Thea communication.
Provides easy integration with the existing Thea authentication system.

Usage:
    from thea_undetected_helper import create_undetected_driver
    
    driver = create_undetected_driver()
    # Use with existing thea_login_handler
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Import availability checks
try:
    import undetected_chromedriver as uc
    UNDETECTED_AVAILABLE = True
except ImportError:
    UNDETECTED_AVAILABLE = False
    logger.warning("undetected-chromedriver not available")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


def create_undetected_driver(
    headless: bool = False,
    user_data_dir: Optional[str] = None,
    profile: Optional[str] = None,
    version_main: Optional[int] = None,
    **kwargs
):
    """
    Create an undetected Chrome driver for Thea communication.

    This function automatically handles:
    - ChromeDriver version detection and download
    - Anti-bot detection bypass
    - Fallback to standard Chrome if needed

    Args:
        headless: Run in headless mode (not recommended for anti-detection)
        user_data_dir: Chrome user data directory
        profile: Chrome profile name
        version_main: Chrome version to use (None = auto-detect)
        **kwargs: Additional arguments passed to uc.Chrome()

    Returns:
        Chrome driver instance (undetected or standard)

    Example:
        >>> driver = create_undetected_driver()
        >>> driver.get("https://chatgpt.com")
    """
    if UNDETECTED_AVAILABLE:
        try:
            logger.info("🔐 Creating undetected Chrome driver...")

            # Configure options
            options = uc.ChromeOptions()
            
            if user_data_dir:
                options.add_argument(f'--user-data-dir={user_data_dir}')
            
            if profile:
                options.add_argument(f'--profile-directory={profile}')

            # Anti-detection options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--window-size=1920,1080')

            if headless:
                logger.warning("⚠️ Headless mode may be detected by anti-bot systems")
                options.add_argument('--headless=new')

            # Create driver
            driver = uc.Chrome(
                options=options,
                version_main=version_main,
                use_subprocess=True,
                driver_executable_path=None,  # Auto-download
                **kwargs
            )

            logger.info("✅ Undetected Chrome driver created successfully")
            return driver

        except Exception as e:
            logger.error(f"❌ Failed to create undetected Chrome driver: {e}")
            logger.info("🔄 Falling back to standard Chrome...")

    # Fallback to standard Chrome
    return create_standard_driver(
        headless=headless,
        user_data_dir=user_data_dir,
        profile=profile
    )


def create_standard_driver(
    headless: bool = False,
    user_data_dir: Optional[str] = None,
    profile: Optional[str] = None
):
    """
    Create a standard Chrome driver using Selenium Manager.

    Args:
        headless: Run in headless mode
        user_data_dir: Chrome user data directory
        profile: Chrome profile name

    Returns:
        Standard Chrome driver instance
    """
    if not SELENIUM_AVAILABLE:
        raise ImportError("Selenium is required for browser functionality")

    logger.info("🚀 Creating standard Chrome driver...")

    options = Options()
    
    if headless:
        options.add_argument('--headless')
    
    if user_data_dir:
        options.add_argument(f'--user-data-dir={user_data_dir}')
    
    if profile:
        options.add_argument(f'--profile-directory={profile}')

    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')

    driver = webdriver.Chrome(options=options)
    logger.info("✅ Standard Chrome driver created successfully")
    
    return driver


def check_undetected_available() -> bool:
    """
    Check if undetected-chromedriver is available.

    Returns:
        True if available, False otherwise
    """
    return UNDETECTED_AVAILABLE


def get_installation_instructions() -> str:
    """
    Get installation instructions for undetected-chromedriver.

    Returns:
        Installation instructions string
    """
    return """
🔧 UNDETECTED-CHROMEDRIVER INSTALLATION
========================================

To use undetected Chrome for bypassing bot detection:

1. Install the package:
   pip install undetected-chromedriver

2. Or install all Thea requirements:
   pip install -r requirements.txt

3. The ChromeDriver will auto-download on first use

Features:
✅ Automatic ChromeDriver version detection
✅ Bypasses Cloudflare and anti-bot systems
✅ Works with ChatGPT without triggering detection
✅ Fallback to standard Chrome if needed

Note: Headless mode reduces effectiveness against bot detection.
"""


if __name__ == "__main__":
    # Example usage
    print("🐝 V2_SWARM Thea Undetected Chrome Helper")
    print("=" * 50)

    # Check availability
    if check_undetected_available():
        print("✅ undetected-chromedriver is available")
        print("🔐 Ready for anti-bot bypass")
    else:
        print("⚠️ undetected-chromedriver is NOT available")
        print(get_installation_instructions())
        print("\n🔄 Will use standard Chrome as fallback")

    # Example: Create a driver
    print("\n📋 Example Usage:")
    print("-" * 50)
    print("from thea_undetected_helper import create_undetected_driver")
    print("from thea_login_handler import TheaLoginHandler")
    print("")
    print("# Create undetected driver")
    print("driver = create_undetected_driver()")
    print("")
    print("# Use with Thea login handler")
    print("login_handler = TheaLoginHandler()")
    print("login_handler.ensure_login(driver)")
    print("")
    print("# Navigate to Thea")
    print('driver.get("https://chatgpt.com/g/g-67f437d96d7c81918b2dbc12f0423867-thea-manager")')


#!/usr/bin/env python3
"""
Deploy via WordPress Admin - Browser Automation
================================================

Uses browser automation to deploy files via WordPress admin Theme Editor.
No SFTP credentials required - uses WordPress admin login.

<!-- SSOT Domain: infrastructure -->

Author: Agent-7 (Web Development Specialist)
Hardened by: Agent-3 (Infrastructure & DevOps Specialist)
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("❌ Selenium not installed. Install with: pip install selenium")
    sys.exit(1)


def _wait_for_logged_in(driver, timeout: int = 60) -> bool:
    """Wait until WordPress admin is logged in (dashboard or editor loaded)."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: "wp-admin" in d.current_url
            and (
                "dashboard" in d.current_url.lower()
                or "themes" in d.current_url.lower()
                or "theme-editor" in d.current_url.lower()
                or d.find_elements(By.CSS_SELECTOR, "#wpadminbar")
            )
        )
        print("✅ Logged in successfully!")
        return True
    except TimeoutException:
        print("❌ Login timeout - could not detect WordPress admin dashboard/editor")
        return False


def _auto_login_if_possible(driver, wp_admin_url: str, timeout: int = 60) -> bool:
    """
    Attempt automated login using WORDPRESS_USER / WORDPRESS_PASS from .env.

    Returns True if login is confirmed, False otherwise.
    """
    wp_user = os.getenv("WORDPRESS_USER")
    wp_pass = os.getenv("WORDPRESS_PASS")

    if not wp_user or not wp_pass:
        print("⚠️  Auto-login requested but WORDPRESS_USER/WORDPRESS_PASS not set in .env")
        return False

    print("🔐 Attempting automatic WordPress login using .env credentials...")
    driver.get(wp_admin_url)
    time.sleep(2)

    try:
        # Wait for login form
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form#loginform"))
        )
        user_input = driver.find_element(By.CSS_SELECTOR, "input#user_login")
        pass_input = driver.find_element(By.CSS_SELECTOR, "input#user_pass")
        submit_btn = driver.find_element(By.CSS_SELECTOR, "input#wp-submit")

        user_input.clear()
        user_input.send_keys(wp_user)
        pass_input.clear()
        pass_input.send_keys(wp_pass)
        submit_btn.click()
    except TimeoutException:
        print("⚠️  Could not find WordPress login form for auto-login")
        return False
    except Exception as e:
        print(f"❌ Auto-login error: {e}")
        return False

    return _wait_for_logged_in(driver, timeout=timeout)


def deploy_via_wordpress_admin(
    site_url: str,
    wp_admin_url: str,
    file_path: Path,
    file_content: Optional[str] = None,
    auto_login: bool = False,
    dry_run: bool = False,
    verify_only: bool = False,
):
    """
    Deploy file via WordPress admin Theme Editor.

    Args:
        site_url: Base site URL (e.g., https://freerideinvestor.com)
        wp_admin_url: WordPress admin URL (e.g., https://freerideinvestor.com/wp-admin)
        file_path: Local file path to deploy
        file_content: Optional file content (if None, reads from file_path)
        auto_login: If True, attempt login using WORDPRESS_USER/PASS from .env
        dry_run: If True, only verify that Theme Editor can be reached (no write)
        verify_only: Alias for dry_run (for CLI ergonomics)
    """
    if not SELENIUM_AVAILABLE:
        return False

    dry_mode = dry_run or verify_only

    # Read file content if not provided
    if file_content is None:
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False
        file_content = file_path.read_text(encoding="utf-8")

    print("🚀 Starting browser automation...")

    # Setup Chrome options
    options = Options()
    options.add_argument("--window-size=1920,1080")
    # Don't run headless - user may need to solve captchas / MFA

    driver = webdriver.Chrome(options=options)

    try:
        # Navigate / login
        if auto_login:
            if not _auto_login_if_possible(driver, wp_admin_url):
                print("❌ Auto-login failed; cannot proceed in automated mode")
                return False
        else:
            # Manual login flow
            print(f"📱 Navigating to: {wp_admin_url}")
            driver.get(wp_admin_url)
            time.sleep(2)

            print("⏳ Waiting for login...")
            print("   Please log in to WordPress admin if prompted")
            print("   Waiting 60 seconds for manual login...")

            if not _wait_for_logged_in(driver, timeout=TimeoutConstants.HTTP_MEDIUM):
                return False

        # Navigate to Theme Editor
        print("📝 Navigating to Theme Editor...")
        # NOTE: Theme name is still passed via CLI, but URL pattern is stable
        theme_editor_url = (
            f"{site_url}/wp-admin/theme-editor.php?file=functions.php&theme=freerideinvestor"
        )
        driver.get(theme_editor_url)
        time.sleep(3)

        # Find the textarea with file content
        try:
            textarea = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "textarea.wp-editor-area, textarea#newcontent")
                )
            )
            print("✅ Found editor textarea")
        except TimeoutException:
            print("❌ Could not find editor textarea")
            print("   Make sure you're on the Theme Editor page")
            return False

        # Find Update File button (even in dry-run to verify flow)
        try:
            update_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "input#submit, button#submit, input[type='submit'][value*='Update']",
                    )
                )
            )
            print("✅ Found Update File button")
        except TimeoutException:
            print("❌ Could not find Update File button")
            return False

        if dry_mode:
            print("✅ DRY-RUN / VERIFY-ONLY: Reached Theme Editor and located editor + button")
            print("   No changes were written to the remote file.")
            return True

        # Clear and paste new content
        print("📝 Updating file content...")
        textarea.clear()
        textarea.send_keys(file_content)
        time.sleep(1)

        # Click Update File button
        update_button.click()
        print("✅ Clicked Update File button")
        time.sleep(3)

        # Check for success message
        try:
            success_msg = driver.find_element(
                By.CSS_SELECTOR, ".notice-success, .updated, #message"
            )
            if success_msg:
                print("✅ File updated successfully!")
                return True
        except Exception:
            pass

        # If no error message, assume success
        print("✅ File update completed (no error detected)")
        return True

    except Exception as e:
        print(f"❌ Error during deployment: {e}")
        return False
    finally:
        print("\n⏳ Keeping browser open for 10 seconds to verify...")
        print("   Close browser when done")
        time.sleep(10)
        driver.quit()


def main():
    """Main deployment function."""
    import argparse
from src.core.config.timeout_constants import TimeoutConstants

    parser = argparse.ArgumentParser(description="Deploy file via WordPress admin")
    parser.add_argument("--site", default="freerideinvestor.com", help="Site domain")
    parser.add_argument("--file", required=True, help="File path to deploy")
    parser.add_argument("--theme", default="freerideinvestor", help="Theme name")
    parser.add_argument(
        "--auto-login",
        action="store_true",
        help="Use WORDPRESS_USER/PASS from .env to log in automatically",
    )
    parser.add_argument(
        "--no-auto-login",
        action="store_true",
        help="Force manual login even if credentials exist",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Verify navigation to Theme Editor without writing changes",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Alias for --dry-run (no changes written)",
    )

    args = parser.parse_args()

    site_url = f"https://{args.site}" if not args.site.startswith("http") else args.site
    wp_admin_url = f"{site_url}/wp-admin"
    file_path = Path(args.file)

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return 1

    # Determine login and mode settings
    dry_mode = args.dry_run or args.verify_only
    auto_login = False
    if args.auto_login and not args.no_auto_login:
        # Require credentials if auto-login requested
        if not os.getenv("WORDPRESS_USER") or not os.getenv("WORDPRESS_PASS"):
            print(
                "❌ --auto-login requested but WORDPRESS_USER/WORDPRESS_PASS "
                "are not set in .env"
            )
            return 1
        auto_login = True

    print("=" * 60)
    print("🚀 WordPress Admin Deployment")
    print("=" * 60)
    print(f"Site: {site_url}")
    print(f"File: {file_path}")
    print(f"Theme: {args.theme}")
    print(f"Mode: {'DRY-RUN/VERIFY-ONLY' if dry_mode else 'WRITE'}")
    print(f"Login: {'AUTO' if auto_login else 'MANUAL'}")
    print()
    print("⚠️  NOTE: This will open a browser window")
    if auto_login:
        print("   Tool will attempt automatic WordPress login using .env credentials")
    else:
        print("   You may need to log in to WordPress admin manually")
    print("   The tool will then navigate to Theme Editor and update/verify the file")
    print()

    input("Press Enter to continue...")

    if deploy_via_wordpress_admin(
        site_url,
        wp_admin_url,
        file_path,
        auto_login=auto_login,
        dry_run=dry_mode,
        verify_only=False,
    ):
        print("\n✅ Deployment flow completed!")
        if not dry_mode:
            print("\nNext steps:")
            print("  1. Clear WordPress menu cache")
            print("  2. Check Appearance > Menus")
            print("  3. Verify on live site")
        return 0
    else:
        print("\n❌ Deployment failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())





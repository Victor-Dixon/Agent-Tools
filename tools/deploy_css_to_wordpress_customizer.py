#!/usr/bin/env python3
"""
Deploy CSS to WordPress Customizer Additional CSS
=================================================

Uses browser automation to add CSS to WordPress Customizer > Additional CSS.
This is the proper way to add site-wide CSS that applies to all blog posts.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-13
V2 Compliant: Yes
"""

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
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def load_blogging_config():
    """Load blogging API configuration."""
    import json
    config_path = project_root / ".deploy_credentials" / "blogging_api.json"
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_css_fix() -> str:
    """Load the CSS readability fix."""
    css_path = project_root / "docs" / "DADUDEKC_BLOG_READABILITY_FIX.css"
    
    if not css_path.exists():
        print(f"⚠️  CSS fix file not found: {css_path}")
        return ""
    
    return css_path.read_text(encoding='utf-8')


def deploy_css_to_customizer(site_url: str, css_content: str, wait_for_login: int = 120) -> bool:
    """
    Deploy CSS to WordPress Customizer Additional CSS using browser automation.
    
    Args:
        site_url: WordPress site URL
        css_content: CSS content to add
        wait_for_login: Seconds to wait for manual login
    
    Returns:
        bool: True if successful
    """
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium not installed. Install with: pip install selenium")
        return False
    
    site_url = site_url.rstrip('/')
    wp_admin_url = f"{site_url}/wp-admin"
    customizer_url = f"{site_url}/wp-admin/customize.php"
    
    print("=" * 60)
    print("🚀 DEPLOY CSS TO WORDPRESS CUSTOMIZER")
    print("=" * 60)
    print(f"Site: {site_url}")
    print(f"CSS Size: {len(css_content):,} characters")
    print()
    
    # Setup Chrome
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"❌ Failed to start browser: {e}")
        print("   Install ChromeDriver or use manual deployment")
        return False
    
    try:
        # Navigate to WordPress admin
        print(f"📱 Navigating to: {wp_admin_url}")
        driver.get(wp_admin_url)
        time.sleep(2)
        
        # Wait for login
        print("⏳ Waiting for login...")
        print(f"   Please log in to WordPress admin (waiting {wait_for_login} seconds)")
        print("   The tool will continue automatically after login")
        
        # Wait for dashboard
        try:
            WebDriverWait(driver, wait_for_login).until(
                lambda d: "wp-admin" in d.current_url and 
                         ("dashboard" in d.current_url.lower() or 
                          "customize" in d.current_url.lower())
            )
            print("✅ Logged in successfully!")
        except TimeoutException:
            print("❌ Login timeout - please try again")
            return False
        
        # Navigate to Customizer
        print("📝 Navigating to Customizer...")
        driver.get(customizer_url)
        time.sleep(3)
        
        # Wait for Customizer to load
        print("⏳ Waiting for Customizer to load...")
        try:
            # Wait for Additional CSS panel to be available
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#customize-controls"))
            )
            print("✅ Customizer loaded")
        except TimeoutException:
            print("❌ Customizer failed to load")
            return False
        
        # Find and click Additional CSS
        print("🔍 Looking for Additional CSS panel...")
        try:
            # Try to find Additional CSS link/button
            # WordPress Customizer structure varies, try multiple selectors
            css_selectors = [
                "a[href*='custom_css']",
                "li[id*='custom_css'] a",
                "li:contains('Additional CSS')",
                "button:contains('Additional CSS')",
                ".control-section-custom_css",
            ]
            
            css_panel_found = False
            for selector in css_selectors:
                try:
                    if "contains" in selector:
                        # Use XPath for text contains
                        element = driver.find_element(By.XPATH, f"//*[contains(text(), 'Additional CSS')]")
                    else:
                        element = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # Scroll into view and click
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(1)
                    element.click()
                    css_panel_found = True
                    print("✅ Found Additional CSS panel")
                    break
                except NoSuchElementException:
                    continue
            
            if not css_panel_found:
                # Try clicking on the panel directly by searching for text
                print("   Trying alternative method...")
                try:
                    # Look for any element containing "Additional CSS" text
                    elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Additional CSS')]")
                    if elements:
                        driver.execute_script("arguments[0].scrollIntoView(true);", elements[0])
                        time.sleep(1)
                        elements[0].click()
                        css_panel_found = True
                        print("✅ Found Additional CSS panel (alternative method)")
                except:
                    pass
            
            if not css_panel_found:
                print("⚠️  Could not find Additional CSS panel automatically")
                print("   Please manually click 'Additional CSS' in the left sidebar")
                print("   Then press Enter to continue...")
                input()
            
            time.sleep(2)
            
            # Find the CSS textarea
            print("🔍 Looking for CSS textarea...")
            textarea_selectors = [
                "textarea#custom_css",
                "textarea[name='custom_css']",
                "textarea.wp-custom-css",
                "#customize-control-custom_css textarea",
                "textarea",
            ]
            
            textarea = None
            for selector in textarea_selectors:
                try:
                    textarea = driver.find_element(By.CSS_SELECTOR, selector)
                    if textarea.is_displayed():
                        print(f"✅ Found CSS textarea using: {selector}")
                        break
                except NoSuchElementException:
                    continue
            
            if not textarea:
                print("❌ Could not find CSS textarea")
                print("   Please manually add CSS to Additional CSS section")
                return False
            
            # Scroll textarea into view
            driver.execute_script("arguments[0].scrollIntoView(true);", textarea)
            time.sleep(1)
            
            # Clear existing content and add new CSS
            print("📝 Adding CSS content...")
            textarea.click()
            time.sleep(0.5)
            
            # Select all and replace
            textarea.send_keys(Keys.CONTROL + "a")
            time.sleep(0.5)
            textarea.send_keys(Keys.DELETE)
            time.sleep(0.5)
            
            # Type CSS content
            textarea.send_keys(css_content)
            time.sleep(1)
            
            print("✅ CSS content added")
            
            # Find and click Publish button
            print("🔍 Looking for Publish button...")
            publish_selectors = [
                "button#save",
                "button.save",
                "#customize-save-button-wrapper button",
                "button:contains('Publish')",
            ]
            
            publish_button = None
            for selector in publish_selectors:
                try:
                    if "contains" in selector:
                        publish_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Publish')]")
                    else:
                        publish_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if publish_button.is_displayed():
                        print(f"✅ Found Publish button using: {selector}")
                        break
                except NoSuchElementException:
                    continue
            
            if publish_button:
                driver.execute_script("arguments[0].scrollIntoView(true);", publish_button)
                time.sleep(1)
                publish_button.click()
                print("✅ Clicked Publish button")
                time.sleep(2)
                
                # Wait for success message
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".notice-success, .customize-saved"))
                    )
                    print("✅ CSS published successfully!")
                except TimeoutException:
                    print("⚠️  Published (but no success message detected)")
            else:
                print("⚠️  Could not find Publish button automatically")
                print("   Please manually click 'Publish' button")
                print("   Then press Enter to continue...")
                input()
            
            print()
            print("=" * 60)
            print("✅ DEPLOYMENT COMPLETE")
            print("=" * 60)
            print(f"CSS has been added to WordPress Customizer > Additional CSS")
            print(f"Site: {site_url}")
            print()
            print("💡 The CSS will now apply to all blog posts site-wide")
            print()
            
            # Keep browser open for a few seconds to verify
            print("Keeping browser open for 5 seconds for verification...")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"❌ Error during deployment: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    finally:
        print("🔒 Closing browser...")
        driver.quit()


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Deploy CSS to WordPress Customizer Additional CSS"
    )
    parser.add_argument(
        "--site",
        type=str,
        default="dadudekc.com",
        help="Site name from config (default: dadudekc.com)"
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=120,
        help="Seconds to wait for login (default: 120)"
    )
    
    args = parser.parse_args()
    
    # Load config
    config = load_blogging_config()
    
    site_key = args.site
    if site_key not in config:
        print(f"❌ {site_key} not found in blogging config")
        return 1
    
    site_config = config[site_key]
    site_url = site_config["site_url"]
    
    # Load CSS fix
    css_fix = load_css_fix()
    if not css_fix:
        print("❌ Could not load CSS fix file")
        return 1
    
    # Deploy CSS
    success = deploy_css_to_customizer(site_url, css_fix, args.wait)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())





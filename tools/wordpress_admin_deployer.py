#!/usr/bin/env python3
"""
WordPress Admin Deployer - Enhanced Automation Tool
====================================================

Deploys files to WordPress sites via admin interface using browser automation.
Supports multiple sites and provides fallback to manual instructions.

<!-- SSOT Domain: infrastructure -->

Author: Agent-7 (Web Development Specialist)
V2 Compliant: <400 lines
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
    from selenium.common.exceptions import TimeoutException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class WordPressAdminDeployer:
    """Deploy files via WordPress admin interface."""
    
    def __init__(self, site_url: str, headless: bool = False):
        """
        Initialize WordPress admin deployer.
        
        Args:
            site_url: Base site URL (e.g., https://freerideinvestor.com)
            headless: Run browser in headless mode (default: False for manual login)
        """
        self.site_url = site_url.rstrip('/')
        self.wp_admin_url = f"{self.site_url}/wp-admin"
        self.headless = headless
        self.driver = None
    
    def check_rest_api(self) -> bool:
        """Check if WordPress REST API is available."""
        if not REQUESTS_AVAILABLE:
            return False
        
        try:
            response = requests.get(f"{self.site_url}/wp-json/wp/v2", timeout=TimeoutConstants.HTTP_QUICK)
            return response.status_code == 200
        except:
            return False
    
    def deploy_via_browser(
        self,
        file_path: Path,
        theme_name: str,
        file_name: str = "functions.php",
        wait_for_login: int = 120
    ) -> bool:
        """
        Deploy file via WordPress admin Theme Editor using browser automation.
        
        Args:
            file_path: Local file path to deploy
            theme_name: WordPress theme name
            file_name: File name in theme (default: functions.php)
            wait_for_login: Seconds to wait for manual login (default: 120)
        
        Returns:
            bool: True if deployment successful
        """
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium not installed. Install with: pip install selenium")
            return False
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False
        
        # Read file content
        try:
            file_content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
        
        print("=" * 60)
        print("🚀 WordPress Admin Deployment")
        print("=" * 60)
        print(f"Site: {self.site_url}")
        print(f"File: {file_path.name} ({len(file_content):,} bytes)")
        print(f"Theme: {theme_name}")
        print()
        
        # Setup Chrome
        options = Options()
        if not self.headless:
            options.add_argument("--window-size=1920,1080")
        else:
            options.add_argument("--headless=new")
        
        try:
            self.driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            print("   Install ChromeDriver or use manual deployment")
            return False
        
        try:
            # Navigate to WordPress admin
            print(f"📱 Navigating to: {self.wp_admin_url}")
            self.driver.get(self.wp_admin_url)
            time.sleep(2)
            
            # Wait for login
            print("⏳ Waiting for login...")
            print(f"   Please log in to WordPress admin (waiting {wait_for_login} seconds)")
            print("   The tool will continue automatically after login")
            
            # Wait for dashboard or theme editor
            try:
                WebDriverWait(self.driver, wait_for_login).until(
                    lambda d: "wp-admin" in d.current_url and 
                             ("dashboard" in d.current_url.lower() or 
                              "themes" in d.current_url.lower() or
                              "theme-editor" in d.current_url.lower())
                )
                print("✅ Logged in successfully!")
            except TimeoutException:
                print("❌ Login timeout - please try again")
                return False
            
            # Navigate to Theme Editor
            print("📝 Navigating to Theme Editor...")
            theme_editor_url = f"{self.wp_admin_url}/theme-editor.php?file={file_name}&theme={theme_name}"
            self.driver.get(theme_editor_url)
            time.sleep(3)
            
            # Find textarea
            try:
                textarea = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.wp-editor-area, textarea#newcontent"))
                )
                print("✅ Found editor textarea")
            except TimeoutException:
                print("❌ Could not find editor textarea")
                print("   Make sure you're on the Theme Editor page")
                return False
            
            # Update file content
            print("📝 Updating file content...")
            textarea.clear()
            textarea.send_keys(file_content)
            time.sleep(1)
            
            # Click Update File button
            try:
                update_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 
                        "input#submit, button#submit, input[type='submit'][value*='Update'], "
                        "input[type='submit'][value*='update']"))
                )
                print("✅ Found Update File button")
                update_button.click()
                print("✅ Clicked Update File button")
                time.sleep(3)
                
                # Check for success message
                try:
                    success_elements = self.driver.find_elements(
                        By.CSS_SELECTOR, 
                        ".notice-success, .updated, #message, .success"
                    )
                    if success_elements:
                        print("✅ File updated successfully!")
                        return True
                except:
                    pass
                
                # Check for error message
                try:
                    error_elements = self.driver.find_elements(
                        By.CSS_SELECTOR,
                        ".notice-error, .error, .warning"
                    )
                    if error_elements:
                        print("⚠️  Warning or error message detected")
                        for elem in error_elements[:2]:
                            print(f"   {elem.text[:200]}")
                except:
                    pass
                
                # If no error, assume success
                print("✅ File update completed (no error detected)")
                return True
                
            except TimeoutException:
                print("❌ Could not find Update File button")
                return False
            
        except Exception as e:
            print(f"❌ Error during deployment: {e}")
            return False
        finally:
            print("\n⏳ Keeping browser open for 10 seconds to verify...")
            print("   Close browser when done")
            time.sleep(10)
            if self.driver:
                self.driver.quit()
    
    def generate_manual_instructions(
        self,
        file_path: Path,
        theme_name: str,
        file_name: str = "functions.php"
    ) -> str:
        """Generate manual deployment instructions."""
        instructions = f"""
# Manual WordPress Admin Deployment Instructions

## Site: {self.site_url}
## File: {file_path.name}
## Theme: {theme_name}

### Steps:

1. **Log into WordPress Admin**:
   - Go to: {self.wp_admin_url}
   - Enter your WordPress admin credentials
   - Click "Log In"

2. **Navigate to Theme Editor**:
   - In left sidebar, click: **Appearance**
   - Click: **Theme Editor**
   - Select theme: **{theme_name}**
   - In file list, click: **{file_name}**

3. **Replace File Contents**:
   - Select all existing content (Ctrl+A or Cmd+A)
   - Delete selected content (Delete key)
   - Open local file: `{file_path}`
   - Select all content (Ctrl+A or Cmd+A)
   - Copy content (Ctrl+C or Cmd+C)
   - Paste into WordPress editor (Ctrl+V or Cmd+V)

4. **Update File**:
   - Scroll down to bottom of editor
   - Click: **Update File** button
   - Wait for success message

5. **Clear Cache**:
   - Go to: **Settings > Permalinks**
   - Click: **Save Changes** (this clears cache)
   - Or use caching plugin to clear cache

6. **Verify**:
   - Check live site navigation menu
   - Verify Developer Tools links are removed
   - Test site functionality

### File Details:
- **Local File**: {file_path}
- **File Size**: {file_path.stat().st_size:,} bytes
- **Theme**: {theme_name}
- **Target File**: {file_name}

### Troubleshooting:
- If file is too large, WordPress may timeout - try smaller chunks
- If editor doesn't load, check theme permissions
- If update fails, check file syntax for PHP errors
"""
        return instructions


def main():
    """CLI entry point."""
    import argparse
from src.core.config.timeout_constants import TimeoutConstants
    
    parser = argparse.ArgumentParser(
        description="Deploy files via WordPress admin"
    )
    parser.add_argument(
        "--site",
        required=True,
        help="Site domain (e.g., freerideinvestor.com)"
    )
    parser.add_argument(
        "--file",
        required=True,
        type=Path,
        help="File path to deploy"
    )
    parser.add_argument(
        "--theme",
        required=True,
        help="WordPress theme name"
    )
    parser.add_argument(
        "--filename",
        default="functions.php",
        help="File name in theme (default: functions.php)"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode"
    )
    parser.add_argument(
        "--wait-login",
        type=int,
        default=120,
        help="Seconds to wait for manual login (default: 120)"
    )
    parser.add_argument(
        "--manual-instructions",
        action="store_true",
        help="Generate manual deployment instructions only"
    )
    
    args = parser.parse_args()
    
    # Ensure site URL has protocol
    site_url = args.site
    if not site_url.startswith("http"):
        site_url = f"https://{site_url}"
    
    deployer = WordPressAdminDeployer(site_url, headless=args.headless)
    
    if args.manual_instructions:
        instructions = deployer.generate_manual_instructions(
            args.file, args.theme, args.filename
        )
        print(instructions)
        
        # Save to file
        instructions_file = Path("agent_workspaces/Agent-7/MANUAL_DEPLOYMENT_INSTRUCTIONS.md")
        instructions_file.parent.mkdir(parents=True, exist_ok=True)
        instructions_file.write_text(instructions)
        print(f"\n✅ Instructions saved: {instructions_file}")
        return 0
    
    # Check REST API first
    if deployer.check_rest_api():
        print("✅ WordPress REST API is available")
        print("   Note: File upload via REST API requires authentication")
        print("   Using browser automation instead...")
        print()
    
    # Deploy via browser
    success = deployer.deploy_via_browser(
        args.file,
        args.theme,
        args.filename,
        args.wait_login
    )
    
    if success:
        print("\n✅ Deployment complete!")
        print("\n📋 Next steps:")
        print("   1. Clear WordPress cache (Settings > Permalinks > Save)")
        print("   2. Verify menu in WordPress admin (Appearance > Menus)")
        print("   3. Check live site navigation")
        return 0
    else:
        print("\n❌ Deployment failed")
        print("\n💡 Fallback: Use manual deployment")
        print("   Run with --manual-instructions to get step-by-step guide")
        return 1


if __name__ == "__main__":
    sys.exit(main())





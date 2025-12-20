#!/usr/bin/env python3
"""
Add CSS to WordPress Theme Custom CSS
=====================================

Adds CSS to WordPress theme's Additional CSS section via REST API.
This is better than embedding CSS in posts as it applies site-wide.

Author: Agent-7 (Web Development Specialist)
Date: 2025-12-13
V2 Compliant: Yes
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    import requests
    from requests.auth import HTTPBasicAuth
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("❌ requests library not available")
    sys.exit(1)

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_DEFAULT = 30


def load_blogging_config() -> Dict[str, Any]:
    """Load blogging API configuration."""
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


def get_custom_css(site_url: str, username: str, app_password: str) -> Optional[str]:
    """Get current custom CSS from WordPress."""
    # WordPress stores custom CSS in theme mods
    # We need to use the Customizer API or theme mods endpoint
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/settings"
    auth = HTTPBasicAuth(username, app_password)
    
    try:
        response = requests.get(
            api_url,
            auth=auth,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )
        
        if response.status_code == 200:
            # Custom CSS is stored in theme mods, not settings
            # We'll need to use a different approach
            return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return None


def add_css_via_post_meta(site_url: str, username: str, app_password: str, css_content: str) -> bool:
    """Add CSS by creating a custom post type or using post meta."""
    # Alternative: Create a custom CSS post or use options API
    # For now, we'll inject CSS via a custom HTML block in a page
    
    # Actually, the best way is to use WordPress's wp.customize API
    # But that requires browser automation. Let's try a different approach:
    # Create a custom CSS file and reference it, or use a plugin approach
    
    # WordPress doesn't have a direct REST API for Additional CSS
    # We need to either:
    # 1. Use a plugin that exposes an API
    # 2. Use wp-cli if available
    # 3. Directly modify theme files (requires FTP)
    # 4. Use browser automation to access Customizer
    
    print("⚠️  WordPress REST API doesn't directly support Additional CSS")
    print("   We need to use browser automation or wp-cli")
    return False


def add_css_via_theme_mod(site_url: str, username: str, app_password: str, css_content: str) -> bool:
    """Try to add CSS via theme modifications endpoint."""
    # WordPress theme mods endpoint
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/themes"
    auth = HTTPBasicAuth(username, app_password)
    
    # This won't work directly - WordPress doesn't expose custom CSS via REST API
    # We need a different approach
    
    print("⚠️  Direct REST API access to Additional CSS is not available")
    print("   WordPress requires Customizer access for Additional CSS")
    return False


def inject_css_via_wp_head_hook(site_url: str, username: str, app_password: str, css_content: str) -> bool:
    """Inject CSS by creating a custom page that outputs CSS in wp_head."""
    # Create a hidden page that outputs CSS
    # This is a workaround since we can't access Additional CSS via REST API
    
    api_url = f"{site_url.rstrip('/')}/wp-json/wp/v2/pages"
    auth = HTTPBasicAuth(username, app_password)
    
    # Create a page with template that outputs CSS
    # Actually, better: create a custom CSS file and enqueue it
    
    print("💡 Alternative approach: Create custom CSS file and enqueue via functions.php")
    print("   Or use browser automation to access WordPress Customizer")
    return False


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Add CSS to WordPress theme Additional CSS"
    )
    parser.add_argument(
        "--site",
        type=str,
        default="dadudekc.com",
        help="Site name from config (default: dadudekc.com)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("ADD CSS TO WORDPRESS THEME")
    print("=" * 60)
    print()
    print("⚠️  IMPORTANT: WordPress REST API doesn't support Additional CSS directly")
    print("   This tool will provide instructions for manual addition")
    print()
    
    # Load config
    config = load_blogging_config()
    
    site_key = args.site
    if site_key not in config:
        print(f"❌ {site_key} not found in blogging config")
        return 1
    
    site_config = config[site_key]
    site_url = site_config["site_url"]
    username = site_config["username"]
    
    # Load CSS fix
    css_fix = load_css_fix()
    if not css_fix:
        print("❌ Could not load CSS fix file")
        return 1
    
    print(f"🔍 Site: {site_url}")
    print(f"   Username: {username}")
    print()
    print("=" * 60)
    print("MANUAL DEPLOYMENT INSTRUCTIONS")
    print("=" * 60)
    print()
    print("Since WordPress REST API doesn't support Additional CSS directly,")
    print("please add the CSS manually via WordPress Customizer:")
    print()
    print("1. Log into WordPress Admin:")
    print(f"   {site_url}/wp-admin")
    print()
    print("2. Go to Appearance > Customize")
    print()
    print("3. Click on 'Additional CSS' in the left sidebar")
    print()
    print("4. Copy and paste the following CSS:")
    print()
    print("-" * 60)
    print(css_fix)
    print("-" * 60)
    print()
    print("5. Click 'Publish' to save")
    print()
    print("=" * 60)
    print("ALTERNATIVE: Browser Automation")
    print("=" * 60)
    print()
    print("We can use browser automation to add CSS automatically.")
    print("Would you like me to create a browser automation script?")
    print()
    
    # Save CSS to a file for easy copy-paste
    output_file = project_root / "docs" / "CSS_FOR_WORDPRESS_COPY_PASTE.txt"
    output_file.write_text(css_fix, encoding='utf-8')
    print(f"💾 CSS saved to: {output_file}")
    print("   You can copy from this file and paste into WordPress Customizer")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())





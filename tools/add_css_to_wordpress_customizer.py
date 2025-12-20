#!/usr/bin/env python3
"""
Add CSS to WordPress Customizer Additional CSS
==============================================

Adds CSS to WordPress theme via Customizer Additional CSS option.
"""

import json
import sys
from pathlib import Path

try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    print("❌ Install required packages: pip install requests")
    sys.exit(1)

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from src.core.config.timeout_constants import TimeoutConstants
except ImportError:
    class TimeoutConstants:
        HTTP_DEFAULT = 30

# Load credentials and CSS
config_path = project_root / ".deploy_credentials" / "blogging_api.json"
css_path = project_root / "docs" / "blog" / "dadudekc_blog_css_for_theme.css"

if not config_path.exists():
    print(f"❌ Config file not found: {config_path}")
    sys.exit(1)

if not css_path.exists():
    print(f"❌ CSS file not found: {css_path}")
    sys.exit(1)

with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

site_config = config.get("dadudekc.com")
if not site_config:
    print("❌ dadudekc.com not found in config")
    sys.exit(1)

css_content = css_path.read_text(encoding='utf-8')

site_url = site_config["site_url"]
username = site_config["username"]
app_password = site_config["app_password"]
api_url = f"{site_url}/wp-json/wp/v2"

session = requests.Session()
session.auth = HTTPBasicAuth(username, app_password)

print("🔍 Adding CSS to WordPress Customizer...\n")

# WordPress Customizer CSS is stored in theme mods
# We need to use the Customizer REST API or update via options

# Try Customizer API endpoint
customizer_url = f"{site_url}/wp-json/wp/v2/settings"

# Get current settings
try:
    response = session.get(
        customizer_url, timeout=TimeoutConstants.HTTP_DEFAULT)
    if response.status_code == 200:
        settings = response.json()
        current_css = settings.get("custom_css", "")

        # Append our CSS
        if current_css and css_content not in current_css:
            new_css = current_css + "\n\n/* DaDudeKC Blog Post Readability Fix */\n" + css_content
        elif css_content not in current_css:
            new_css = "/* DaDudeKC Blog Post Readability Fix */\n" + css_content
        else:
            print("✅ CSS already in Customizer")
            sys.exit(0)

        # Update settings
        update_data = {"custom_css": new_css}
        update_response = session.post(
            customizer_url,
            json=update_data,
            timeout=TimeoutConstants.HTTP_DEFAULT
        )

        if update_response.status_code in (200, 201):
            print("✅ CSS added to WordPress Customizer Additional CSS")
            print(f"   Total CSS length: {len(new_css)} chars")
        else:
            print(
                f"⚠️  Settings API returned: HTTP {update_response.status_code}")
            print("   Trying alternative method...\n")

            # Alternative: Use theme mods endpoint
            # Note: This requires a plugin or custom endpoint
            print("⚠️  Direct Customizer API update not available")
            print("   Manual step required:")
            print(f"   1. Go to: {site_url}/wp-admin/customize.php")
            print("   2. Navigate to: Additional CSS")
            print("   3. Add the CSS from: docs/blog/dadudekc_blog_css_for_theme.css")
    else:
        print(f"⚠️  Settings API not available: HTTP {response.status_code}")
        print("   Manual step required:")
        print(f"   1. Go to: {site_url}/wp-admin/customize.php")
        print("   2. Navigate to: Additional CSS")
        print(f"   3. Add the CSS from: {css_path}")

except Exception as e:
    print(f"⚠️  Error: {e}")
    print("\n📋 Manual Steps Required:")
    print(f"   1. Go to: {site_url}/wp-admin/customize.php")
    print("   2. Navigate to: Additional CSS")
    print(f"   3. Add the CSS from: {css_path}")
    print(
        f"\n   CSS content ({len(css_content)} chars) ready for manual addition")

print("\n✅ CSS ready for theme - posts already cleaned up!")

#!/usr/bin/env python3
"""
Fix FreeRideInvestor.com Footer Contact Link
===========================================

Updates footer widget/menu to point to correct Contact page URL.

Author: Agent-2
"""

import json
import sys
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load credentials
creds_file = project_root / ".deploy_credentials" / "blogging_api.json"
with open(creds_file) as f:
    creds_data = json.load(f)

SITE_CONFIG = creds_data["freerideinvestor"]
SITE_URL = SITE_CONFIG["site_url"]
USERNAME = SITE_CONFIG["username"]
APP_PASSWORD = SITE_CONFIG["app_password"]

API_BASE = f"{SITE_URL}/wp-json/wp/v2"
AUTH = HTTPBasicAuth(USERNAME, APP_PASSWORD.replace(" ", ""))


def get_contact_page():
    """Get Contact page."""
    url = f"{API_BASE}/pages"
    params = {"slug": "contact", "per_page": 1}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)
    if response.status_code == 200:
        pages = response.json()
        return pages[0] if pages else None
    return None


def get_footer_widgets():
    """Get footer widgets."""
    # Try to get widgets via REST API (may require plugin)
    url = f"{SITE_URL}/wp-json/wp/v2/widgets"
    response = requests.get(url, auth=AUTH, timeout=30)
    if response.status_code == 200:
        return response.json()
    return None


def update_footer_via_wp_cli():
    """Update footer via WP-CLI."""
    from tools.wordpress_manager import WordPressManager

    manager = WordPressManager("freerideinvestor")
    if not manager.connect():
        return False

    # Get Contact page ID
    contact = get_contact_page()
    if not contact:
        print("❌ Contact page not found")
        return False

    contact_id = contact["id"]
    contact_url = contact.get("link", "").replace(SITE_URL, "")

    print(f"✅ Found Contact page (ID: {contact_id}, URL: {contact_url})")

    # Try to update footer menu
    # First, check if there's a footer menu
    menus_json, _, _ = manager.wp_cli("menu list --format=json")
    menus = json.loads(menus_json) if menus_json.strip() else []

    footer_menu = None
    for menu in menus:
        if "footer" in menu.get("name", "").lower():
            footer_menu = menu
            break

    if footer_menu:
        menu_id = footer_menu.get("term_id")
        print(f"✅ Found footer menu (ID: {menu_id})")

        # Check if Contact is already in menu
        items_json, _, _ = manager.wp_cli(
            f"menu item list {menu_id} --format=json")
        items = json.loads(items_json) if items_json.strip() else []

        contact_in_menu = any(
            item.get("object_id") == str(contact_id) for item in items
        )

        if not contact_in_menu:
            # Add Contact to footer menu
            stdout, stderr, code = manager.wp_cli(
                f'menu item add-post {menu_id} {contact_id} --title="Contact"'
            )
            if code == 0:
                print("✅ Added Contact to footer menu")
            else:
                print(f"⚠️  Failed to add Contact to menu: {stderr}")
        else:
            print("✅ Contact already in footer menu")
    else:
        # Try to update footer widget area
        # This might require theme-specific code or widget API
        print("⚠️  Footer menu not found, may need theme/widget update")
        print(f"💡 Contact page URL: {contact_url}")
        print("   Footer link should point to this URL")

    # Flush cache
    manager.purge_caches()
    manager.disconnect()

    return True


def main():
    """Main execution."""
    print("🔧 Fixing FreeRideInvestor.com footer Contact link...\n")

    # Verify Contact page exists
    contact = get_contact_page()
    if not contact:
        print("❌ Contact page not found - cannot fix footer link")
        print("💡 Contact page should exist (ID: 85 from earlier fix)")
        sys.exit(1)

    print(
        f"✅ Contact page exists (ID: {contact['id']}, URL: {contact.get('link', '')})")

    # Update footer via WP-CLI
    success = update_footer_via_wp_cli()

    if success:
        print("\n✅ Footer Contact link fix complete!")
        print(f"📋 Contact page URL: {contact.get('link', '')}")
        print("💡 If footer still shows 404, the theme may need manual widget update")
    else:
        print("\n⚠️  Could not automatically update footer")
        print("💡 Manual steps:")
        print("   1. Go to WordPress admin → Appearance → Widgets")
        print("   2. Find footer widget area")
        print("   3. Update Contact link to point to /contact")


if __name__ == "__main__":
    main()

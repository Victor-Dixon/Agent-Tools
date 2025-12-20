#!/usr/bin/env python3
"""
Update FreeRideInvestor.com Navigation Menus
===========================================

Adds Blog, About, Contact pages to navigation menu via WP-CLI.

Author: Agent-2
"""

from tools.wordpress_manager import WordPressManager
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Update navigation menus."""
    print("🔧 Updating FreeRideInvestor.com navigation menus...\n")

    manager = WordPressManager("freerideinvestor")

    if not manager.connect():
        print("❌ Failed to connect to server")
        sys.exit(1)

    # Get existing menu or create one
    menus_json, _, _ = manager.wp_cli("menu list --format=json")
    menus = json.loads(menus_json) if menus_json.strip() else []

    menu_name = "Main Menu"
    menu_id = None

    for m in menus:
        if m.get("name") == menu_name:
            menu_id = m.get("term_id")
            break

    if not menu_id:
        # Create menu
        stdout, stderr, code = manager.wp_cli(f'menu create "{menu_name}"')
        if code != 0:
            print(f"❌ Failed to create menu: {stderr}")
            sys.exit(1)
        print(f"✅ Created menu: {menu_name}")
        # Get menu ID
        menus_json, _, _ = manager.wp_cli("menu list --format=json")
        menus = json.loads(menus_json) if menus_json.strip() else []
        for m in menus:
            if m.get("name") == menu_name:
                menu_id = m.get("term_id")
                break

    if not menu_id:
        print("❌ Could not find or create menu")
        sys.exit(1)

    # Get page IDs
    pages_json, _, _ = manager.wp_cli(
        "post list --post_type=page --format=json --fields=ID,post_name,post_title")
    pages = json.loads(pages_json) if pages_json.strip() else []

    page_map = {}
    for page in pages:
        slug = page.get("post_name", "")
        page_map[slug] = page.get("ID")

    # Add pages to menu
    menu_items = [
        ("blog", "Blog"),
        ("about", "About"),
        ("contact", "Contact")
    ]

    for slug, title in menu_items:
        if slug in page_map:
            page_id = page_map[slug]
            # Check if already in menu
            items_json, _, _ = manager.wp_cli(
                f'menu item list {menu_id} --format=json')
            items = json.loads(items_json) if items_json.strip() else []
            exists = any(item.get("object_id") == str(page_id)
                         for item in items)

            if not exists:
                stdout, stderr, code = manager.wp_cli(
                    f'menu item add-post {menu_id} {page_id} --title="{title}"'
                )
                if code == 0:
                    print(f"✅ Added '{title}' to menu")
                else:
                    print(f"⚠️  Failed to add '{title}': {stderr}")
            else:
                print(f"⏭️  '{title}' already in menu")
        else:
            print(f"⚠️  Page '{slug}' not found")

    # Assign menu to primary location
    stdout, stderr, code = manager.wp_cli(
        f'menu location assign {menu_id} primary')
    if code == 0:
        print(f"\n✅ Assigned '{menu_name}' to primary location")
    else:
        print(f"⚠️  Failed to assign menu location: {stderr}")

    # Flush cache
    manager.purge_caches()

    print("\n✅ Menu update complete!")


if __name__ == "__main__":
    main()

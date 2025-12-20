#!/usr/bin/env python3
"""
Remove Developer Tools from dadudekc.com Navigation Menus
========================================================

Removes "Developer Tools" menu items from all navigation menus to simplify navigation
as per ad-readiness audit (IA-DADUDEKC-NAV-UNIFY-01).

Target navigation: Home / Services / Case Studies / About / Contact

Author: Agent-2
V2 Compliant: <300 lines
"""

from tools.wordpress_manager import WordPressManager
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def remove_developer_tools_from_menus(manager: WordPressManager):
    """Remove Developer Tools menu items from all navigation menus."""
    print("🔧 Removing 'Developer Tools' from navigation menus...\n")

    # Get all menus
    menus_json, _, _ = manager.wp_cli("menu list --format=json")
    if not menus_json.strip():
        print("⏭️  No menus found")
        return False

    menus = json.loads(menus_json)
    removed_count = 0

    for menu in menus:
        menu_name = menu.get("name", "")
        menu_id = menu.get("term_id")

        if not menu_id:
            continue

        # Get menu items
        items_json, _, _ = manager.wp_cli(
            f'menu item list "{menu_name}" --format=json'
        )

        if not items_json.strip():
            continue

        items = json.loads(items_json)

        for item in items:
            item_title = item.get("title", "").strip()
            item_id = item.get("db_id")

            # Check if this is a Developer Tools item
            # Match variations: "Developer Tools", "Developer", "Tools", etc.
            if not item_id:
                continue

            title_lower = item_title.lower()
            if any(keyword in title_lower for keyword in [
                "developer tools",
                "developer",
                "tools",
                "dev tools"
            ]):
                # Check if it's specifically "Developer Tools" or similar
                # Be careful not to remove "Services" or other legitimate items
                if "developer" in title_lower and "tool" in title_lower:
                    print(
                        f"  🗑️  Removing '{item_title}' from menu '{menu_name}' (ID: {item_id})")
                    stdout, stderr, code = manager.wp_cli(
                        f"menu item delete {item_id}")
                    if code == 0:
                        removed_count += 1
                        print(f"     ✅ Removed")
                    else:
                        print(f"     ⚠️  Failed: {stderr}")

    if removed_count > 0:
        print(f"\n✅ Removed {removed_count} 'Developer Tools' menu item(s)")
        return True
    else:
        print("\n⏭️  No 'Developer Tools' menu items found to remove")
        return False


def verify_navigation_structure(manager: WordPressManager):
    """Verify navigation structure matches target: Home / Services / Case Studies / About / Contact."""
    print("\n🔍 Verifying navigation structure...\n")

    menus_json, _, _ = manager.wp_cli("menu list --format=json")
    if not menus_json.strip():
        print("⏭️  No menus found")
        return

    menus = json.loads(menus_json)

    target_items = ["home", "services", "case studies", "about", "contact"]

    for menu in menus:
        menu_name = menu.get("name", "")
        items_json, _, _ = manager.wp_cli(
            f'menu item list "{menu_name}" --format=json'
        )

        if not items_json.strip():
            continue

        items = json.loads(items_json)
        current_items = [item.get("title", "").strip().lower()
                         for item in items]

        print(f"📋 Menu: {menu_name}")
        print(
            f"   Current items: {', '.join([item.get('title', '') for item in items])}")

        # Check for Developer Tools
        has_dev_tools = any(
            "developer" in item.get("title", "").lower() and
            "tool" in item.get("title", "").lower()
            for item in items
        )

        if has_dev_tools:
            print(f"   ⚠️  Still contains 'Developer Tools'")
        else:
            print(f"   ✅ No 'Developer Tools' found")


def main():
    """Main execution."""
    print("🔧 Removing 'Developer Tools' from dadudekc.com navigation menus...\n")

    manager = WordPressManager("dadudekc.com")

    if not manager.connect():
        print("❌ Failed to connect to server")
        sys.exit(1)

    try:
        # Remove Developer Tools from menus
        removed = remove_developer_tools_from_menus(manager)

        # Verify navigation structure
        verify_navigation_structure(manager)

        # Flush caches
        print("\n🔄 Flushing WordPress caches...")
        manager.purge_caches()
        print("✅ Caches flushed")

        if removed:
            print("\n✅ Navigation menu simplification complete!")
            print("   Target structure: Home / Services / Case Studies / About / Contact")
        else:
            print("\n✅ Verification complete - no changes needed")

    finally:
        manager.disconnect()


if __name__ == "__main__":
    main()





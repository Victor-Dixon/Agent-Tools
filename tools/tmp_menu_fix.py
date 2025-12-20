#!/usr/bin/env python3
"""
Temporary helper to create/assign a minimal primary menu for freerideinvestor.
Removes auto-generated page list (Developer Tools clutter) by assigning a clean menu.
"""

from tools.wordpress_manager import WordPressManager
import json
import sys


def main():
    mgr = WordPressManager("freerideinvestor")
    cred = mgr.credentials or {}
    cred["port"] = 65002
    cred["username"] = "u996867598"
    cred["wp_cli_path"] = "php /usr/local/bin/wp-cli-2.12.0.phar"
    mgr.credentials = cred
    mgr.credentials["remote_path"] = (
        "/home/u996867598/domains/freerideinvestor.com/public_html"
    )

    if not mgr.connect():
        sys.exit("connect failed")

    menu_name = "Main"

    menus_json, _, _ = mgr.wp_cli("menu list --format=json")
    menus = json.loads(menus_json) if menus_json.strip() else []
    menu_id = None
    for m in menus:
        if m.get("name") == menu_name:
            menu_id = m.get("term_id")
            break

    if not menu_id:
        mgr.wp_cli(f"menu create {menu_name}")
        menus_json, _, _ = mgr.wp_cli("menu list --format=json")
        menus = json.loads(menus_json) if menus_json.strip() else []
        for m in menus:
            if m.get("name") == menu_name:
                menu_id = m.get("term_id")
                break

    if menu_id:
        items_json, _, _ = mgr.wp_cli(f"menu item list {menu_name} --format=json")
        items = json.loads(items_json) if items_json.strip() else []
        if not items:
            mgr.wp_cli(
                f"menu item add-custom {menu_name} 'Home' https://freerideinvestor.com"
            )
        mgr.wp_cli(f"menu location assign {menu_name} primary")
        print("Assigned menu to primary with Home link")
    else:
        print("Menu id not found")

    mgr.disconnect()


if __name__ == "__main__":
    main()


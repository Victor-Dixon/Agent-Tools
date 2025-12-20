#!/usr/bin/env python3
"""
Temporary helper to remove Developer Tools pages, assign a clean primary menu,
and purge caches for freerideinvestor.com.
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

    # 1) Delete Developer Tools pages
    dev_page_ids = [
        35, 34, 33, 32, 31, 30, 29, 25, 24, 23, 19, 18, 17, 16, 15, 14, 13, 5
    ]
    for pid in dev_page_ids:
        mgr.wp_cli(f"post delete {pid} --force")

    # 2) Ensure a clean primary menu with at least Home
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

    # 3) Purge caches
    mgr.wp_cli("litespeed-purge all")
    mgr.wp_cli("cache flush")

    mgr.disconnect()


if __name__ == "__main__":
    main()


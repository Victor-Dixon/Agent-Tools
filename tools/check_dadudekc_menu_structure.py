#!/usr/bin/env python3
"""Check dadudekc.com menu structure."""

from tools.wordpress_manager import WordPressManager
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


mgr = WordPressManager("dadudekc.com")
mgr.connect()

menus_json, _, _ = mgr.wp_cli("menu list --format=json")
menus = json.loads(menus_json) if menus_json.strip() else []

print("Menus:")
for m in menus:
    print(f"  - {m.get('name')} (ID: {m.get('term_id')})")

for m in menus:
    menu_name = m.get("name")
    items_json, _, _ = mgr.wp_cli(
        f'menu item list "{menu_name}" --format=json')
    if items_json.strip():
        items = json.loads(items_json)
        print(f"\nItems in {menu_name}:")
        for item in items:
            print(
                f"    - {item.get('title')} (ID: {item.get('db_id')}, URL: {item.get('url', 'N/A')})")

mgr.disconnect()





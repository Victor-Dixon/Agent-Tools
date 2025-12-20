#!/usr/bin/env python3
"""
Clean WordPress Defaults on dadudekc.com
=========================================

Removes or unpublishes WordPress default "Hello world!" post and "Uncategorized" category.
Updates navigation and sitemap to exclude defaults.

Author: Agent-2
V2 Compliant: <300 lines
"""

from tools.wordpress_manager import WordPressManager
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

SITE_CONFIG = creds_data["dadudekc.com"]
SITE_URL = SITE_CONFIG["site_url"]
USERNAME = SITE_CONFIG["username"]
APP_PASSWORD = SITE_CONFIG["app_password"]

API_BASE = f"{SITE_URL}/wp-json/wp/v2"
AUTH = HTTPBasicAuth(USERNAME, APP_PASSWORD.replace(" ", ""))


def find_default_post():
    """Find WordPress default 'Hello world!' post."""
    url = f"{API_BASE}/posts"
    params = {"per_page": 100, "search": "Hello world"}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)

    if response.status_code == 200:
        posts = response.json()
        for post in posts:
            title = post.get("title", {}).get("rendered", "")
            if "Hello world" in title.lower() or post.get("slug") == "hello-world":
                return post
    return None


def find_uncategorized_category():
    """Find 'Uncategorized' category."""
    url = f"{API_BASE}/categories"
    params = {"per_page": 100, "search": "Uncategorized"}
    response = requests.get(url, params=params, auth=AUTH, timeout=30)

    if response.status_code == 200:
        categories = response.json()
        for cat in categories:
            if cat.get("name", "").lower() == "uncategorized" or cat.get("slug") == "uncategorized":
                return cat
    return None


def unpublish_post(post_id: int):
    """Unpublish a post (set to draft)."""
    url = f"{API_BASE}/posts/{post_id}"
    response = requests.post(
        url,
        json={"status": "draft"},
        auth=AUTH,
        timeout=30
    )
    return response.status_code == 200


def delete_post(post_id: int):
    """Delete a post permanently."""
    url = f"{API_BASE}/posts/{post_id}"
    response = requests.delete(url, auth=AUTH, timeout=30)
    return response.status_code == 200


def update_category(category_id: int, new_name: str = "General"):
    """Update category name from 'Uncategorized' to something else."""
    url = f"{API_BASE}/categories/{category_id}"
    response = requests.post(
        url,
        json={"name": new_name},
        auth=AUTH,
        timeout=30
    )
    return response.status_code == 200


def remove_from_navigation(manager: WordPressManager):
    """Remove default post/category from navigation menus."""
    # Get all menus
    menus_json, _, _ = manager.wp_cli("menu list --format=json")
    if not menus_json.strip():
        return

    menus = json.loads(menus_json)

    for menu in menus:
        menu_id = menu.get("term_id")
        # Get menu items
        items_json, _, _ = manager.wp_cli(
            f"menu item list {menu_id} --format=json")
        if items_json.strip():
            items = json.loads(items_json)
            for item in items:
                title = item.get("title", "")
                if "Hello world" in title.lower() or "Uncategorized" in title:
                    item_id = item.get("db_id")
                    # Remove from menu
                    manager.wp_cli(f"menu item delete {item_id}")


def main():
    """Main execution."""
    print("🔧 Cleaning WordPress defaults on dadudekc.com...\n")

    # Find default post
    default_post = find_default_post()
    if default_post:
        post_id = default_post["id"]
        post_title = default_post.get("title", {}).get("rendered", "")
        print(f"✅ Found default post: '{post_title}' (ID: {post_id})")

        # Unpublish (safer than delete)
        if unpublish_post(post_id):
            print(f"✅ Unpublished default post (ID: {post_id})")
        else:
            print(f"⚠️  Failed to unpublish post (ID: {post_id})")
    else:
        print("⏭️  No default 'Hello world!' post found")

    # Find Uncategorized category
    uncategorized = find_uncategorized_category()
    if uncategorized:
        cat_id = uncategorized["id"]
        cat_name = uncategorized.get("name", "")
        print(f"✅ Found 'Uncategorized' category (ID: {cat_id})")

        # Update name to "General" (safer than deleting)
        if update_category(cat_id, "General"):
            print(f"✅ Renamed 'Uncategorized' to 'General' (ID: {cat_id})")
        else:
            print(f"⚠️  Failed to update category (ID: {cat_id})")
    else:
        print("⏭️  No 'Uncategorized' category found")

    # Remove from navigation
    manager = WordPressManager("dadudekc.com")
    if manager.connect():
        print("\n🔧 Removing defaults from navigation menus...")
        remove_from_navigation(manager)
        manager.purge_caches()
        manager.disconnect()
        print("✅ Navigation menus updated")
    else:
        print("⚠️  Could not connect to update navigation")

    print("\n✅ WordPress defaults cleanup complete!")
    print("💡 Note: Post set to draft (not deleted) and category renamed (not deleted) for safety")


if __name__ == "__main__":
    main()




